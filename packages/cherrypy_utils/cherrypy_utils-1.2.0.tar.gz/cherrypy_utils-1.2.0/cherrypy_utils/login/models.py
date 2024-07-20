import cherrypy


def ldap_user_authenticated() -> bool:
    return cherrypy.session.get("ldap_authenticated", 0) == 1


def authenticate_user(username, password) -> bool:
    cherrypy.log("Enabled LDAP support and signing in via production mode")

    from cherrypy_utils.login import ldap_auth

    if ldap_auth and ldap_auth.ldap_login(username, password):
        cherrypy.session["ldap_authenticated"] = 1
        return True
    else:
        cherrypy.session["ldap_authenticated"] = 0
        return False
