import requests

class FileUploader:

	def uploadFile(self,file_path:str):
		try:
			# open the file in binary mode
			with open(file_path, "rb") as file:
				# make the HTTP POST request to the Transfer.sh API
				response = requests.post("https://transfer.sh/", files={"file": file})
				# extract the URL from the response
				url = response.content.decode("utf-8")
				return url
		except Exception as e:
			print(f"Error uploading file: {e}")