import HeartbotBackyard.DBHandler as DBHandler
import HeartbotBackyard.Errors as Errors
from HeartbotBackyard.Email import EmailHandler
from flask import Blueprint, jsonify, request, session, make_response
import redis,random,uuid


r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
#rdis=redis.Redis(host="localhost",port=6379,db=0,decode_responses=True)
api_bp = Blueprint('api', __name__, url_prefix='/api')


smtp=EmailHandler()


def handle_otp(user_id, otp=None):
	if otp:
		if r.get(str(user_id)) == otp:
			return True
		else :
			return False
	else:
		notp=str(random.randint(100000,999999))
		r.setex(str(user_id),600,notp)
		return notp

def session_builder(user):
	
	session_id=f"{user.id}:{uuid.uuid4()}"
	r.hset(session_id, mapping = {
	'user_id': user.id,
	'email': user.email,
	'username': user.username,
	'is_subscribed': int(user.is_subscribed),
	'is_suspended': int(user.is_suspended),
	'is_verified': int(user.is_verified)
	})

	return session_id

def update_session(session_id):
	
	user=DBHandler.fetch_user(r.hget(session_id,"user_id"))
	r.hset(session_id, mapping = {
	'user_id': user.id,
	'email': user.email,
	'username': user.username,
	'is_subscribed': int(user.is_subscribed),
	'is_suspended': int(user.is_suspended),
	'is_verified': int(user.is_verified)
	})

def invoke_sessions_except(session_id):
	user_id=r.hget(session_id,"user_id")
	sessions=r.scan_iter(f"{user_id}:*")
	
	for asession in sessions:
		if asession==session_id : continue
		else: r.delete(asession)

def fetch_session(session_id):
	return r.hgetall(session_id)

def not_logged_in():
	response=make_response(jsonify({"status":"error","code":"not_logged_in"}), 401)
	response.set_cookie("session_id","",expires=0)
	return response
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
	 		session_id=session_builder(user_data)
	 		response=make_response(jsonify({"status":"success"}))
	 		response.set_cookie("session_id",session_id,httponly=True,secure=True)
	 		return response
	 		
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
			#otp=handle_otp(user_data.id)
			#smtp.verify_email(email,otp,username)
			
			session_id=session_builder(user_data)
			response=make_response(jsonify({"status":"success"}))
			response.set_cookie("session_id",session_id,httponly=True,secure=True)
			return response
			
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
	session_info=fetch_session(request.cookies.get("session_id","None"))
	if session_info:
		
		return jsonify(
		{"status":"success",
		"data":
			session_info
		})
	else:
		return not_logged_in()

@api_bp.route("/change_email",methods=["GET"])
def change_email():
	session_info=fetch_session(request.cookies.get("session_id","None"))
	if session_info:
		uid=session_info["user_id"]
		new_email = request.args.get("new_email")
		if new_email:
			try:
				old=DBHandler.change_email(uid,new_email)
				smtp.email_changed(old["email"],old["username"],new_email)
				otp=handle_otp(uid)
				smtp.verify_email(new_email, otp, old["username"])
				DBHandler.edit_verify(uid,False)
				update_session(request.cookies.get("session_id","None"))
				return {"status":"success","code":"confirm_email"}
			except Errors.InvalidUID:
				return error("invalid_uid")
			except Errors.InvalidUpdate:
				return error("same_email")
		else:
			return error("missing_parameter")
	else:
		return not_logged_in()


@api_bp.route("/verify", methods=["GET"])
def verify():
	session_info=fetch_session(request.cookies.get("session_id","None"))
	if session_info:
		otp = request.args.get("otp")
		if otp:
			
			if handle_otp(session_info["user_id"],otp):
				DBHandler.edit_verify(session_info["user_id"],True)
				return jsonify({"status": "success"})
			
			else:
				return error("invalid_otp",200)
		else:
			return error("missing_parameter")
	else:
		return not_logged_in()
		
@api_bp.route("/change_password", methods=["GET"])
def change_password():
	session_info=fetch_session(request.cookies.get("session_id","None"))
	if session_info:
		new_password = request.args.get("password")
		if new_password:
			try:
				DBHandler.change_password(session_info["user_id"],new_password)
				invoke_sessions_except(request.cookies.get("session_id","None"))
				return jsonify({"status": "success"})
			except Errors.InvalidUpdate:
				return error("password_didnt_change")
			
		else:
			return error("missing_parameter")
	else:
		return not_logged_in()



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