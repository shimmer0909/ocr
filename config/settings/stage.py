from .base import *

#
#
#AWS_ACCESS_KEY_ID = 'AKIAILVXH37AKICDTG4Q'
#AWS_SECRET_ACCESS_KEY = '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'
#
#AWS_S3_BUCKET = 'docs-indifi-staging'

RABBIT_MQ["HOST"] = "3.7.61.186"
RABBIT_MQ["HEARTBEAT"] = 60
RABBIT_MQ["USER_NAME"] = "indifi"
RABBIT_MQ["PASSWORD"] = "test123"



MONGO["DBNAME"] = 'arya-dev'
MONGO["HOST"] = 'cluster0-jfb0t.mongodb.net'
MONGO["USER"] = 'dev-user'
MONGO["PASSWORD"] = 'indifi123'