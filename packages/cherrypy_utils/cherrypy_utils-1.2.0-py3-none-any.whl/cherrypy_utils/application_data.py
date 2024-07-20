import cherrypy
import pathlib

from typing import Dict

from cherrypy_utils import url_utils
from cherrypy_utils import templating
from cherrypy_utils import authentication
from cherrypy_utils.login.models import authenticate_user, ldap_user_authenticated


class ApplicationData:
    def __init__(
        self,
        subdomain,
        shared_data_location,
        application_location,
        template_location,
        api_key_filepath,
        production=True,
    ):
        self.subdomain = subdomain
        self.shared_data_location = shared_data_location  # a directory on the filesystem where any dynamic, shared data that can change over time should be stored.
        self.application_location = application_location  # type: pathlib.Path
        self.api_key_filepath = api_key_filepath
        self.template_location = template_location
        self.production = production
        self.login_redirect_url = self.subdomain
        self.additional_data = {}

        self.template_engine = templating.create_environment(template_location=template_location)
        authentication.initialize(api_key_filepath=self.api_key_filepath)

    def template_domain(self):
        return self.subdomain if self.subdomain != "/" else ""

    def is_development_mode(self):
        return not self.is_production_mode()

    def is_production_mode(self):
        return self.production

    def user_is_authenticated(self):
        return ldap_user_authenticated()

    def authenticate_user(self, username, password):
        cherrypy.session["ldap_authenticated"] = 1

        if self.production:
            return authenticate_user(username, password)
        else:
            return True

    def set_login_redirect(self, *url_parts):
        self.login_redirect_url = url_utils.combine_url(self.subdomain, *url_parts)
        cherrypy.log("Setting login redirect url to {0}".format(self.login_redirect_url))


APPS = {}  #  type: Dict[str, ApplicationData]


def initialize(
    application_name,
    subdomain,
    shared_data_location,
    application_location,
    template_location,
    api_key_filepath,
    production=True,
):
    APPS[application_name] = ApplicationData(
        subdomain=subdomain,
        shared_data_location=shared_data_location,
        application_location=application_location,
        template_location=template_location,
        api_key_filepath=api_key_filepath,
        production=production,
    )
    return APPS[application_name]


def get_app(application_name: str) -> ApplicationData:
    return APPS[application_name]
