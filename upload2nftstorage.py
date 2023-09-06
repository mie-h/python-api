import requests

url = "http://file.api.wechat.com/cgi-bin/media/upload?access_token=ACCESS_TOKEN&type=TYPE"
files = {"media": open("test.jpg", "rb")}
requests.post(url, files=files)
