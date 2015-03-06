# Votetrak

A Google App Engine app that tweets every 60 minutes about congressional votes that have occurred in the last hour.

Currently available at [votetrak.us](http://www.votetrak.us)

## Requirements

- Download and install [Python 2.7.x](https://www.python.org/downloads/)
- Install [pip](https://pip.pypa.io/en/latest/installing.html) (if not already installed with Python 2.7.9)
- Download and install [Google App Engine SDK for Python](https://cloud.google.com/appengine/downloads)

## Setup

Install the required dependencies to run the app (this will install the libraries in the local `lib` directory):

    $ pip install -r requirements.txt -t lib

Create a `settings.cfg` file based on the [sample provided](https://github.com/crcsmnky/votetrak/blob/master/settings.cfg.sample) and fill in the appropriate details:

- Get a [Sunlight Foundation API key](http://sunlightfoundation.com/api/)
- [Create a Twitter account](https://twitter.com/signup) that will tweet the tweets
- [Generate an OAuth access token](https://dev.twitter.com/oauth/overview/application-owner-access-tokens) for your application

## Local Deployment

Start the [Python development web server](https://cloud.google.com/appengine/docs/python/tools/devserver):

    $ dev_appserver.py .

Refer to the link above for more information about the options available when running the development web server.

