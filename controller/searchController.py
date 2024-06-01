from functools import wraps
import mysql.connector
from flask import Blueprint
from flask import request, jsonify
import pdb
from datetime import datetime
from sql_address import sql_address
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

def ensure_connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            conn.ping(reconnect=True)
        except mysql.connector.Error:
            conn.reconnect()
        return func(conn, *args, **kwargs)
    return wrapper

@search_bp.route(prefix + '/user/<query>', methods=['GET'])
@ensure_connection
def search_user(conn, query):
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM user")
        rows = cur.fetchall()
        response = []
        for row in rows:
            if(jellyfish.jaro_similarity(row["username"], query) > 0.8):
                response.append({"id": row["id"], "email": row["email"], "phoneNumber": row["phone_number"], "username": row["username"], "bio": row["bio"], "profilePicture": row["profile_picture"], "createTime": row["create_date"], "postCount": row["post_count"], "followerCount": row["follower_count"], "followingCount": row["following_count"], "commentCount": row["comment_count"]})
            return jsonify(response)