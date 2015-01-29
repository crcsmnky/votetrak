import celery
import sunlight
import logging
import redis
import twitter
from ConfigParser import ConfigParser
from datetime import datetime, timedelta


logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(name)s.%(module)s.%(funcName)s: %(message)s')


class Votes(object):
    db = None
    config = None
    twitter = None
    cache = None

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.config = ConfigParser()
        self.config.read(kwargs.get('config', 'dev.config'))

        self.logger.debug("read {} sections: {}".format(
            len(self.config.sections()), self.config.sections()))

        sunlight.config.API_KEY = self.getConfig().get('votetrak', 'sunlight')
        self.logger.debug("sunlight API key: {}".format(sunlight.config.API_KEY))


    def getConfig(self):
        return self.config

    def getCache(self):
        if self.cache is None:
            self.logger.debug("self.cache not set")
            cfg = self.getConfig()
            self.logger.debug("connecting to redis")
            self.cache = redis.Redis(
                host=cfg.get('votetrak', 'redishost'),
                port=cfg.getint('votetrak', 'redisport'),
                db=cfg.getint('votetrak', 'redisdb')
            )
        return self.cache

    def getTwitter(self):
        if self.twitter is None:
            self.logger.debug("twitter not set")
            cfg = self.getConfig()

            self.logger.debug("connecting to twitter")
            self.twitter = twitter.Api(
                consumer_key=cfg.get('twitter','consumer_key'),
                consumer_secret=cfg.get('twitter','consumer_secret'), 
                access_token_key=cfg.get('twitter','access_token'),
                access_token_secret=cfg.get('twitter','access_token_secret')
            )
        return self.twitter

    def run(self):
        tweetfmt = "{bill_id}: \"{question}...\" ({title}...) {link}"
        datetimefmt = "%Y-%m-%dT%H:%M:%SZ"

        lastvote = self.getCache().get('lastvote')
        self.logger.debug("lastvote: {}".format(lastvote))

        if lastvote is None:
            lastvote = (datetime.utcnow().replace(microsecond=0) - 
                timedelta(minutes=30)).strftime(datetimefmt)

        self.logger.debug("getting votes since {}".format(lastvote))
        votes = sunlight.congress.votes(
            fields=self.getConfig().get('votes','fields'), 
            voted_at__gt=lastvote)

        if votes:
            lastvote = votes[0]['voted_at']
            self.getCache().set('lastvote', lastvote)
            self.logger.debug("setting lastvote: {}".format(votes[0]['voted_at']))
            tw = self.getTwitter()
            for v in votes:
                tweet = tweetfmt.format(
                    bill_id=v['bill_id'].capitalize(),
                    question=v['question'][0:30],
                    title=v['official_title'][0:30],
                    link="vtrk.us/"+v['bill_id']
                )
                self.logger.debug("tweet: {}".format(tweet))


def main():
    v = Votes()
    v.run()


if __name__ == '__main__':
    main()
        

