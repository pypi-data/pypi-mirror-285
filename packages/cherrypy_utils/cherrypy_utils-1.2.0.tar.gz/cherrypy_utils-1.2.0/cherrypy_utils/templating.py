import cherrypy

from jinja2 import Environment, FileSystemLoader, select_autoescape


def create_environment(template_location):
    cherrypy.log("Loading jinja template engine using filesystem location: {0}".format(template_location))
    return Environment(
        loader=FileSystemLoader(template_location),
        autoescape=select_autoescape(["html", "xml"]),
    )
