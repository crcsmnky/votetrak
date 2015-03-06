#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import time
import json
import tweepy
import logging

from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from webapp2_extras import jinja2
from ConfigParser import SafeConfigParser
from datetime import datetime, timedelta


class TweetVote(ndb.Model):
    tweet = ndb.TextProperty()
    bill_id = ndb.StringProperty()
    voted_at = ndb.DateTimeProperty()
    tweeted_at = ndb.DateTimeProperty(auto_now_add=True)


class BaseHandler(webapp2.RequestHandler):
    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    @webapp2.cached_property
    def config(self):
        config = SafeConfigParser()
        config.read('settings.cfg')
        return config

    def render_response(self, template, **context):
        response = self.jinja2.render_template(template, **context)
        self.response.write(response)

    def handle_exception(self, exception, debug):
        logging.exception(exception)
        context = {}
        self.render_response('error.html', **context)
        if isinstance(exception, webapp2.HTTPException):
            self.response.set_status(exception.code)
        else:
            self.response.set_status(500)


class HomeHandler(BaseHandler):
    def get(self):
        context = {}
        self.render_response('home.html', **context)


class BillHandler(BaseHandler):
    def get(self, bill_id):
        bills = self.get_bills(bill_id)
        try:
            context = {'bill': bills[0]}
        except IndexError:
            self.response.set_status(500)
        self.render_response('bill.html', **context)

    def get_bills(self, bill_id):
        key = self.config.get('sunlight', 'key')
        fields = self.config.get('bills', 'fields')
        bills_url = self.config.get('bills', 'url')

        logging.info('getting bill matching {}'.format(bill_id))

        url = bills_url.format(key=key, fields=fields, bill_id=bill_id)
        response = urlfetch.fetch(url)

        if response.status_code == 200:
            bills = json.loads(response.content)['results']
            logging.info('{} bills returned'.format(len(bills)))
        else:
            logging.info('get_bills url fetch {}'.format(response.status_code))
            bills = []

        return bills


class TweetVoteHandler(BaseHandler):
    _twitterapi = None

    def get(self):
        query = TweetVote.query().order(-TweetVote.voted_at)
        tweet_votes = query.fetch(1, projection=[TweetVote.voted_at])

        try:
            last_voted_at = self.generate_last_voted_at(tweet_votes[0].voted_at)
        except IndexError:
            last_voted_at = self.generate_last_voted_at()

        votes = self.get_votes(last_voted_at)

        if votes:
            tw = self.get_twitter()
            for v in votes:
                tweet = self.tweet_vote(v)
                self.response.write(tweet + '<br>')
                tweetvote = TweetVote(
                    bill_id=v['bill_id'], tweet=tweet, 
                    voted_at=self.convert_to_datetime(v['voted_at']))
                tweetvote.put()

    def get_votes(self, voted_at):
        key = self.config.get('sunlight', 'key')
        fields = self.config.get('votes', 'fields')
        votes_url = self.config.get('votes', 'url')

        logging.info('getting votes since {}'.format(voted_at))

        url = votes_url.format(key=key, fields=fields, voted_at=voted_at)
        response = urlfetch.fetch(url)

        if response.status_code == 200:
            votes = json.loads(response.content)['results']
            logging.info('{} votes returned'.format(len(votes)))
        else:
            logging.info('get_votes url fetch {}'.format(response.status_code))
            votes = None

        return votes

    def tweet_vote(self, vote):
        tweetfmt = self.config.get('twitter', 'tweet')
        tweet = tweetfmt.format(
            bill_id_cap=vote['bill_id'].upper(),
            question=vote['question'][0:40],
            title=vote['bill']['official_title'][0:50],
            bill_id=vote['bill_id'],
            yes=vote['breakdown']['total']['Yea'],
            no=vote['breakdown']['total']['Nay']            
        )
        logging.info(tweet)
        self.get_twitter().update_status(tweet)
        return tweet

    def get_twitter(self):
        if self._twitterapi is None:
            cfg = self.config
            auth = tweepy.OAuthHandler(cfg.get('twitter','consumer_key'),
                                       cfg.get('twitter','consumer_secret'))
            auth.set_access_token(cfg.get('twitter','access_token'),
                                  cfg.get('twitter','access_token_secret'))
            logging.info('logging into twitter via tweepy')
            self._twitterapi = tweepy.API(auth)
        return self._twitterapi

    def convert_to_datetime(self, datestr):
        datetimefmt = "%Y-%m-%dT%H:%M:%SZ"
        return datetime.strptime(datestr, datetimefmt)

    def generate_last_voted_at(self, dt=None):
        datetimefmt = "%Y-%m-%dT%H:%M:%SZ"
        if dt is None:
            dt = datetime.utcnow().replace(microsecond=0) - timedelta(minutes=60)
        return dt.strftime(datetimefmt)


app = webapp2.WSGIApplication([
    (r'/', HomeHandler),
    (r'/bills/(.+)', BillHandler),
    (r'/tweet-vote', TweetVoteHandler)
], debug=True)
