from setuptools import find_packages, setup

setup(
    name="cherrypy_utils",
    packages=find_packages(include=["cherrypy_utils", "cherrypy_utils.login"]),
    version="1.0.24",
    description="Collection of utility functions and modules for cherrypy web servers",
    author="Me",
    license="MIT",
    install_requires=[
        "cherrypy",
        "python-ldap",
        "requests",
        "python-dateutil",
        "sqlalchemy",
    ],
)
