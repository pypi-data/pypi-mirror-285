import requests
def Info_Tik(user):
	try:
		url = 'http://tik.report.ilebo.cc/users/login'
		headers = {
            'X-IG-Capabilities': '3brTvw==',
            'User-Agent': 'TikTok 85.0.0.21.100 Android (33/13; 480dpidpi; 1080x2298; HONOR; ANY-LX2; ANY-LX2;)',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json; charset=utf-8',
            'Content-Length': '73',
            'Host': 'tik.report.ilebo.cc',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
        }
		data = {"unique_id": user, "purchaseTokens": []}
		respose = requests.post(url, headers=headers, data=data).json()
		name = respose['data']['user']['user']['nickname']
		following= respose['data']['user']['stats']['followingCount']
		followers = respose['data']['user']['stats']['followerCount']
		Id = respose['data']['user']['user']['id']
		like = respose['data']['user']['stats']['heartCount']
		private = respose['data']['user']['user']['privateAccount']
		video = respose['data']['user']['stats']['videoCount']
		return {'username':user,'name':name,'followers':followers,'following':following,'id':Id,'like':like,'private':private,'video':video}
		#return good user
	except:
		return {'username':'','name':'','followers':'','following':'','id':'','like':'','video':''}
#return erorr user 
