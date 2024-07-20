import cherrypy

from cherrypy.process import plugins

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


def db(**kw):
    return scoped_session(sessionmaker(**kw))


class SQLAlchemyTool(cherrypy.Tool):
    def __init__(self, session_name, **kw):
        """
        The SA tool is responsible for associating a SA session
        to the SA engine and attaching it to the current request.
        Since we are running in a multithreaded application,
        we use the scoped_session that will create a session
        on a per thread basis so that you don't worry about
        concurrency on the session object itself.

        This tools binds a session to the engine each time
        a requests starts and commits/rollbacks whenever
        the request terminates.
        """
        cherrypy.Tool.__init__(self, "on_start_resource", self.bind_session, priority=20)

        self.session_name = session_name
        self.session = db(**kw)

    def _setup(self):
        cherrypy.Tool._setup(self)
        cherrypy.request.hooks.attach("on_end_resource", self.commit_transaction, priority=80)

    def bind_session(self):
        cherrypy.engine.publish(self.session_name + ".db.bind", self.session)

        if not hasattr(cherrypy.request, "databases"):
            cherrypy.request.databases = {}

        cherrypy.request.databases[self.session_name] = self.session

    def commit_transaction(self):
        cherrypy.request.databases[self.session_name] = None

        try:
            self.session.commit()
        except:
            self.session.rollback()
            raise
        finally:
            self.session.remove()

        self.session.close()


class SQLAlchemyPlugin(plugins.SimplePlugin):
    def __init__(self, name, bus, orm_base, dburi, after_engine_setup=None, **kw):
        """
        The plugin is registered to the CherryPy engine and therefore
        is part of the bus (the engine *is* a bus) registery.

        We use this plugin to create the SA engine. At the same time,
        when the plugin starts we create the tables into the database
        using the mapped class of the global metadata.

        Finally we create a new 'bind' channel that the SA tool
        will use to map a session to the SA engine at request time.
        """
        plugins.SimplePlugin.__init__(self, bus)
        self.name = name
        self.dburi = dburi
        self.orm_base = orm_base
        self.create_kwargs = kw
        self.after_engine_setup = after_engine_setup

        self.bus.subscribe(name + ".db.bind", self.bind)
        self.bus.subscribe(name + ".db.create", self.create)

        self.sa_engine = None

    def start(self):
        self.sa_engine = create_engine(self.dburi, **self.create_kwargs)

    def create(self):
        if not self.sa_engine:
            self.start()

        cherrypy.log("Creating tables: %s" % self.sa_engine)
        self.orm_base.metadata.bind = self.sa_engine
        self.orm_base.metadata.create_all(self.sa_engine)

        if self.after_engine_setup:
            session = scoped_session(sessionmaker())
            session.configure(bind=self.sa_engine)
            try:
                self.after_engine_setup(session)
                session.commit()
            except:
                session.rollback()
                raise
            finally:
                session.remove()

            session.close()

    def stop(self):
        if self.sa_engine:
            self.sa_engine.dispose()
            self.sa_engine = None

    def bind(self, session):
        session.remove()
        session.configure(bind=self.sa_engine)


""" Example usage of this plugin:

        // Setup step
        database_name = "test_database"

        cherrypy.tools.digital_deception_database = SQLAlchemyTool(database_name)

        SQLAlchemyPlugin(
            database_name,
            cherrypy.engine,
            Base,
            connection_string,
            echo=False,
            pool_recycle=20000,
            after_engine_setup=initialize_db,
        )
        cherrypy.log("Publishing db create")
        cherrypy.engine.publish("database_name.db.create")

        // Usage in a view function
        session = cherrypy.request.databases[database_name]

        session.add(entity)
        session.commit()
        session.flush()
        ... etc
"""
