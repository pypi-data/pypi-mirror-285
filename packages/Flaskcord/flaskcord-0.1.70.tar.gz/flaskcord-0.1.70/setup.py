'''
=====================
Flaskcord
=====================

.. image:: https://img.shields.io/pypi/v/flaskcord?style=for-the-badge
   :target: https://pypi.org/project/flaskcord/

.. image:: https://img.shields.io/readthedocs/flaskcord?style=for-the-badge
   :target: https://flaskcord.readthedocs.io/en/latest/

.. image:: https://img.shields.io/discord/1258233857358958633?label=Vinny%20Support%20Server&logo=Discord&style=for-the-badge
   :target: https://discord.gg/FgyJJV24XF

Discord OAuth2 extension for Flask.
Forked from Flaskcord, with support for flask[async]

Installation
============

To install the current latest release, use the following command:

.. code-block:: sh

   python3 -m pip install flaskcord

Basic Example
=============

.. code-block:: python

   import os

   from flask import Flask, redirect, url_for
   from flaskcord import DiscordOAuth2Session, requires_authorization, Unauthorized

   app = Flask(__name__)

   app.secret_key = b"random bytes representing flask secret key"
   os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"      # !! Only in development environment.

   app.config["DISCORD_CLIENT_ID"] = 490732332240863233    # Discord client ID.
   app.config["DISCORD_CLIENT_SECRET"] = ""                # Discord client secret.
   app.config["DISCORD_REDIRECT_URI"] = ""                 # URL to your callback endpoint.
   app.config["DISCORD_BOT_TOKEN"] = ""                    # Required to access BOT resources.

   discord = DiscordOAuth2Session(app)

   @app.route("/login/")
   def login():
       return discord.create_session()

   @app.route("/callback/")
   def callback():
       discord.callback()
       return redirect(url_for(".me"))

   @app.errorhandler(Unauthorized)
   def redirect_unauthorized(e):
       return redirect(url_for("login"))

   @app.route("/me/")
   @requires_authorization
   def me(): # supports async if using flask[async]!
       user = discord.fetch_user()
       return f"""
       <html>
           <head>
               <title>{user.name}</title>
           </head>
           <body>
               <img src='{user.avatar_url}' />
           </body>
       </html>"""

   if __name__ == "__main__":
       app.run()

Requirements
============

* Flask
* requests_oauthlib
* cachetools
* discord.py

Documentation
=============

Head over to the `documentation`_ for full API reference. 

.. _documentation: https://flaskcord.readthedocs.io/en/latest/
'''

import re
import os

from setuptools import setup, find_packages


def __get_version():
    with open("flaskcord/__init__.py") as package_init_file:
        return re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', package_init_file.read(), re.MULTILINE).group(1)


requirements = [
    "Flask",
    "pyjwt>=2.4.0",
    "requests",
    "oauthlib",
    "cachetools",
    "requests_oauthlib",
]


on_rtd = os.getenv('READTHEDOCS') == 'True'
if on_rtd:
    requirements.append('sphinxcontrib-napoleon')
    requirements.append('Pallets-Sphinx-Themes')

extra_requirements = {
    'docs': [
        'sphinx>=7.4.6'
    ]
}


setup(
    name='Flaskcord',
    version=__get_version(),
    url='https://github.com/Vinny-Bot/Flaskcord',
    license='MIT',
    author='The Cosmos & Vinny contributors',
    author_email='dev@vinny.pp.ua',
    description='Discord OAuth2 extension for Flask.',
    long_description=__doc__,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=requirements,
    extras_require=extra_requirements,
    classifiers=[
        'Framework :: Flask',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
