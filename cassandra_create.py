from cassandra.cluster import Cluster
from passlib.hash import sha256_crypt

cluster = Cluster(['172.17.0.2'])
session = cluster.connect()

# Creates keyspace using CQL command 
# Had trouble with syntax used this for reference https://github.com/datastax/python-driver/blob/master/example_core.py
session.execute("""
        CREATE KEYSPACE IF NOT EXISTS %s
        WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '1' }
        """ % "testkeyspace",)

session.execute('USE testkeyspace')

# Couldnt find way for cassandra to increment starting from one 
# Used this reference for UUID https://docs.datastax.com/en/cql/3.3/cql/cql_reference/timeuuid_functions_r.html
session.execute(
    """CREATE TABLE IF NOT EXISTS testkeyspace.articles(
        article_id uuid,
        author text,
        title text,
        content text,
        date_published timestamp,
        last_modified timestamp,
        PRIMARY KEY ((article_id), date_published)
    ) WITH CLUSTERING ORDER BY (date_published DESC)"""
)

session.execute(
    """CREATE TABLE IF NOT EXISTS testkeyspace.comments(
        comment_id uuid,
        article_url text,
        author text,
        date_published timestamp,
        comment text,
        PRIMARY KEY ((comment_id), date_published)
    ) WITH CLUSTERING ORDER BY (date_published DESC)"""
)

session.execute(
    """CREATE TABLE IF NOT EXISTS testkeyspace.tags(
        tag_id uuid PRIMARY KEY,
        article_url text,
        tag_name text,
    )"""
)

session.execute(
    """CREATE TABLE IF NOT EXISTS testkeyspace.users(
        user_id uuid PRIMARY KEY,
        name text,
        username text,
        email text,
        password text,
    )"""
)

# user
password = "password"
hashed_pw = sha256_crypt.encrypt(password)

session.execute(
    """INSERT INTO users(
        user_id, 
        name, 
        username,
        email,
        password
        ) VALUES (
            uuid(),
            'email',
            'email', 
            'email@yahoo.com', 
            """ + str(hashed_pw) + """
    );"""
)


#Referenced used for inserting https://docs.datastax.com/en/cql/3.3/cql/cql_reference/cqlInsert.html
#Inserting Articles: 

session.execute(
    """INSERT INTO articles(
        79f0e9a7-e428-4041-bba1-7fc04a654256, 
        author, 
        title,
        content,
        date_published,
        last_modified
        ) VALUES (
            uuid(),
            'Email',
            'blog 1', 
            'content', 
            'toTimeStamp(now())',
            'toTimeStamp(now())'
    );"""
)

session.execute(
    """INSERT INTO articles(
        article_id, 
        author, 
        title,
        content,
        date_published,
        last_modified
        ) VALUES (
            uuid(),
            'Email',
            'blog 2', 
            'content', 
            'toTimeStamp(now())',
            'toTimeStamp(now())'
    );"""
)

session.execute(
    """INSERT INTO articles(
        article_id, 
        author, 
        title,
        content,
        date_published,
        last_modified
        ) VALUES (
            uuid(),
            'Email',
            'blog 3', 
            'content', 
            'toTimeStamp(now())',
            'toTimeStamp(now())'
    );"""
)

session.execute(
    """INSERT INTO articles(
        article_id, 
        author, 
        title,
        content,
        date_published,
        last_modified
        ) VALUES (
            uuid(),
            'Email',
            'blog 4', 
            'content', 
            'toTimeStamp(now())',
            'toTimeStamp(now())'
    );"""
)

session.execute(
    """INSERT INTO articles(
        article_id, 
        author, 
        title,
        content,
        date_published,
        last_modified
        ) VALUES (
            uuid(),
            'Email',
            'blog 5', 
            'content', 
            'toTimeStamp(now())',
            'toTimeStamp(now())'
    );"""
)


#Inster Comments:

session.execute(
    """INSERT INTO comments(
        comment_id, 
        article_url,
        author,
        date_published,
        comment
        ) VALUES (
            uuid(),
            'Email',
            'http://localhost/articles/79f0e9a7-e428-4041-bba1-7fc04a654256', 
            'comment', 
            'toTimeStamp(now())',
            'toTimeStamp(now())'
    );"""
)

session.execute(
    """INSERT INTO comments(
        comment_id, 
        article_url,
        author,
        date_published,
        comment
        ) VALUES (
            uuid(),
            'Email',
            'http://localhost/articles/79f0e9a7-e428-4041-bba1-7fc04a654256', 
            'comment', 
            'toTimeStamp(now())',
            'toTimeStamp(now())'
    );"""
)
session.execute(
    """INSERT INTO comments(
        comment_id, 
        article_url,
        author,
        date_published,
        comment
        ) VALUES (
            uuid(),
            'Email',
            'http://localhost/articles/79f0e9a7-e428-4041-bba1-7fc04a654256', 
            'comment', 
            'toTimeStamp(now())',
            'toTimeStamp(now())'
    );"""
)
session.execute(
    """INSERT INTO comments(
        comment_id, 
        article_url,
        author,
        date_published,
        comment
        ) VALUES (
            uuid(),
            'Email',
            'http://localhost/articles/79f0e9a7-e428-4041-bba1-7fc04a654256', 
            'comment', 
            'toTimeStamp(now())',
            'toTimeStamp(now())'
    );"""
)
session.execute(
    """INSERT INTO comments(
        comment_id, 
        article_url,
        author,
        date_published,
        comment
        ) VALUES (
            uuid(),
            'Email',
            'http://localhost/articles/79f0e9a7-e428-4041-bba1-7fc04a654256', 
            'comment', 
            'toTimeStamp(now())',
            'toTimeStamp(now())'
    );"""
)
session.execute(
    """INSERT INTO comments(
        comment_id, 
        article_url,
        author,
        date_published,
        comment
        ) VALUES (
            uuid(),
            'Email',
            'http://localhost/articles/79f0e9a7-e428-4041-bba1-7fc04a654256', 
            'comment', 
            'toTimeStamp(now())',
            'toTimeStamp(now())'
    );"""
)

# tags
session.execute(
    """INSERT INTO comments(
        tag_id,
        article_url,
        tag_name
        ) VALUES (
            uuid(),
            'http://localhost/articles/79f0e9a7-e428-4041-bba1-7fc04a654256',
            'tag1'
    );"""
)
session.execute(
    """INSERT INTO comments(
        tag_id,
        article_url,
        tag_name
        ) VALUES (
            uuid(),
            'http://localhost/articles/79f0e9a7-e428-4041-bba1-7fc04a654256',
            'tag2'
    );"""
)
session.execute(
    """INSERT INTO comments(
        tag_id,
        article_url,
        tag_name
        ) VALUES (
            uuid(),
            'http://localhost/articles/79f0e9a7-e428-4041-bba1-7fc04a654256',
            'tag3'
    );"""
)
session.execute(
    """INSERT INTO comments(
        tag_id,
        article_url,
        tag_name
        ) VALUES (
            uuid(),
            'http://localhost/articles/79f0e9a7-e428-4041-bba1-7fc04a654256',
            'tag4'
    );"""
)
session.execute(
    """INSERT INTO comments(
        tag_id,
        article_url,
        tag_name
        ) VALUES (
            uuid(),
            'http://localhost/articles/79f0e9a7-e428-4041-bba1-7fc04a654256',
            'tag5'
    );"""
)