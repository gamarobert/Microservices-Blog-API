from flask import Flask
from flask import request, g, json, jsonify
from basicauth import SubBasicAuth
from datetime import datetime
import articlesdb as dbf
import sqlite3
import sys

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

# @app.errorhandler(304)
# def not_modified(error=None):
#     message = {
#         'status': 304,
#         'message': 'Not Modified: ' + request.url
#     }

#     resp = jsonify(message)
#     resp.status_code = 304

    # return resp

@app.route('/articles')
def root():
    return "testing testing..."

# curl -i --header 'Content-Type: application/json' http://localhost:5000/articles/<id>/
@app.route('/articles/<int:id>/', methods=['GET'])
def article(id):

    articles = dbf.query_db("SELECT * FROM articles WHERE article_id = ?", [id], one=True)
    datemod = datetime.strptime(articles['last_modified'], "%Y-%m-%d %H:%M:%S.%f")

    lastmodified = datemod.strftime("%a, %d %b %Y %I:%M:%S GMT")
    
    # print(str(request.if_modified_since == "If-Modified-Since: " + str(lastmodified.strftime("%a, %d %b %Y %I:%M:%S GMT"))), file=sys.stderr)
    # print(request.if_modified_since, file=sys.stderr)

    # print(str(request.headers['If-Modified-Since: ' +str(lastmodified)]), file=sys.stderr)
    
    # if request.headers.get('If-Modified-Since','') < lastmodified:
    #     print(str(request.headers.get('If-Modified-Since',str(lastmodified))), file=sys.stderr)

    is_conditional = request.headers.get('If-Modified-Since') or request.headers.get('If-None-Match')

    if request.method == 'GET' and is_conditional == None:
        if articles is not None:
            article = articles['title']
            message = {
                "article": article
            }
            resp = jsonify(message)
            resp.status_code = 200
            resp.headers['Last-Modified'] = str(lastmodified)
            return resp
        else:
            return not_found()
    else:
            message = {
                'message': 'HTTP 304: Not Modified'
            }
            resp = jsonify(message)
            resp.status_code = 304
            return resp
    


# curl --include --verbose --request POST --header 'Content-Type: application/json' --user "username" --data '{"title":"Testing Title","content":"TESTINGGG"}' http://localhost:5000/articles/new_article/
@app.route('/articles/new_article/' , methods=['POST'])
# @basic_auth.required
def new_article():
    
    if request.method == 'POST':
        cur = dbf.get_db().cursor()
        db = dbf.get_db()

        auth = request.authorization
        
        title = request.json['title']
        content = request.json['content']

        cur.execute("INSERT INTO articles (author, title, content) VALUES (?, ?, ?)",
                        (auth.username, title, content))

        db.commit()
        cur.close()

        message = {
            'message': 'Article created!'
        }
        
        resp = jsonify(message)
        resp.status_code = 201
        return resp


# curl --include --header 'Content-Type: application/json' --user "username" --data '{"title": "Changed title", "content": "edited content"}' http://localhost:5000/articles/edit_article/<int:id>/
@app.route('/articles/edit_article/<int:id>/', methods=['GET', 'POST'])
# @basic_auth.required
def edit_article(id):

    article = dbf.query_db("SELECT * FROM articles WHERE article_id=?", [id], one=True)

    if request.method == 'POST' and article is not None:

        title = request.json['title']
        content = request.json['content']
        cur = dbf.get_db().cursor()
        db = dbf.get_db()

        #time is weird due to sqlite TIMESTAMP and python datetime.now?
        cur.execute("UPDATE articles SET title=?, content=?, last_modified=? WHERE article_id=?", 
                    (title, content, datetime.now(), id))
        db.commit()
        cur.close()

        message = {
            'message': 'Article updated!'
        }

        resp = jsonify(message)
        resp.status_code = 201

        return resp
    elif article is None:
        return not_found()  

# curl --include --header 'Content-Type: application/json' -X DELETE --user "username" http://localhost:5000/articles/delete_article/1/
@app.route('/articles/delete_article/<int:id>/', methods=['DELETE'])
# @basic_auth.required
def delete_article(id):
    
    article = dbf.query_db("SELECT * FROM articles WHERE article_id=?", [id], one=True)
    
    if request.method == 'DELETE' and article is not None:   
        cur = dbf.get_db().cursor()
        db = dbf.get_db()
        cur.execute("DELETE FROM articles WHERE article_id = ?", [id])

        db.commit()
        cur.close()
    
        message = {
            'message': 'Article successfully deleted.'
        }
        resp = jsonify(message)

        return resp
    elif article is None:
        return not_found()
 
# curl --include --verbose --header 'Content-Type: application/json' http://localhost:5000/articles/retrieve_articles/2/
@app.route('/articles/retrieve_articles/<int:num>/', methods=['GET'])
def retrieve_articles(num):
    
    articles = dbf.query_db("SELECT * FROM articles ORDER BY article_id DESC LIMIT (?)", [num])

    # will hold all articles 
    articles_msg = []

    if request.method == 'GET' and articles is not None:
        for article in articles:
            articles_msg.append(
                {
                    "article_id": article['article_id'],
                    "author": article['author'],
                    "title": article['title'],
                    "content": article['content'],
                    "date_published": article['date_published'],
                    "last_modified": article['last_modified']
                }   
            )
        
        resp = jsonify(articles_msg)
        resp.status_code = 200
        resp.headers['Last-Modified'] = str(datetime.strptime(articles[0]['last_modified'], "%Y-%m-%d %H:%M:%f"))

        return resp
    elif articles is None:
        return not_found()

#  curl -i --header 'Content-Type: application/json' http://localhost:5000/articles/metadata/2/
@app.route('/articles/metadata/<int:num>/', methods=['GET'])
def retrieve_metadata(num):
    
    articles = dbf.query_db("SELECT * FROM articles ORDER BY article_id DESC LIMIT (?)", [num])

    # will hold all articles 
    articles_msg = []

    if request.method == 'GET' and articles is not None:
        for article in articles:
            articles_msg.append(
                {
                    "author": article['author'],
                    "title": article['title'],
                    "content": article['content'],
                    "date_published": article['date_published'],
                    "url": "http:localhost/articles/retrieve_metadata/" + str(article['article_id'])
                }   
            )
        
        resp = jsonify(articles_msg)
        resp.status_code = 200
        # Not sure if this is correct, we can only add one response header
        resp.headers['Last-Modified'] = str(datetime.strptime(articles[0]['last_modified'], "%Y-%m-%d %H:%M:%f"))
        return resp
    elif articles is None:
        return not_found()

