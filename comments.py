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
import sys

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
    pass


# curl --include --verbose --header 'Content-Type: application/json' --user "email" --data '{"comment": "new comment"}' http://localhost/comments/new/<article_id>
@app.route('/comments/new/<id>', methods = ['POST'])
def new_comment(id):

    query = session.execute("SELECT * FROM testkeyspace.articles WHERE article_id=" + str(id))

    if request.method == 'POST' and query[0] is not None:

        comment = request.json['comment']
        coward = "Anonymous Coward"
        url = "http://localhost/articles/" + str(id)
        
        if basic_auth.authenticate() == True:
            
            auth = request.authorization
            stmt = session.prepare("INSERT INTO testkeyspace.comments (comment_id, comment, article_url, author, date_published) VALUES (uuid(),?,?,?, toTimeStamp(now()))") 
            session.execute(stmt, (comment, url, auth.username))

            msg = { 'message' : 'Comment has been added'}
            resp = jsonify(msg)
            resp.status_code = 201

            return resp
        
        elif basic_auth.authenticate() != True:            
            stmt = session.prepare("INSERT INTO testkeyspace.comments (comment_id, comment, article_url, author, date_published) VALUES (uuid(), ?, ?, ?, toTimeStamp(now()))") 
            session.execute(stmt, (comment, url, coward))
            
            msg = { 'message' : 'Comment has been added you coward..'}
            resp = jsonify(msg)
            resp.status_code = 201

            return resp

        elif query[0] is None:
            return not_found()

# curl --include --header 'Content-Type: application/json' -X DELETE --user "email" http://localhost/comments/delete/<article_id>/<comment_id>
@app.route('/comments/delete/<article_id>/<comment_id>', methods = ['DELETE'])
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

# curl --include --verbose --header 'Content-Type: application/json' --user "email"  http://localhost/comments/count/<article_id>
@app.route('/comments/count/<article_id>', methods=['GET'])
def count_comments(article_id):
    
    url = "http://localhost/articles/" + str(article_id)
    
    query = session.execute("SELECT * FROM testkeyspace.articles WHERE article_id=" + str(article_id))  
    stmt = session.prepare("SELECT * FROM testkeyspace.comments WHERE article_url=? ALLOW FILTERING")
    comments = session.execute(stmt, [url])
    
    if request.method == 'GET':
        if query[0] is not None:
            # if article has no comments, do else
            if comments.current_rows:
                stmt = session.prepare("SELECT COUNT(article_url) as count FROM testkeyspace.comments WHERE article_url=? ALLOW FILTERING")
                number = session.execute(stmt, [url])
                num = number[0].count

                datepub_str = datetime.strftime(comments[0].date_published,"%a, %d %b %Y %I:%M:%S GMT")
                datepub_date = datetime.strptime(str(datepub_str), "%a, %d %b %Y %I:%M:%S GMT")

                msg = { 'numOfComments': str(num) }
                resp = jsonify(msg)
                resp.status_code = 200
                resp.headers['Last-Modified'] = datepub_str

                if request.headers.get("If-Modified-Since") is not None:
                    if request.if_modified_since < datepub_date:
                        return resp
                    else:
                        resp.status_code = 304
                        return resp
                else:
                    return resp
            else:
                msg = { 'numOfComments': 0}
                resp = jsonify(msg)
                return resp
        else:
            return not_found

#  curl --include --verbose --header 'Content-Type: application/json' --user "email" http://localhost/comments/recent/<id>/<num>
@app.route('/comments/recent/<id>/<n>', methods=['GET'])
def recent_comments(id, n):

    url = "http://localhost/articles/" + str(id)

    # Dynamic limit is unsupported in cql?
    stmt = session.prepare("SELECT * FROM testkeyspace.comments WHERE article_url=? LIMIT " + str(n) + " ALLOW FILTERING")
    comments = session.execute(stmt, [url])
    
    

    comment_arr = []
    
    if request.method == 'GET':
        if comments.current_rows:
            datepub_str = datetime.strftime(comments[0].date_published, "%a, %d %b %Y %I:%M:%S GMT")
            datepub_date = datetime.strptime(str(datepub_str), "%a, %d %b %Y %I:%M:%S GMT")
        
            for comment in comments:
                comment_arr.append(
                    {
                        "comment" : comment.comment
                        }
                        )

            resp = jsonify(comment_arr)
            resp.status_code = 200
            resp.headers['Last-Modified'] = datepub_str

            if request.headers.get("If-Modified-Since") is not None:
                if request.if_modified_since < datepub_date:
                    return resp
                else:
                    resp.status_code = 304
                    return resp            
            else:
                return resp

        else:
            return not_found()

#5c2dd169-ec3e-456f-9951-0ffd476f25ca