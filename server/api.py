import HeartbotBackyard.DBHandler as DBHandler
import HeartbotBackyard.Errors as Errors
from flask import Blueprint, jsonify, request, session
import redis
import random

rdis=redis.Redis(host="localhost",port=6379,db=0,decode_responses=True)
api_bp = Blueprint('api', __name__, url_prefix='/api')

def bad_request(message):
	return jsonify({"status":"bad_request","message":message}), 400
def invalid_request(message):
	return jsonify({"status":"invalid","message":message}), 429
def error(message):
	return jsonify({"status":"error","message":message}), 200

@api_bp.route("/login", methods=["POST"])
def login():
	
	 if request.method!="POST":
	 	return bad_request("Wrong method")
	 
	 
	 data=dict(request.get_json(force=True))
	 username=data.get("username",False)
	 password=data.get("password", False)
	 if username and password:
	 	user_data=DBHandler.check_login_creds(username,password)
	 	if user_data :
	 		session["id"]=user_data.id
	 		session["username"]=user_data.username
	 		session["type"]=user_data.type
	 		return jsonify({"status":"success"})
	 		
	 	else:
	 		return error("wrong_username_or_password")
	 else:
	 	return bad_request("bad_request")

@api_bp.route("/register", methods=["POST"])
def register():
	data=dict(request.get_json(force=True))
	email=data.get("email",False)
	username=data.get("username",False)
	password=data.get("password", False)
	if email and username and password:
		try:
			DBHandler.register_user(email,username,password)
			return {"status":"success","message":"confirm_email"}
		except Errors.InvalidEmail:
			return error("invalid_email")
		except Errors.InvalidUsername:
			return error("invalid_username")
		except Errors.UnavailableUsername:
			return error("unavailable_username")
	else:
		return bad_request("invalid")

@api_bp.route("/check_username", methods=["GET"])
def check_username():
	username = request.args.get("username")
	if not username:
		return bad_request("missing_username")
	
	available = DBHandler.check_if_username_available(username)
	return jsonify({"status": "success", "available": available})

@api_bp.route("/get_profile", methods=["GET"])
def mytoken():
	if session.get("id",False):
		
		return jsonify(
		{"status":"success",
		"data":
			{
			"user_id":session["id"],
			"username":session["username"],
			"type":session["type"]
			}
		})
	else:
		return error("not_logged_in")