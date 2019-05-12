# Juan Carrera Dev 1



from cassandra.cluster import Cluster



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
        PRIMARY KEY (article_id, last_modified)
    ) WITH CLUSTERING ORDER BY (last_modifed DESC)"""
)

session.execute(
    """CREATE TABLE IF NOT EXISTS testkeyspace.comments(
        comment_id uuid PRIMARY KEY,
        article_url text,
        author text,
        date_published timestamp,
        comment text
    )"""
)

# session.execute(
#     """CREATE TABLE IF NOT EXISTS testkeyspace.tags(
#         tag_id uuid PRIMARY KEY,
#         article_url text,
#         tag_name text,
#     )"""
# )

# session.execute(
#     """CREATE TABLE IF NOT EXISTS testkeyspace.users(
#         user_id uuid PRIMARY KEY,
#         name text,
#         username text,
#         email text,
#         password text,
#     )"""
# )

# #Referenced used for inserting https://docs.datastax.com/en/cql/3.3/cql/cql_reference/cqlInsert.html
# #Inserting Articles: 

# session.execute(
#     """INSERT INTO articles(
#         article_id, 
#         author, 
#         title,
#         content,
#         date_published,
#         last_modified
#         ) VALUES (
#             uuid(),
#             'John',
#             'blog 1', 
#             'foo booso isbos so', 
#             '2019-03-12 04:53:16',
#             '2019-04-19 04:53:16'
#     );"""
# )

# session.execute(
#     """INSERT INTO articles(
#         article_id, 
#         author, 
#         title,
#         content,
#         date_published,
#         last_modified
#         ) VALUES (
#             uuid(),
#             'Juan',
#             'blogger blog', 
#             'foo booso isbos so', 
#             '2019-03-12 04:53:16',
#             '2019-04-19 04:53:16'
#     );"""
# )

# session.execute(
#     """INSERT INTO articles(
#         article_id, 
#         author, 
#         title,
#         content,
#         date_published,
#         last_modified
#         ) VALUES (
#             uuid(),
#             'Robert',
#             'i am cool heres why', 
#             'foo booso isbos so', 
#             '2019-03-12 04:53:16',
#             '2019-04-19 04:53:16'
#     );"""
# )

# #Inster Comments:

# session.execute(
#     """INSERT INTO comments(
#         comment_id, 
#         article_url,
#         author,
#         date_published,
#         comment
#         ) VALUES (
#             uuid(),
#             'Robert',
#             'http://localhost/articles/79f0e9a7-e428-4041-bba1-7fc04a654256', 
#             'foo booso isbos so', 
#             '2019-03-12 04:53:16',
#             '2019-04-19 04:53:16'
#     );"""
# )



