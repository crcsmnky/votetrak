import celery
from ConfigParser import ConfigParser


config = ConfigParser()
config.read('votetrak.config')


app = celery.Celery(
    'votetrak',
    broker='redis://{}:{}/{}'.format(
        config.get('votetrak','redishost'),
        config.getint('votetrak','redisport'),
        config.getint('votetrak','celerydb')),
    include=['tasks']
)


if __name__ == '__main__':
    app.start()
