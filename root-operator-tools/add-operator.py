#!/usr/bin/env python

import pymongo

client = pymongo.MongoClient("localhost", 27017)
db = client.ndncert


operator = {
    'name': 'Alexander Afanasyev',
    'email': 'afanasev@cs.ucla.edu',
    'key': '',
    'last_timestamp': '',
    'site_emails': ['ucla.edu', 'cs.ucla.edu'],
    'site_name': 'University of California, Los Angeles',
    'site_prefix': '/ndn/edu/ucla'
    }

db.operators.insert(operator)
