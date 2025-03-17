from flask import Flask
from api import api_bp, smtp

app = Flask(__name__)
app.secret_key = "ksmk"
app.register_blueprint(api_bp)

with app.app_context():
	smtp.init_app()

@app.route("/")
def home():
    return "up and running."

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=80)