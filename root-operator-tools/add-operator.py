#!/usr/bin/env python

import pymongo
import json
import argparse
import sys

parser = argparse.ArgumentParser(description='Add/Replace operator information')
parser.add_argument('input', metavar='input', type=str,
                    help='''File with operator information in JSON format (see example for details).  Use - to input from stdin''')
args = parser.parse_args()

if (not args.input):
    parser.print_help ()
    exit (1)

if args.input == '-':
    json_input = sys.stdin
else:
    json_input = open(args.input)

operator = json.load(json_input)

client = pymongo.MongoClient("localhost", 27017)
db = client.ndncert

db.operators.remove({'site_prefix': operator['site_prefix']})
db.operators.insert(operator)

print "[%s] site's operator [%s] has been added or updated" % (operator['site_prefix'], operator['name'])

