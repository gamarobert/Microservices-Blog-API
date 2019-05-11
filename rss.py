from flask import Flask
import requests
from cachecontrol import CacheControl
from rfeed import *
import datetime

app = Flask(__name__)

@app.route('/')
def root():
    pass

@app.route('/rss/summary', methods=['GET'])
def summary():

    # 
    sess = requests.session()
    cached_sess = CacheControl(sess)

    response = cached_sess.get('http://localhost/articles/retrieve_articles/10/', auth=('email', 'password'))
    articles = response.json()
    # 
    # r_articles = requests.get('http://localhost/articles/retrieve_articles/10/', auth=('email', 'password'))
    # articles = r_articles.json()

    items = []
    # if r_articles.status_code == 200:
    if response.status_code == 200:
        for article in articles:
            items.append(
                Item(
                    title = article['title'],
                    link = "http://localhost/articles/" + str(article['article_id']),
                    author = article['author'],
                    pubDate = datetime.datetime.strptime(article['date_published'], "%Y-%m-%d %H:%M:%f")
                ))
                 
        feed = Feed(
            title = "Summary RSS Feed",
            link = "http://localhost/rss/summary",
            description = "This feed shows a summary of the 10 most recent articles",
            language = "en-US",
            lastBuildDate = datetime.datetime.now(),
            items = items
        )
        return feed.rss()
    else:
        # print(str(r_articles.status_code), file=sys.stderr)
        print(str(response.status_code), file=sys.stderr)
        return "articles error"
    

# A full feed containing the full text for each article, its tags as RSS categories, and a comment count.

@app.route('/rss/full', methods=['GET'])
def full():
    r_articles = requests.get('http://localhost/articles/retrieve_articles/10/', auth=('email', 'password'))
   
    items = []
    if r_articles.status_code == 200:
        articles = r_articles.json()
        for article in articles:
            r_comments = requests.get('http://localhost/comments/count/' + str(article['article_id']), auth=('email', 'password'))
            
            # not sure why its 201 yet, hmm
            if r_comments.status_code == 200:
                commentCount = r_comments.json()
            else:
                print(str(r_comments.status_code), file=sys.stderr)
                return "comments error"

            r_tags = requests.get('http://localhost/tags/all/' + str(article['article_id']), auth=('email', 'password'))
            
            if r_tags.status_code == 200:
                allTags = r_tags.json()

                tags_arr = []
                for tag in allTags:
                    tags_arr.append(
                        tag['tag']
                    )
            else:
                print(str(r_tags.status_code), file=sys.stderr)
                return "tags error"

            items.append(
                Item(
                    title = article['article_id'],
                    author = article['author'],
                    description = article['content'],
                    categories = tags_arr,
                    comments = commentCount['numOfComments']
                ))
        
        feed = Feed(
            title = "Full RSS Feed",
            link = "http://localhost/rss/full",
            description = "This feed shows a full content for 10 articles",
            language = "en-US",
            lastBuildDate = datetime.datetime.now(),
            items = items
        )
        return feed.rss()

    else:
        print(str(r_articles.status_code), file=sys.stderr)
        return "articles error"

@app.route('/rss/comments', methods=['GET'])
def comments():
    
    r_articles = requests.get('http://localhost/articles/retrieve_articles/10/' , auth=('email', 'password'))
       
    if r_articles.status_code == 200:
        articles = r_articles.json()

        items = [] 
        for article in articles:
            r_comments = requests.get('http://localhost/comments/recent/' + str(article['article_id']) + '/10', auth=('email', 'password'))
            
            if r_comments.status_code == 200:
                comments = r_comments.json()
                all_comments = []
                for comment in comments:
                    all_comments.append(
                        comment['comment']
                    )
            else:
                print(str(r_comments.status_code), file=sys.stderr)
                return "comments error"

            items.append(
                Item(
                    title = article['title'],
                    pubDate = datetime.datetime.strptime(article['date_published'], "%Y-%m-%d %H:%M:%f"),
                    description =  all_comments
                ))
        feed = Feed(
            title = "Comments feed for articles",
            link = "http://localhost/rss/comments",
            description = "This feed shows comments for each article.",
            language = "en-US",
            lastBuildDate = datetime.datetime.now(),
            items = items
        )
        return feed.rss()
    else:
        print(str(r_articles.status_code), file=sys.stderr)
