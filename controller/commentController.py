from functools import wraps
import mysql.connector
from flask import Blueprint
from flask import request, jsonify
import pdb
from datetime import datetime
from sql_address import sql_address

comment_bp = Blueprint('comment', __name__, url_prefix="/api")
prefix = "/comment"

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

@comment_bp.route(prefix + '/post', methods=['POST'])
@ensure_connection
def post_comment(conn):
    with conn.cursor() as cur:
        body = request.json
        body['has_parent'] = False
        body['like_count'] = 0
        cur.execute("INSERT INTO comment (post_id, user_id, content, has_parent, like_count) VALUES (%(postId)s, %(userId)s, %(content)s, %(has_parent)s, %(like_count)s)", body)
        cur.execute("UPDATE post SET comment_count = comment_count + 1 WHERE id = %(postId)s", body)
        return "200"
    
@comment_bp.route(prefix + '/comment', methods=['POST'])
@ensure_connection
def comment_comment(conn):
    with conn.cursor() as cur:
        body = request.json
        body['has_parent'] = True
        body['like_count'] = 0
        body['comment_count'] = 0
        cur.execute("INSERT INTO comment (post_id, user_id, content, has_parent, like_count, parent_id, comment_count) VALUES (%(postId)s, %(userId)s, %(content)s, %(has_parent)s, %(like_count)s, %(parentId)s, %(comment_count)s)", body)
        
        return "200"
    
@comment_bp.route(prefix + '/<post_id>', methods=['GET'])
@ensure_connection
def get_comments(conn, post_id):
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM comment WHERE post_id = %s", (post_id,))
        comments = cur.fetchall()
        comment_tree = []

        # Create a dictionary to map comment IDs to their corresponding comments
        comment_dict = {comment["id"]: comment for comment in comments}

        for comment in comments:
            if not comment["has_parent"]:
                # If comment doesn't have a parent, it's a root comment
                comment_tree.append(comment)
            else:
                # If comment has a parent, add it to its parent's 'replies' list
                parent_id = comment["parent_id"]
                parent_comment = comment_dict[parent_id]
                if "replies" not in parent_comment:
                    parent_comment["replies"] = []
                parent_comment["replies"].append(comment)

        return comment_tree
    
@comment_bp.route(prefix + '/like', methods=['POST'])
@ensure_connection
def like_comment(conn):
    with conn.cursor() as cur:
        body = request.json
        cur.execute("UPDATE comment SET like_count = like_count + 1 WHERE id = %(commentId)s", body)
        cur.execute("INSERT INTO liked (comment_id, user_id) VALUES (%(commentId)s, %(userId)s)")
        return "200"

@comment_bp.route(prefix + '/unlike', methods=['POST'])
@ensure_connection
def unlike_comment(conn):
    with conn.cursor() as cur:
        body = request.json
        cur.execute("UPDATE comment SET like_count = like_count - 1 WHERE id = %(commentId)s", body)
        cur.execute("DELETE FROM liked WHERE comment_id = %(commentId)s AND user_id = %(userId)s")
        return "200"