from functools import wraps
import mysql.connector
from flask import Blueprint
from flask import request, jsonify,send_file
import pdb
from datetime import datetime


user_bp = Blueprint('user', __name__, url_prefix="/api")
prefix = "/user"

# Connect to the MySQL database
conn = mysql.connector.connect(
    host='127.0.0.1',
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
        cur.execute("INSERT INTO user (email, phone_number, password, username) VALUES (%(email)s, %(phoneNumber)s, %(password)s, %(username)s)", body)
        return "200"

@user_bp.route(prefix + '/<user_id>', methods=["GET"])
@ensure_connection
def get_user(conn, user_id):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM user WHERE id = %s", [user_id])
        return cur.fetchone()

@user_bp.route(prefix, methods=["PUT"])
@ensure_connection
def set_bio(conn):
    with conn.cursor() as cur:
        body = request.json
        cur.execute("UPDATE user SET bio = %(bio)s WHERE id = %(user_id)s", body)
        return "200"
    
@user_bp.route(prefix + '/<user_id>/profile_picture', methods=["PUT"])
@ensure_connection
def set_profile_picture(conn, user_id, profile_picture):
    with conn.cursor() as cur:
        cur.execute("UPDATE user SET profile_picture = %s WHERE id = %s", [profile_picture, user_id])
        return "200"

""""
@sql_bp.route(prefix + '/getWaylineFiles')
@ensure_connection
def get_wayline_files(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM wayline_file")
        rows = cur.fetchall()
        records = []
        column_names = [desc[0] for desc in cur.description]  # Get column names
        for row in rows:
            record_dict = {}
            for i in range(len(column_names)):
                if column_names[i] in ['id', 'name', "create_time", "update_time", "wayline_id", "template_types"]:
                    if column_names[i] in ["create_time", "update_time"]:
                        seconds_since_epoch = row[i] / 1000
                        dt = datetime.fromtimestamp(seconds_since_epoch)
                        formatted_datetime = dt.strftime('%d-%m-%Y %H:%M')
                        print(formatted_datetime)
                        record_dict[column_names[i]] = formatted_datetime
                    else:
                        record_dict[column_names[i]] = row[i]
            records.append(record_dict)
    return jsonify({'waylinefiles': records}), 200

@sql_bp.route(prefix + '/deleteWaylineFile/<wayline_file_id>', methods=["DELETE"])
@ensure_connection
def delete_wayline_file(conn,wayline_file_id):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM wayline_file WHERE id = %s", [wayline_file_id])
    return "200"

@sql_bp.route(prefix + '/saveAIJob', methods=["POST"])
@ensure_connection
def save_ai_jobs(conn):
    data = request.json
    with conn.cursor() as cur:
        cur.execute("INSERT INTO AI_jobs (job_name, job_description, status, process, wayline_job_id, AI_model_id, user_id) VALUES (%(job_name)s, %(job_description)s, 'ongoing', '0% - in progress', %(wayline_job_id)s, %(AI_model_id)s, 1)", data)
    return "200"

@sql_bp.route(prefix + '/getJobIDFromAIJobID/<ai_job_id>')
@ensure_connection
def get_job_id_from_ai_job_id(conn,ai_job_id):
    with conn.cursor() as cur:
        cur.execute("SELECT wayline_job_id FROM AI_jobs WHERE AI_jobs.id = %s", [ai_job_id])
        rows = cur.fetchall()
        response = rows[0][0]
    return jsonify({'job_id': response}),200

@sql_bp.route(prefix + '/getAIJobs', methods=["GET"])
@ensure_connection
def get_ai_jobs(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT AI_jobs.id, AI_model.model_name, wayline_job.name, AI_jobs.process, AI_jobs.status FROM AI_jobs, AI_model, wayline_job WHERE AI_jobs.AI_model_id = AI_model.id AND AI_jobs.wayline_job_id = wayline_job.job_id")
        rows = cur.fetchall()
        response = {"aiJobs": []}
        for row in rows:
            response["aiJobs"].append(row)
    return jsonify(response), 200

@sql_bp.route(prefix + '/getAIJob/<ai_job_id>', methods=["GET"])
@ensure_connection
def get_ai_job(conn,ai_job_id):
    with conn.cursor() as cur:
        cur.execute("SELECT AI_jobs.job_name, AI_model.model_name, wayline_job.name, AI_jobs.process, AI_jobs.status, AI_jobs.create_date, AI_jobs.finish_date FROM AI_jobs, AI_model, wayline_job WHERE AI_jobs.AI_model_id = AI_model.id AND AI_jobs.wayline_job_id = wayline_job.job_id AND AI_jobs.id = %s", [ai_job_id])
        rows = cur.fetchall()
        response = {"aiJob": rows[0]}
    return jsonify(response), 200

@sql_bp.route(prefix + '/deleteAIJob/<job_id>', methods=["DELETE"])
@ensure_connection
def delete_ai_job(conn,job_id):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM AI_jobs WHERE id = %s", [job_id])
    return "200"

@sql_bp.route(prefix + '/getAIJobResults/<job_id>', methods=["GET"])
@ensure_connection
def get_ai_job_results(conn,job_id):
    with conn.cursor() as cur:
        cur.execute("SELECT img_oss_path, result FROM AI_job_result WHERE AI_job_id = %s", [job_id])
        rows = cur.fetchall()
        response = {}
        for row in rows:
            response[row[0]] = row[1]
    return jsonify(response), 200

@sql_bp.route(prefix + '/getAIModelIDNames', methods=["GET"])
@ensure_connection
def get_ai_models(conn):
    with conn.cursor() as cur:
        response = {"ids": [], "names": []}
        cur.execute("SELECT id, model_name FROM AI_model")
        rows = cur.fetchall()
        for row in rows:
            response["ids"].append(row[0])
            response["names"].append(row[1])
    return jsonify(response), 200

@sql_bp.route(prefix + '/getModelName/<ai_model_id>', methods=["GET"])
@ensure_connection
def get_model_name(conn,ai_model_id):
    with conn.cursor() as cur:
        cur.execute("SELECT model_name FROM AI_model WHERE id = %s", [ai_model_id])
        rows = cur.fetchall()
        response = rows[0][0]
    return jsonify({'modelName': response})

@sql_bp.route(prefix + '/getWaylineJobIDNames', methods=["GET"])
@ensure_connection
def get_wayline_job_id_names(conn):
    with conn.cursor() as cur:
        response = {"ids": [], "names": []}
        cur.execute("SELECT job_id, name FROM wayline_job")
        rows = cur.fetchall()
        for row in rows:
            response["ids"].append(row[0])
            response["names"].append(row[1])
    return jsonify(response), 200

@sql_bp.route(prefix + '/getWaylineJobMediaCount/<wayline_job_id>', methods=["GET"])
@ensure_connection
def get_wayline_job_media_count(conn,wayline_job_id):
    with conn.cursor() as cur:
        response = {"mediaCount": 0}
        cur.execute("SELECT media_count FROM wayline_job WHERE job_id = %s", [wayline_job_id])
        rows = cur.fetchall()
        response["mediaCount"] = rows[0]
    return jsonify(response), 200

@sql_bp.route(prefix + '/getWaylineJobNameFileIdFlighTimeStatus/<wayline_job_id>', methods=["GET"])
@ensure_connection
def get_wayline_job_name_flighttime_fileid(conn,wayline_job_id):
    with conn.cursor() as cur:
        response = {"name": "", "fileId": "", "flightTime":"", "status": ""}
        cur.execute("SELECT name, file_id, begin_time, end_time, status FROM wayline_job WHERE job_id = %s", [wayline_job_id])
        rows = cur.fetchall()
        response["name"] = rows[0][0]
        response["fileId"] = rows[0][1]
        response["flightTime"] = rows[0][3] - rows[0][2]
        response["status"] = rows[0][4]
    return jsonify(response), 200

@sql_bp.route(prefix + '/getMissionName/<file_id>', methods=["GET"])
@ensure_connection
def get_mission_name(conn,file_id):
    with conn.cursor() as cur:
        response = {"missionName": ""}
        cur.execute("SELECT name FROM wayline_file WHERE wayline_id = %s", [file_id])
        rows = cur.fetchall()
        response["missionName"] = rows[0][0]
    return jsonify(response), 200


def save_ai_result(connection,AI_job_id, img_oss_path, result):
    cur = connection.cursor()
    row = [AI_job_id, img_oss_path, result]
    cur.execute("INSERT INTO AI_job_result (AI_job_id, img_oss_path, result) VALUES(%s, %s, %s)", row)
    connection.commit()
    cur.close()

    return "200"

@sql_bp.route(prefix + '/getDocks', methods=["GET"])
@ensure_connection
def get_all_docks(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM manage_device")
        rows = cur.fetchall()
        records = []
        for row in rows:
            if row[6] == 1:
                record_dict = {}
                record_dict["nickname"] = row[4]
                record_dict["sn"] = row[1]
                records.append(record_dict)
    return jsonify({'docks': records}), 200

def add_odm_task(job_id, output_path, status):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM odm_tasks WHERE job_id = %s", [job_id])
        existing_task = cur.fetchone()
        
        if existing_task:
            # If a record with the given job_id exists, update its status
            cur.execute("UPDATE odm_tasks SET status = %s, output_path = %s WHERE job_id = %s", [status, output_path, job_id])
        else:
            # If no record with the given job_id exists, create a new record
            cur.execute("INSERT INTO odm_tasks (job_id, output_path, status) VALUES (%s, %s, %s)", [job_id, output_path, status])
    return "200"

def get_odm_tasks():    
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM odm_tasks")
        rows = cur.fetchall()
        records = []
        for row in rows:
            records.append(row)
    
        return records


@sql_bp.route(prefix + '/deleteODMTask/<job_id>', methods=["DELETE"])
@ensure_connection
def delete_odm_task(conn,job_id):
    with conn.cursor() as cur:
        sql_query = f"DELETE FROM odm_tasks WHERE job_id = {job_id};"
        cur.execute(sql_query)
    return "200"

@sql_bp.route(prefix + '/addHistory', methods=["POST"])
@ensure_connection
def add_history(conn):
    cur = conn.cursor()
    data = request.json
    cur.execute("INSERT INTO history (event_code, event_description, event_type) VALUES(%(event_code)s, %(event_description)s, %(event_type)s)", data)
    conn.commit()
    cur.close()

    return "200"

@sql_bp.route(prefix + '/getHistory', methods=["GET"])
@ensure_connection
def get_history(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT * from history")
        rows = cur.fetchall()
        records = []
        for row in rows:
            records.append(row)
        
        return records
"""