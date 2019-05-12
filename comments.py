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
from datetime import datetime
from basicauth import SubBasicAuth
from cassandra.cluster import Cluster

app = Flask(__name__)

basic_auth = SubBasicAuth(app)
basic_auth.init_app(app)

cluster = Cluster(['172.17.0.2'])

session = cluster.connect()
session.set_keyspace('testkeyspace')


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


# curl --include --verbose --header 'Content-Type: application/json' --user "email" --data '{"comment": "new comment"}' http://localhost/comments/new/9581b19d-05ee-40bd-8888-fbf98f0a0579/
@app.route('/comments/new/<id>', methods = ['GET', 'POST'])
def new_comment(id):

    # query = dbf.query_db("SELECT * FROM articles WHERE article_id=?", [id], one=True)
    query = session.execute("SELECT * FROM testkeyspace.articles WHERE article_id=" + str(id))

    if request.method == 'POST' and query[0] is not None:

        comment = request.json['comment']
        url = "http://localhost/articles/" + str(id)

        # cur = dbf.get_db().cursor()
        # db = dbf.get_db()
        
        if basic_auth.authenticate() == True:
            
            auth = request.authorization
            # cur.execute("INSERT INTO comments (comment, article_url, user_name) VALUES (?, ?, ?)", (comment, url, auth.username))
            stmt = session.prepare("INSERT INTO testkeyspace.comments (comment_id, comment, article_url, author, date_published) VALUES (uuid(),?,?,?, toTimeStamp(now()))") 
            session.execute(stmt, (comment, url, auth.username))

            msg = { 'message' : 'Comment has been added'}
            resp = jsonify(msg)
            resp.status_code = 201

            return resp
        
        elif basic_auth.authenticate() != True:

            # cur.execute("INSERT INTO comments (comment, article_url, user_name) VALUES (?, ?, ?)", (comment, url, "Anonymous Coward"))
            
            stmt = session.prepare("INSERT INTO testkeyspace.comments (comment_id, comment, article_url, author, date_published) VALUES (uuid(),?,?, \"Anonymous Coward\", toTimeStamp(now()))") 
            session.execute(stmt, (comment, url))
            
            msg = { 'message' : 'Comment has been added you coward..'}
            resp = jsonify(msg)
            resp.status_code = 201

            return resp

        elif query[0] is None:
            return not_found()

# curl --include --header 'Content-Type: application/json' -X DELETE --user "email" http://localhost/comments/delete/9581b19d-05ee-40bd-8888-fbf98f0a0579/5493d9ef-b638-4f0f-bb6d-a32b21a3075b
@app.route('/comments/delete/<article_id>/<comment_id>', methods = ['POST', 'GET', 'DELETE'])
# @basic_auth.required
def delete_comment(article_id,comment_id):

    cid = comment_id
    url = 'http://localhost/articles/' + str(article_id)

    # query = dbf.query_db("SELECT comment FROM comments WHERE article_url=?", [url], one = True)
    stmt = session.prepare("SELECT * FROM testkeyspace.comments WHERE article_url=? ALLOW FILTERING")
    query = session.execute(stmt, [url])

    if request.method == 'DELETE' and query[0] is not None:
        
        session.execute("DELETE FROM testkeyspace.comments WHERE comment_id=" + str(cid))

        msg = { 'message' : 'comment deleted...' }
        resp = jsonify(msg)
        resp.status_code = 201
        return resp

    elif query[0] is None:
        return not_found()

# curl --include --verbose --header 'Content-Type: application/json' --user "email"  http://localhost/comments/count/9581b19d-05ee-40bd-8888-fbf98f0a0579
@app.route('/comments/count/<article_id>', methods= ['GET'])
def count_comments(article_id):

    if request.method == 'GET':
        url = "http://localhost/articles/" + str(article_id)
        
        # number = dbf.query_db("SELECT COUNT(article_url) as count FROM comments WHERE article_url=?", [url], one=True)
        
        stmt = session.prepare("SELECT COUNT(article_url) as count FROM testkeyspace.comments WHERE article_url=? ALLOW FILTERING")
        number = session.execute(stmt, [url])
        num = number[0].count

        # comments = dbf.query_db("SELECT * FROM comments WHERE article_url=(?)", [url], one=True)
        stmt = session.prepare("SELECT * FROM testkeyspace.comments WHERE article_url=? ALLOW FILTERING")
        comments = session.execute(stmt, [url])

        msg = { 'numOfComments': str(num) }
        resp = jsonify(msg)
        resp.status_code = 200
        resp.headers['Last-Modified'] = str(datetime.strptime(str(comments[0].date_published), "%Y-%m-%d %H:%M:%S.%f"))

        return resp


# @app.route('/comments/recent/<id>/<n>', methods=['GET'])
# def recent_comments(id, n):

#     url = "http://localhost/articles/" + str(id)

#     comment = dbf.query_db("SELECT * FROM testkeyspace.comments WHERE article_url=? ORDER BY comment ASC LIMIT ?",[url, n])
#     # stmt = session.prepare("SELECT * FROM comments WHERE article_url=?")
    
#     comment_arr = []
    
#     if request.method == 'GET' and comment is not None:
#         for comments in comment:
#             comment_arr.append(
#                 {
#                     "comment" : comments["comment"]
#                 }
#             )

#         resp = jsonify(comment_arr)
#         resp.status_code = 200
#         resp.headers['Last-Modified'] = str(datetime.strptime(comment[0]['date_published'], "%Y-%m-%d %H:%M:%f"))

#         return resp
    
#     elif comment is None:
#         return not_found()

