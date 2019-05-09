from flask import Flask
from flask_basicauth import BasicAuth
from passlib.hash import sha256_crypt
import userdb as db
import sqlite3

class SubBasicAuth(BasicAuth):
    def check_credentials(self, username, password):

        password_cand = password
        query = db.query_db("SELECT * FROM users WHERE username=?", [username], one=True)

        if password_cand is not None and query is not None:
            password_db = query['password']
            return sha256_crypt.verify(password_cand, password_db)
        else:
            return False   
          
    