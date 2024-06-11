class OperationResult:
	
	def __init__(self, success, message):
		self.success = success
		self.message = message

	def was_successful(self):
		return self.success

	def get_message(self):
		return self.message