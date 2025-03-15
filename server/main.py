# app.py
from flask import Flask
from api import api_bp  # Import the blueprint from api.py

app = Flask(__name__)

# Register the blueprint
app.secret_key="ksmk"
app.register_blueprint(api_bp)

@app.route("/")
def home():
	return "up and running."

if __name__ == '__main__':
    app.run()
    