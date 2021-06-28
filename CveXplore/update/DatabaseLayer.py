#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Database layer translates database calls to functions
#
# Software is free software released under the "GNU Affero General Public License v3.0"
#
# Copyright (c) 2015-2018  Pieter-Jan Moreels - pieterjan.moreels@gmail.com

# imports

import pymongo

from .Config import Configuration as conf

# Variables
db = conf.getMongoConnection()
colCVE = db["cves"]
colCPE = db["cpe"]
colCWE = db["cwe"]
colCPEOTHER = db["cpeother"]
colINFO = db["info"]
colVIA4 = db["via4"]
colCAPEC = db["capec"]

mongo_version = db.command("buildinfo")["versionArray"]
# to check if mongodb > 4.4
# if it is, then use allow_disk_use for optimized queries
# to be removed in future with the conditional statements
# and use allow_disk_use by default

# Functions
def sanitize(x):
    if type(x) == pymongo.cursor.Cursor:
        x = list(x)
    if type(x) == list:
        for y in x:
            sanitize(y)
    if x and "_id" in x:
        x.pop("_id")
    return x


# DB Functions
def ensureIndex(collection, field, **kwargs):
    db[collection].create_index(field, **kwargs)


def drop(collection):
    db[collection].drop()


def setColUpdate(collection, date):
    colINFO.update({"db": collection}, {"$set": {"last-modified": date}}, upsert=True)


def setColInfo(collection, field, data):
    colINFO.update({"db": collection}, {"$set": {field: data}}, upsert=True)


def updateCVE(cve):
    if cve["cvss3"] is not None:
        colCVE.update(
            {"id": cve["id"]},
            {
                "$set": {
                    "cvss3": cve["cvss3"],
                    "impact3": cve["impact3"],
                    "exploitability3": cve["exploitability3"],
                    "cvss3-vector": cve["cvss3-vector"],
                    "impactScore3": cve["impactScore3"],
                    "exploitabilityScore3": cve["exploitabilityScore3"],
                    "cvss": cve["cvss"],
                    "summary": cve["summary"],
                    "references": cve["references"],
                    "impact": cve["impact"],
                    "vulnerable_product": cve["vulnerable_product"],
                    "access": cve["access"],
                    "cwe": cve["cwe"],
                    "vulnerable_configuration": cve["vulnerable_configuration"],
                    "vulnerable_configuration_cpe_2_2": cve[
                        "vulnerable_configuration_cpe_2_2"
                    ],
                    "last-modified": cve["Modified"],
                }
            },
            upsert=True,
        )
    else:
        colCVE.update(
            {"id": cve["id"]},
            {
                "$set": {
                    "cvss3": cve["cvss3"],
                    "cvss": cve["cvss"],
                    "summary": cve["summary"],
                    "references": cve["references"],
                    "impact": cve["impact"],
                    "vulnerable_product": cve["vulnerable_product"],
                    "access": cve["access"],
                    "cwe": cve["cwe"],
                    "vulnerable_configuration": cve["vulnerable_configuration"],
                    "vulnerable_configuration_cpe_2_2": cve[
                        "vulnerable_configuration_cpe_2_2"
                    ],
                    "last-modified": cve["Modified"],
                }
            },
            upsert=True,
        )


def dropCollection(col):
    return db[col].drop()
    # jdt_NOTE: is exactly the same as drop(collection)
    # jdt_NOTE: use only one of them


def getTableNames():
    # return db.collection_names()
    # jdt_NOTE: collection_names() is depreated, list_collection_names() should be used instead
    return db.list_collection_names()


def getCPEVersionInformation(query):
    return sanitize(colCPE.find_one(query))


def getCPEs():
    return sanitize(colCPE.find())


def getInfo(collection):
    return sanitize(colINFO.find_one({"db": collection}))
