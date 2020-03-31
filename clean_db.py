#!/usr/bin/env python3

# script for use in a crontab for cleaning dbase
# it removes rows older than 21 days
import sqlite3
import sys

dbpath = sys.argv[1]
sql = """DELETE FROM telegrams WHERE timestamp <= date('now','-21 day'); """
con = sqlite3.connect(dbpath)
cur = con.cursor()
cur.execute(sql)
con.commit()
