from functools import wraps
import mysql.connector
from flask import Blueprint
from flask import request, jsonify
import pdb
from datetime import datetime
from endpoints import sql_address
import jellyfish

search_bp = Blueprint('search', __name__, url_prefix="/api")
prefix = "/search"

# Connect to the MySQL database
conn = mysql.connector.connect(
    host=sql_address,
    user='portal',
    password='portal',
    database='portal_base',
    autocommit=True,
    ssl_disabled=True  # Disable SSL
)

similarity_threshold = 0.7

def ensure_connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            conn.ping(reconnect=True)
        except mysql.connector.Error:
            conn.reconnect()
        return func(conn, *args, **kwargs)
    return wrapper

@search_bp.route(prefix + '/post/<query>', methods=['GET'])
@ensure_connection
def search_post(conn, query):
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM post")
        rows = cur.fetchall()
        response = []
        for row in rows:
            if(jellyfish.jaro_similarity(row["title"], query) > similarity_threshold):
                response.append({"id": row["id"], "userId": row["user_id"], "title": row["title"], "content": row["content"], "image": row["image"], "likeCount": row["like_count"], "commentCount": row["comment_count"], "createDate": row["create_date"]})
            return jsonify(response)

@search_bp.route(prefix + '/topic/<query>', methods=['GET'])
@ensure_connection
def search_topic(conn, query):
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM topic")
        rows = cur.fetchall()
        response = []
        for row in rows:
            if(jellyfish.jaro_similarity(row["name"], query) > similarity_threshold):
                response.append({"id": row["id"], "name": row["name"], "description": row["description"], "logo": row["logo"]})
            return jsonify(response)

@search_bp.route(prefix + '/user/<query>', methods=['GET'])
@ensure_connection
def search_user(conn, query):
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM user")
        rows = cur.fetchall()
        response = []
        for row in rows:
            if(jellyfish.jaro_similarity(row["username"], query) > similarity_threshold):
                response.append({"id": row["id"], "email": row["email"], "phoneNumber": row["phone_number"], "username": row["username"], "bio": row["bio"], "profilePicture": row["profile_picture"], "createTime": row["create_date"], "postCount": row["post_count"], "followerCount": row["follower_count"], "followingCount": row["following_count"]})
            return jsonify(response)