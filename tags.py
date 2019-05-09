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
import tagsdb as dbf
import sqlite3

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
    pass
#curl -i --header 'Content-Type: application/json' -d '{"tag":"new tag"}' http://localhost:5000/tag/new/1
@app.route('/tags/new/<int:id>', methods = ['GET','POST'])
# @basic_auth.required

def new_tag(id):

    query = dbf.query_db("SELECT * FROM articles WHERE article_id=?", [id], one=True)
    # if request.headers['Content-Type'] == 'application/json':

    if request.method == 'POST' and query is not None:
        article_id = query['article_id']

        tag = request.json['tag']

        url = "http://localhost/articles/" + str(article_id)

        cur = dbf.get_db().cursor()
        db = dbf.get_db()

        #auth = request.authorization

        cur.execute("INSERT INTO tags (tag_name, article_url) VALUES (?, ?)", (tag, url))

        db.commit()
        cur.close()

        msg = { 'message' : 'Tag added...' }

        # resp = Response(msg, status=201, mimetype='application/json')
        resp = jsonify(msg)
        resp.status_code = 201

        return resp
    elif query is None:
        return not_found()
        
    else:
        return "Unsupported media type.. "

#curl -i --header 'Content-Type: application/json' -d '{"tag":"new tag"}' http://localhost:5000/tag/new/1
@app.route('/tags/edit/<int:id>', methods = ['GET','POST'])
# @basic_auth.required

def edit_tag(id):

    query = dbf.query_db("SELECT * FROM articles WHERE article_id=?", [id], one=True)
    
    # if request.headers['Content-Type'] == 'application/json':

    if request.method == 'POST' and query is not None:
        article_id = query['article_id']

        query = dbf.query_db("SELECT * FROM articles WHERE article_id=?", [id], one=True)

        tag = request.json['tag']

        url = "http://localhost/articles/" + str(article_id)
    
        cur = dbf.get_db().cursor()
        db = dbf.get_db()

        cur.execute("INSERT INTO tags (tag_name, article_url) VALUES (?, ?)", (tag, url))

        db.commit()
        cur.close()

        msg = { 'message' : 'Tag added...' }

    # resp = Response(msg, status=201, mimetype='application/json')
        resp = jsonify(msg)
        resp.status_code = 201

        return resp
    elif query is None:
        return not_found()

    else:
        return "Unsupported media type.. "

# curl --include --header 'Content-Type: application/json' -X DELETE http://localhost:5000/tag/delete/1
@app.route('/tags/delete/<int:id>', methods = ['POST', 'GET', 'DELETE'])
# @basic_auth.required

def delete_tag(id):

    tag = dbf.query_db("SELECT tag_id FROM tags WHERE tag_id=?", [id], one = True)

    #if request.headers['Content-Type'] == 'application/json':
    if request.method == 'DELETE' and tag is not None:
        cur = dbf.get_db().cursor()
        db = dbf.get_db()
        cur.execute("DELETE FROM tags WHERE tag_id = ?", [id])

        db.commit()
        cur.close()

        msg = { 'message' : 'Tag deleted...' }

        resp = jsonify(msg)
        resp.status_code = 201

        return resp
    elif tag is None:
        return not_found()

    else:
        return "Unsupported media type.. "
                
# curl --include --header 'Content-Type: application/json' http://localhost:5000/tags/all/<int:article_id>
@app.route('/tags/all/<string:article_id>', methods=['GET'])
def tag_for_id(article_id): 
    
    url = "http://localhost/articles/" + article_id
    
    tags = dbf.query_db("SELECT tag_name FROM tags WHERE article_url=?", [url])
    tags_arr = []

    #if request.headers['Content-Type'] == 'application/json':
    if request.method == 'GET' and tags is not None: 
        for tag in tags:
            tags_arr.append(
                {
                    "tag" : tag["tag_name"]
                }
            )

        resp = jsonify(tags_arr)
        resp.status_code = 200

        return resp
        
    elif tags is None:
        return not_found()

    # else: 
    #     return "Unsupported media type.. "


#curl --include --header 'Content-Type: application/json' http://localhost:5000/tags/list_url/<string:tag>
@app.route('/tags/list_url/<string:tag>', methods=['GET'])

def list_all_url(tag):

    url = dbf.query_db("SELECT article_url FROM tags WHERE tag_name=?",[tag])

    url_arr = []

    #if request.headers['Content-Type'] == 'application/json':
    if request.method == 'GET' and url is not None: 
        for urls in url:
            url_arr.append(
                {
                    "urls for this tag" : urls["article_url"]
                }
            )

        resp = jsonify(url_arr)
        resp.status_code = 200

        return resp
        
    elif url is None:
        return not_found()
    else: 
        return "Unsupported media type.. "


    



