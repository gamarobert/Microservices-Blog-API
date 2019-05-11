from flask import Flask
from flask import request, url_for, g, json, jsonify
from basicauth import SubBasicAuth
from passlib.hash import sha256_crypt
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

@app.errorhandler(409)
def db_error(error=None):
    message = {
        'status': 409,
        'message': 'Database error: ' + request.url
    }

    resp = jsonify(message)
    resp.status_code = 409

    return resp

@app.route('/')
def root():
    pass

@app.route('/auth', methods=['GET'])
@basic_auth.required
def authenticate():
    message = { 'status': 'OK' }

    resp = jsonify(message)
    resp.status_code = 200
                
    return resp


#curl --include --verbose --request POST --header 'Content-Type: application/json' --data '{"name":"name", "email":"email", "password":"password"}' http://localhost:5000/users/register_user/
@app.route('/users/register_user/' , methods=['POST'])
def register():
    
    name = request.json['name']
    email = request.json['email']
    password = request.json['password']
    username = email.split('@')
    
    # assigns text infront of '@' as username
    username = username[0]
    
    # hashing of password
    hashed_pw = sha256_crypt.encrypt(password)

    if request.method == 'POST':
        
        stmt = session.prepare("INSERT INTO testkeyspace.users (user_id, name, username, email, password) VALUES (uuid(), ?, ?, ?, ?)")
        query = session.execute(stmt, ( name, username, email, hashed_pw))

        message = {
            'message': 'User successfully created!'
        }

        resp = jsonify(message)
        resp.status_code = 201

        return resp
        

# # curl --include --verbose --request DELETE --user "username" --header 'Content-Type: application/json'  http://localhost:5000/users/delete_user/<int:uid>/
@app.route('/users/delete_user/<uid>/', methods=['DELETE'])

def delete_user(uid):

    if request.method == 'DELETE':
        
        delete_row = session.execute("DELETE FROM testkeyspace.users WHERE user_id = " + str(uid))

        message = {
            'message': 'successfully deleted.'
        }

        resp = jsonify(message)
        resp.status_code = 200
        
        return resp
    
    elif user is None:
        return db_error()
    

# # curl --include --verbose --header 'Content-Type: application/json' --user "username" --data '{"password": "editedpassword"}' http://localhost:5000/users/edit_password/<int:uid>/
# @app.route('/users/edit_password/<int:uid>/', methods=['POST'])
# # @basic_auth.required
# def edit_password(uid):

#     user = dbf.query_db("SELECT * FROM users WHERE uid=?", [uid], one=True)

#     if user is not None:

#         password = request.json['password']
#         hashed_pw = sha256_crypt.encrypt(password)

#         if request.method == 'POST':
#             cur = dbf.get_db().cursor()
#             db = dbf.get_db()

#             cur.execute("UPDATE users SET password=? WHERE uid=?", 
#                         (hashed_pw, uid))
#             db.commit()
#             cur.close()

#             message = {
#                 'message': 'Password updated!'
#             }

#             resp = jsonify(message)
#             resp.status_code = 201

#             return resp

#     elif user is None:
#             return not_found()

