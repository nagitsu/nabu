DATABASE_ENGINE = "sqlite:///data.db"
LOG_FILE_LOCATION = 'corpus.log'

MAX_RETRIES = 5
REQUEST_TIMEOUT = 20
REQUEST_COOLDOWN = 0.2
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:36.0) Gecko/20100101 Firefox/36.0'
}
REQUEST_CONCURRENCY = 50
LOOP_COOLDOWN = 900

MIN_WORDS_PER_DOCUMENT = 10

LOGGING_CONFIG = {
    'version': 1,

    'formatters': {
        'verbose': {
            'format': "%(levelname)s :: %(asctime)s :: %(module)s :: %(message)s"
        },
    },

    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILE_LOCATION,
            'maxBytes': 1024*1024*10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },

    'loggers': {
        'nabu.corpus': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'gensim': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
