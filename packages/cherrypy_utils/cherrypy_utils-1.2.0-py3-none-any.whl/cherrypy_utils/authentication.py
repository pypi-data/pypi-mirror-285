import os
import uuid
import cherrypy


API_KEY = ""


def initialize(api_key_filepath):
    """This needs to be called to setup the required API key properly!
    Should be called at the top/initialization
    """
    global API_KEY

    if not os.path.exists(api_key_filepath):
        with open(api_key_filepath, "w") as api_key_file:
            api_key_file.write(str(uuid.uuid4()))

    with open(api_key_filepath, "r") as api_key_file:
        API_KEY = api_key_file.read().rstrip("\n")

    cherrypy.log("Using API KEY {0} for authentication".format(API_KEY))


@cherrypy.tools.register("before_handler", name="require_api_key")
def check_authentication():
    """Cherrypy tool to handle authenticating requests against an API key in a file and the request header X-HTTP-APIKEY.
    In order to use this properly, you should configure it in cherrypy config files for specific endpoints by using:

        [/path/to/api/]
        tools.require_api_key.on = True

    Otherwise, you can use the cherrypy tool decorator on a view class like so:

        @cherrypy.expose
        @cherrypy.tools.require_api_key()
        class MyView(object):
            def GET(self):
                // Do something
                pass
    """
    provided_key = cherrypy.request.headers.get("X-HTTP-APIKEY", None)
    cherrypy.log("API Key Provided by user was {0}".format(provided_key))
    if not provided_key == API_KEY:
        cherrypy.log("Raising 401 error as API key does not match expected")
        raise cherrypy.HTTPError(status=401, message="API Key Invalid")
