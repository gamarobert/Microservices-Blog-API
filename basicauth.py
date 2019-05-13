from flask import Flask
from flask_basicauth import BasicAuth
from passlib.hash import sha256_crypt
import sqlite3
from cassandra.cluster import Cluster
import sys


cluster = Cluster(['172.17.0.2'])

session = cluster.connect()
session.set_keyspace('testkeyspace')

class SubBasicAuth(BasicAuth):
    
    def check_credentials(self, username, password):

        password_cand = password

        stmt = session.prepare("SELECT * FROM testkeyspace.users WHERE username=? ALLOW FILTERING")
        query = session.execute(stmt, [username])

        if password_cand is not None and query[0].username is not None:
            password_db = query[0].password
            return sha256_crypt.verify(password_cand, password_db)
        else:
            return False   
