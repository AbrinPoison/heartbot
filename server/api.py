import HeartbotBackyard.DBHandler as DBHandler
import HeartbotBackyard.Errors as Errors
from HeartbotBackyard.Email import EmailHandler
import pyotp, base64
from flask import Blueprint, jsonify, request, session
#import redis

#rdis=redis.Redis(host="localhost",port=6379,db=0,decode_responses=True)
api_bp = Blueprint('api', __name__, url_prefix='/api')
secret=pyotp.random_base32()

smtp=EmailHandler()


def handle_otp(user_id, otp=None):
	user_id_bytes = str(user_id).encode('utf-8')
	encoded_combined = base64.b32encode(user_id_bytes + secret.encode('utf-8')).decode('utf-8')
	
	if not otp:
		return pyotp.TOTP(encoded_combined,interval=600).now()
	else:
		return pyotp.TOTP(encoded_combined,interval=600).verify(otp)
	
def bad_request(message):
	return jsonify({"status":"bad_request","code":message}), 400
def invalid_request(message, code=400):
	return jsonify({"status":"invalid","code":message}), code
def error(message, code=200):
	return jsonify({"status":"error","code":message}), code

@api_bp.route("/login", methods=["POST"])
def login():
	
	 if request.method!="POST":
	 	return bad_request("wrong_method")
	 
	 
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
	 	return bad_request("missing_parameter")

@api_bp.route("/register", methods=["POST"])
def register():
	
	data=dict(request.get_json(force=True))
	email=data.get("email",False)
	username=data.get("username",False)
	password=data.get("password", False)
	if email and username and password:
		try:
			user_data=DBHandler.register_user(email,username,password)
			
			session["id"]=user_data.id
			session["username"]=user_data.username
			session["type"]=user_data.type
			otp=handle_otp(user_data.id)
			smtp.verify_email(email,otp,username)
			return {"status":"success","message":"confirm_email"}
		except Errors.InvalidEmail:
			return error("invalid_email")
		except Errors.InvalidUsername:
			return error("invalid_username")
		except Errors.UnavailableUsername:
			return error("unavailable_username")
	else:
		return bad_request("missing_parameter")

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
		return error("not_logged_in",401)

@api_bp.route("/change_email",methods=["GET"])
def change_email():
	id=session.get("id",False)
	if id:
		new_email = request.args.get("new_email")
		if new_email:
			try:
				old=DBHandler.change_email(id,new_email)
				smtp.email_changed(old.email,old.username,new_email)
				otp=handle_otp(id)
				smtp.verify_email(new_email, otp, old.username)
				return {"status":"success","message":"confirm_email"}
			except Errors.InvalidUID:
				return error("invalid_uid")
			except Errors.InvalidUpdate:
				return error("same_email")
		else:
			return error("missing_parameter")
	else:
		return error("not_logged_in",401)


@api_bp.route("/verify", methods=["GET"])
def verify():
	id=session.get("id",False)
	if id:
		otp = request.args.get("otp")
		if otp:
			
			if handle_otp(id,otp):
				DBHandler.verify_account(id)
				return jsonify({"status": "success"})
			
			else:
				return error("invalid_otp",200)
		else:
			return error("missing_parameter")
	else:
		return error("not_logged_in",401)


##### Admin #####

@api_bp.route("/suspend",methods=["GET"])
def suspend():
	user_id=request.args.get("id")
	if not user_id:
		return invalid_request("no_uid")
	type=session.get("type",False)
	if type == "admin":
		try:
			DBHandler.suspend_user(user_id)
			return jsonify({"status":"success"})
		except Errors.InvalidUID:
			return error("invalid_uid")
		except Errors.InvalidUpdate:
			return error("user_is_suspended")
	else:
		return invalid_request("permission_denied", 403)

@api_bp.route("/unsuspend",methods=["GET"])
def unsuspend():
	user_id=request.args.get("id")
	if not user_id:
		return invalid_request("no_uid")
	type=session.get("type",False)
	if type == "admin":
		try:
			DBHandler.unsuspend_user(user_id)
			return jsonify({"status":"success"})
		except Errors.InvalidUID:
			return error("invalid_uid")
		except Errors.InvalidUpdate:
			return error("user_is_active")
	else:
		return invalid_request("permission_denied", 403)

@api_bp.route("/create_admin",methods=["POST"])
def promote():
	if request.method!="POST":
	 	return bad_request("wrong_method")
	 
	 
	data=dict(request.get_json(force=True))
	username=data.get("username",False)
	password=data.get("password", False)
	if username and password:
		try:
			DBHandler.create_admin(username,password)
			return jsonify({"status":"success"})
		except Errors.InvalidUpdate :
			return error("admin_exists")
	else:
		return bad_request("missing_parameter")

@api_bp.route("/remove_admin",methods=["GET"])
def demote():
	username=request.args.get("username")
	if not username:
		return invalid_request("no_username")
	
	try:
		DBHandler.remove_admin(username)
		return jsonify({"status":"success"})
	except Errors.InvalidUID :
		return error("admin_doesnt_exist")