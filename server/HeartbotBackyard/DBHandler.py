from sqlalchemy import create_engine, Column, Integer, String, exc
from sqlalchemy.orm import declarative_base, sessionmaker  
from hashlib import sha256
from . import Errors
import re, uuid
email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
username_regex = r'^[a-z][a-zA-Z0-9_]{2,19}$'

engine = create_engine("sqlite:///users.db")  
Base = declarative_base()  
salt=b"demosalt"
class User(Base):  
    __tablename__ = "users"  
    id = Column(Integer, primary_key=True)
    email = Column(String)
    username = Column(String, unique=True)  
    password = Column(String)
    type = Column(String)
    
    
    


Base.metadata.create_all(engine)  
  
Session = sessionmaker(bind=engine)  
database = Session()

def _is_email(email):
	return re.match(email_regex, email) is not None

def _is_valid_username(username):
    return re.match(username_regex, username) is not None

########################

def check_if_username_available(username:str):
	user = database.query(User).filter_by(username=username).first()
	if user:
		return False
	else:
		return True

def register_user(email:str,username:str,password:str):
	if _is_valid_username(username) == False:
		raise Errors.InvalidUsername()
	if _is_email(email) == False:
		raise Errors.InvalidEmail()
	user=User(
	email=email,
	username=username,
	password=sha256(salt+password.encode()).hexdigest(),
	type="free",
	)
	
	database.add(user)
	try:
		database.commit()
		return True
	except exc.IntegrityError:
		database.rollback()
		raise Errors.UnavailableUsername()
	
	

def check_login_creds(username:str, password:str):
	if _is_email(username):
		user = database.query(User).filter_by(email=username).first()
	elif _is_valid_username(username):
		user = database.query(User).filter_by(username=username).first()
	else:
		return False
	
	if user:
		
		if sha256(salt+password.encode()).hexdigest() == user.password:
			return user
		else :
			return False
	else:
		return False

