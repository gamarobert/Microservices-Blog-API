"""
    Author: Juan Carrera
    File: comments.py
    Resources: 
        http://blog.luisrei.com/articles/flaskrest.html
        http://www.sqlitetutorial.net/
        
"""

from flask import Flask, logging
from flask import request, url_for, g, json, jsonify, Response
from basicauth import SubBasicAuth
import sqlite3
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
    pass
    
#curl -i --header 'Content-Type: application/json' -d '{"tag":"new tag"}' http://localhost/tags/new/9581b19d-05ee-40bd-8888-fbf98f0a0579
@app.route('/tags/new/<id>', methods = ['GET','POST'])
def new_tag(id):
    
    query = session.execute("SELECT * FROM testkeyspace.articles WHERE article_id ="+str(id))

    if request.method == 'POST' and query[0] is not None:
        
        article_id = query[0].article_id
        tag = request.json['tag']

        url = "http://localhost/articles/" + str(article_id)

        stmt = session.prepare("INSERT INTO testkeyspace.tags (tag_id ,tag_name, article_url) VALUES (uuid(),?, ?)")
        session.execute(stmt, (tag, url))

        msg = { 'message' : 'Tag added...' }
        resp = jsonify(msg)
        resp.status_code = 201

        return resp
    elif query[0] is None:
        return not_found()

#curl -i --header 'Content-Type: application/json' -d '{"tag_name":"tag2"}' -u "email" http://localhost/tags/edit/80380782-a891-4132-a1c6-69c738c6c968
@app.route('/tags/edit/<tag_id>', methods = ['GET','POST'])
def edit_tag(tag_id):

    query = session.execute("SELECT * FROM testkeyspace.tags WHERE tag_id ="+str(tag_id))
    
    if request.method == 'POST' and query[0] is not None:
        
        tag = request.json['tag_name']
        
        stmt = session.prepare("UPDATE testkeyspace.tags SET tag_name=? WHERE tag_id=" + str(tag_id))
        session.execute(stmt, [tag])

        msg = { 'message' : 'Tag updated...' }
        resp = jsonify(msg)
        resp.status_code = 201

        return resp
    elif query[0] is None:
        return not_found()

    else:
        return "Unsupported media type.. "

# curl --include --header 'Content-Type: application/json' -X DELETE http://localhost/tags/delete/980d08d4-e376-4fe3-a52e-400c29f80604
@app.route('/tags/delete/<id>', methods = ['POST', 'GET', 'DELETE'])
def delete_tag(id):

    found_tag = session.execute("SELECT * FROM testkeyspace.tags WHERE tag_id=" + str(id))

    if request.method == 'DELETE' and found_tag[0] is not None:
        
        session.execute("DELETE FROM testkeyspace.tags WHERE tag_id ="+str(id))

        msg = { 'message' : 'Tag deleted...' }

        resp = jsonify(msg)
        resp.status_code = 201

        return resp

    elif found_tag[0] is None:
        return not_found()

# curl --include --header 'Content-Type: application/json' -u "email" http://localhost/tags/all/9581b19d-05ee-40bd-8888-fbf98f0a0579 
@app.route('/tags/all/<string:article_id>', methods=['GET'])
def tag_for_id(article_id): 
    
    url = "http://localhost/articles/" + article_id
    
    # tags = dbf.query_db("SELECT tag_name FROM tags WHERE article_url=?", [url])
    stmt = session.prepare("SELECT tag_name FROM tags WHERE article_url=? ALLOW FILTERING")
    tags = session.execute(stmt, [url])
    
    tags_arr = []



    #if request.headers['Content-Type'] == 'application/json':
    if request.method == 'GET' and tags is not None: 
        for tag in tags:
            tags_arr.append(
                {
                    "tag" : tag.tag_name
                }
            )

        resp = jsonify(tags_arr)
        resp.status_code = 200

        return resp
        
    elif tags is None:
        return not_found()


#curl --include --header 'Content-Type: application/json' -u "email" http://localhost/tags/list_url/tag2
@app.route('/tags/list_url/<string:tag>', methods=['GET'])

def list_all_url(tag):

    stmt = session.prepare("SELECT * FROM tags WHERE tag_name=? ALLOW FILTERING")
    urls = session.execute(stmt, [tag])

    url_arr = []

    if request.method == 'GET' and urls is not None: 
        for url in urls:
            url_arr.append(
                {
                    "urls" : url.article_url
                }
            )

        resp = jsonify(url_arr)
        resp.status_code = 200

        return resp
        
    elif url is None:
        return not_found()

