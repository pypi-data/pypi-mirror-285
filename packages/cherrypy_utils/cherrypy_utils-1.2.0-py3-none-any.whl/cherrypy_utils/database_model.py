import cherrypy

from sqlalchemy.orm import scoped_session


class DatabaseModel(cherrypy.Tool):
    def __init__(self, model_name, database_name):
        cherrypy.Tool.__init__(self, "on_start_resource", self.initialize, priority=30)
        self.session: scoped_session = None
        self.model_name = model_name
        self.database_name = database_name

    def _setup(self):
        cherrypy.Tool._setup(self)
        cherrypy.request.hooks.attach("on_end_resource", self.on_session_ended, priority=70)

    def initialize(self):
        self.session = cherrypy.request.databases[self.database_name]

        if not hasattr(cherrypy.request, "models"):
            cherrypy.request.models = {}

        cherrypy.request.models[self.model_name] = self

        self.on_session_started()

    def get_session(self):
        return self.session

    def on_session_started(self):
        pass

    def on_session_ended(self):
        pass
