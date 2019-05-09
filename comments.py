"""
    Author: Juan Carrera
    File: comments.py
    Resources: 
        http://blog.luisrei.com/articles/flaskrest.html
        http://www.sqlitetutorial.net/

"""

from flask import Flask, logging
from flask import request, url_for, g, json, jsonify, Response
import sqlite3
import commentsdb as dbf
from datetime import datetime
from basicauth import SubBasicAuth


app = Flask(__name__)
basic_auth = SubBasicAuth(app)
basic_auth.init_app(app)

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url
    }

    resp = jsonify(message)
    resp.status_code = 404

    return resp

@app.route('/')
def root():
    return "hello"

@app.route('/comments/new/<int:id>', methods = ['GET', 'POST'])
def new_comment(id):

    query = dbf.query_db("SELECT * FROM articles WHERE article_id=?", [id], one=True)
   
    if request.method == 'POST' and query is not None:
        article_id = query['article_id']
        comment = request.json['comment']
        url = "http://localhost/articles/" + str(article_id)

        cur = dbf.get_db().cursor()
        db = dbf.get_db()
        
        if basic_auth.authenticate() == True:
            
            auth = request.authorization
            cur.execute("INSERT INTO comments (comment, article_url, user_name) VALUES (?, ?, ?)", (comment, url, auth.username))
            msg = { 'message' : 'Comment has been added'}
            resp = jsonify(msg)
            resp.status_code = 201

            return resp
        
        elif basic_auth.authenticate() != True:

            cur.execute("INSERT INTO comments (comment, article_url, user_name) VALUES (?, ?, ?)", (comment, url, "Anonymous Coward"))
            msg = { 'message' : 'Comment has been added you coward..'}
            
            resp = jsonify(msg)
            resp.status_code = 201

            return resp

        elif query is None:
            return not_found()


@app.route('/comments/delete/<string:article_id>/<int:comment_id>', methods = ['POST', 'GET', 'DELETE'])
# @basic_auth.required
def delete_comment(article_id,comment_id):

    url = "http://localhost/articles/" + article_id

    query = dbf.query_db("SELECT comment FROM comments WHERE article_url=?", [url], one = True)

    if request.method == 'DELETE' and query is not None:
        cur = dbf.get_db().cursor()
        db = dbf.get_db()
        cur.execute("DELETE FROM comments WHERE article_url = ? AND comment_id = ?", [url,comment_id])

        db.commit()
        cur.close()

        msg = { 'message' : 'comment deleted...' }

        resp = jsonify(msg)
        resp.status_code = 201

        return resp
    elif query is None:
        return not_found()

@app.route('/comments/count/<string:article_id>', methods= ['GET'])
def count_comments(article_id):

    if request.method == 'GET':
        url = "http://localhost/articles/" + article_id
        
        number = dbf.query_db("SELECT COUNT(article_url) as count FROM comments WHERE article_url=?", [url], one=True)
        num = number['count']

        comments = dbf.query_db("SELECT * FROM comments WHERE article_url=(?)", [url], one=True)
        
        msg = { 'numOfComments': str(num) }

        

        resp = jsonify(msg)
        resp.status_code = 200
        resp.headers['Last-Modified'] = str(datetime.strptime(comments['date_published'], "%Y-%m-%d %H:%M:%f"))

        return resp


@app.route('/comments/recent/<string:id>/<int:n>', methods=['GET'])
def recent_comments(id, n):

    url = "http://localhost/articles/" + id
    comment = dbf.query_db("SELECT * FROM comments WHERE article_url=? ORDER BY comment ASC LIMIT ?",[url, n])

    comment_arr = []
    
    if request.method == 'GET' and comment is not None:
        for comments in comment:
            comment_arr.append(
                {
                    "comment" : comments["comment"]
                }
            )

        resp = jsonify(comment_arr)
        resp.status_code = 200
        resp.headers['Last-Modified'] = str(datetime.strptime(comment[0]['date_published'], "%Y-%m-%d %H:%M:%f"))

        return resp
    
    elif comment is None:
        return not_found()

