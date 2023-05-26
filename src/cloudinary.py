from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
import cloudinary
import time


class Uploader:
	
	def __init__(self, cloud_name:str, api_key:str, api_secret:str):
		cloudinary.config(
			cloud_name = cloud_name,
			api_key = api_key,
			api_secret = api_secret,
			secure = True
		)
					
	def upload_image(self, image_url:str):
		public_id = self.generatePublicId()
		upload(image_url, public_id=public_id)
		url, options = cloudinary_url(public_id)
		return url

	def generatePublicId(self):
		return "rbyb" + str(int(round(time.time() * 1000)))