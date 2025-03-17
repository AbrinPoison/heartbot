class UnavailableUsername(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args,"The chosen username isn't available.")

class InvalidUsername(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args,"Pick a valid username, using only letters, numbers, and _, also it doesn't start with a number.")
class InvalidEmail(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args,"Invalid email.")
class InvalidUID(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args,"Invalid user id")
class InvalidUpdate(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args,"Invalid user id")
