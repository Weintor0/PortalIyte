from functools import wraps
import mysql.connector
from flask import Blueprint
from flask import request, jsonify
import pdb
from datetime import datetime
from sql_address import sql_address


user_bp = Blueprint('user', __name__, url_prefix="/api")
prefix = "/user"

# Connect to the MySQL database
conn = mysql.connector.connect(
    host=sql_address,
    user='portal',
    password='portal',
    database='portal_base',
    autocommit=True,
    ssl_disabled=True  # Disable SSL
)

def ensure_connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            conn.ping(reconnect=True)
        except mysql.connector.Error:
            conn.reconnect()
        return func(conn, *args, **kwargs)
    return wrapper

@user_bp.route(prefix + '/login', methods=["GET"])
@ensure_connection
def login(conn):
    with conn.cursor() as cur:
        body = request.json
        cur.execute("SELECT * FROM user")
        rows = cur.fetchall()
        for row in rows:
            if(row[2] == body['phoneNumber'] and row[3] == body['password']):
                return "200"
        return "401"
    
@user_bp.route(prefix + '/register', methods=["POST"])
@ensure_connection
def register(conn):
    with conn.cursor() as cur:
        body = request.json
        cur.execute("INSERT INTO user (email, phone_number, password, username, follower_count, following_count, post_count) VALUES (%(email)s, %(phoneNumber)s, %(password)s, %(username)s,0,0,0)", body)
        user_id = cur.lastrowid
        return jsonify({"id": user_id}), 200

@user_bp.route(prefix + '/<user_id>', methods=["GET"])
@ensure_connection
def get_user(conn, user_id):
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM user WHERE id = %s", [user_id])
        row  = cur.fetchone()
        response = {"id": row["id"], "email": row["email"], "phoneNumber": row["phone_number"], "username": row["username"], "bio": row["bio"], "profilePicture": row["profile_picture"], "createTime": row["create_date"], "postCount": row["post_count"], "followerCount": row["follower_count"], "followingCount": row["following_count"]}
        return jsonify(response), 200

@user_bp.route(prefix + '/setBio', methods=["PUT"])
@ensure_connection
def set_bio(conn):
    with conn.cursor() as cur:
        body = request.json
        cur.execute("UPDATE user SET bio = %(bio)s WHERE id = %(userId)s", body)
        return "200"
    
@user_bp.route(prefix + '/setProfilePicture', methods=["PUT"])
@ensure_connection
def set_profile_picture(conn):
    with conn.cursor() as cur:
        body = request.json
        cur.execute("UPDATE user SET profile_picture = %(profilePicture)s WHERE id = %(userId)s", body)
        return "200"
