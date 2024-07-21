import requests
def Twitter_Download(url):
	urll = url.split("/")[-1]
	headers = {
	    'authority': 'onlinetechbd.com',
	    'accept': '*/*',
	    'accept-language': 'ar-IQ,ar;q=0.9,en-US;q=0.8,en;q=0.7',
	    'origin': 'https://7ammel.net',
	    'referer': 'https://7ammel.net/',
	    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
	    'sec-ch-ua-mobile': '?1',
	    'sec-ch-ua-platform': '"Android"',
	    'sec-fetch-dest': 'empty',
	    'sec-fetch-mode': 'cors',
	    'sec-fetch-site': 'cross-site',
	    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
	}
	
	params = {
	    'video': urll,
	}
	try:
		r = requests.get('https://onlinetechbd.com/video/new-api.php', params=params, headers=headers).json()["hd"]
		return {"url":r}
	except Exception as e:
		return e
