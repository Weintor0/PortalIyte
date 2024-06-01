from flask import Flask
from controller.userController import user_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.register_blueprint(user_bp)


@app.before_request
def init_threads():
    app.before_request_funcs[None].remove(init_threads)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002,debug = True)