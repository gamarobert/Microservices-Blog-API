from flask import Flask
from flask import request, g, json, jsonify
from basicauth import SubBasicAuth
from datetime import datetime
import sqlite3
import sys
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

@app.route('/articles')
def root():
    return "testing testing..."

# curl -i --header 'Content-Type: application/json' http://localhost/articles/66394710-9d34-4418-875f-804083cf849d/
@app.route('/articles/<id>/', methods=['GET'])
def article(id):
    
    articles = session.execute("SELECT * FROM testkeyspace.articles WHERE article_id =" + str(id))
  
    # Datatype: String
    lastmod_str = datetime.strftime(articles[0].last_modified,"%a, %d %b %Y %I:%M:%S GMT") 
    
    # Datatype: Date
    lastmod_date = datetime.strptime(str(lastmod_str), "%a, %d %b %Y %I:%M:%S GMT")
    
    # Example: Mon, 05 Oct 2015 07:28:00 GMT

    if request.method == 'GET':
        if articles is not None:
            message = {
                    "article": articles[0].title
                    }
            resp = jsonify(message)
            resp.status_code = 200
            resp.headers['Last-Modified'] = lastmod_str

            if request.headers.get("If-Modified-Since") is not None:
                if request.if_modified_since < lastmod_date:
                    return resp
                else:
                    resp.status_code = 304
                    return resp      
            else:
                return resp                  
        else:
            return not_found()

# curl --include --verbose --request POST --header 'Content-Type: application/json' --user "email" --data '{"title":"Testing Title","content":"TESTINGGG"}' http://localhost/articles/new_article/
@app.route('/articles/new_article/' , methods=['POST'])
# @basic_auth.required
def new_article():
    
    if request.method == 'POST':
        
        auth = request.authorization
        
        title = request.json['title']
        content = request.json['content']

        stmt = session.prepare("INSERT INTO articles (article_id, author, content, date_published, last_modified, title) VALUES (uuid(), ?, ?, toTimeStamp(now()), toTimeStamp(now()), ?)")
        session.execute(stmt, (auth.username, content, title))

        message = { 'message': 'Article created!'}
        resp = jsonify(message)
        resp.status_code = 201
        return resp


# # curl --include --header 'Content-Type: application/json' --user "email" --data '{"title": "Changed title", "content": "edited content"}' http://localhost/articles/edit_article/6d922c24-cdaf-49b6-8110-edc0c33263c8/
@app.route('/articles/edit_article/<id>/', methods=['POST'])
# @basic_auth.required
def edit_article(id):

    article = session.execute("SELECT * FROM articles WHERE article_id=" + str(id))

    if request.method == 'POST' and article[0] is not None:

        title = request.json['title']
        content = request.json['content']
        date_published = article[0].date_published
        stmt = session.prepare("UPDATE testkeyspace.articles SET content=?, last_modified=toTimeStamp(now()), title=? WHERE article_id=" + str(id) + " AND date_published=?")
        
        session.execute(stmt, [content, title, date_published])

        message = { 'message': 'Article updated!' }
        resp = jsonify(message)
        resp.status_code = 201

        return resp
    elif article is None:
        return not_found()  

# # curl --include --header 'Content-Type: application/json' -X DELETE --user "email" http://localhost/articles/delete_article/ea75f9da-198d-4c9a-8909-8197ee6f5ea8/
@app.route('/articles/delete_article/<id>/', methods=['DELETE'])
def delete_article(id):
    
    found_article = session.execute("SELECT * FROM testkeyspace.articles WHERE article_id ="+str(id))
    
    if request.method == 'DELETE' and found_article[0].article_id is not None:   
        
        session.execute("DELETE FROM testkeyspace.articles WHERE article_id ="+str(id))
    
        message = {
            'message': 'Article successfully deleted.'
        }
        resp = jsonify(message)

        return resp
    elif found_article is None:
        return not_found()
 
# curl --include --verbose --header 'Content-Type: application/json' http://localhost/articles/retrieve_articles/3/
@app.route('/articles/retrieve_articles/<int:num>/', methods=['GET'])
def retrieve_articles(num):
    
    articles = session.execute("SELECT * FROM testkeyspace.articles LIMIT "+ str(num))

    # Store last modified as string from  lastest article in articles 
    lastmod_str = datetime.strftime(articles[0].last_modified,"%a, %d %b %Y %I:%M:%S GMT")
    
    # Store last modified as date type from  lastest article in articles 
    lastmod_date = datetime.strptime(str(lastmod_str), "%a, %d %b %Y %I:%M:%S GMT")

    articles_msg = []

    if request.method == 'GET':
        if articles is not None:
            for article in articles:
                articles_msg.append(
                    {
                        "article_id": article.article_id,
                        "author": article.author,
                        "title": article.title,
                        "content": article.content,
                        "date_published": article.date_published,
                        "last_modified": article.last_modified
                    }   
                )
            
            resp = jsonify(articles_msg)
            resp.status_code = 200
            resp.headers['Last-Modified'] = lastmod_str
            
            if request.headers.get("If-Modified-Since") is not None:
                if request.if_modified_since < lastmod_date:
                    return resp
                else:
                    resp.status_code = 304
                    return resp            
            return resp
        else:
            return not_found()

# #  curl -i --header 'Content-Type: application/json' http://localhost/articles/metadata/2/
@app.route('/articles/metadata/<int:num>/', methods=['GET'])
def retrieve_metadata(num):

    articles = session.execute("SELECT * FROM testkeyspace.articles LIMIT "+ str(num))

    # Store last modified as string from  lastest article in articles 
    lastmod_str = datetime.strftime(articles[0].last_modified,"%a, %d %b %Y %I:%M:%S GMT")
    
    # Store last modified as date type from  lastest article in articles 
    lastmod_date = datetime.strptime(str(lastmod_str), "%a, %d %b %Y %I:%M:%S GMT")


    articles_msg = []

    if request.method == 'GET':
        if articles is not None:
            for article in articles:
                articles_msg.append(
                    {
                        "author": article.author,
                        "title": article.title,
                        "content": article.content,
                        "date_published": article.date_published,
                        "url": "http:localhost/articles/retrieve_metadata/" + str(article.article_id)
                    }   
                )
                
            resp = jsonify(articles_msg)
            resp.status_code = 200
            resp.headers['Last-Modified'] = lastmod_str
            
            if request.headers.get("If-Modified-Since") is not None:
                if request.if_modified_since < lastmod_date:
                    return resp
                else:
                    resp.status_code = 304
                    return resp
            else:
                return resp
        else:
            return not_found()
