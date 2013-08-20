#!/usr/bin/env python
# encoding: utf-8
"""
database.py

this is a collection of interface methods for mongodb

Created by nano on 2012-06-08.
Copyright (c) 2012 UCLA Regents. All rights reserved.
"""

import re
import sys
import pymongo
from pymongo import Connection
from pymongo.errors import CollectionInvalid
from pymongo import ASCENDING, DESCENDING
#from pymongo.code import Code
from bson.code import Code
import string
import json
from decimal import *
import operator
from collections import OrderedDict
import os
import ConfigParser
import io
from BeautifulSoup import BeautifulSoup
from xml.dom.minidom import parseString
from datetime import datetime, date, time
import time as _time

config = ConfigParser.RawConfigParser()
configFile = os.path.dirname(__file__)+'/config.cfg'
config.readfp(open(configFile))

connection = Connection('localhost', int(config.get("archiver", "dbPort")))
#db = connection.test
#ollection = db.test

colName = str(config.get("archiver", "colName"))

db = connection[colName]
collection = db[colName]

def main():
    pass

if __name__ == '__main__':
	main()

def index(req):
    sys.stderr = sys.stdout
    req.content_type = "text/plain"
    req.write("Hello World!\n")
    anotherMethod(req)
    #writeDatabase(req)

def logDatabase(predictionXML, locationXML, nextBusRoute, nextBusOccupancy, nextBusETA, nextBusPredictable):
    #connect to mongoDB
    #connection = Connection()
    #db = connection.test
    #collection = db.test

    data = post={"time":_time.time(), "predictions":predictionXML, "vehicleLocations":locationXML, "nextBusRoute":nextBusRoute,"nextBusOccupancy":nextBusOccupancy,"nextBusETA":nextBusETA, "nextBusPredictable":nextBusPredictable}

    lastID = collection.insert(data)

    return lastID

def clearDatabase():
    # clear collection
    db.drop_collection(colName)

def getEntryFromID(id):
    return(collection.find_one({"_id":id}))

def getLastEntry():
    lastEntry = collection.find_one(sort = [('_id',DESCENDING)])
    return lastEntry

def getAllEntries(limit):
    allEntries = collection.find(sort = [('_id',ASCENDING)]).skip(75000).limit(limit)
    return allEntries
    
def getAllEntriesDuringDay(y,m,d):
    # return only entries for a given day between 8am and 6pm 

    day = date(y,m,d)
    startTime = time(7,30)
    endTime = time(18,30)

    startDateTime = datetime.combine(day,startTime)
    endDateTime = datetime.combine(day,endTime)

    morning = int(_time.mktime(startDateTime.timetuple()))
    evening = int(_time.mktime(endDateTime.timetuple()))

    series = collection.find({ "time" : {"$gt": morning, "$lt": evening} })
    return series
    

'''
#MAP REDUCE - sorta working ish

map = Code("function() {for (var key in this) { emit(key, null); }}")
reduce = Code("function(key, stuff) { return null; }")

result = collection.map_reduce(map,reduce,"host").distinct("_id")

for doc in result:
        out+=doc+"\n"
'''
