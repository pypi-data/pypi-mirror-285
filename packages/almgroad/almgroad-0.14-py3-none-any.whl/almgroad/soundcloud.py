import requests
def Sound_Cloud(url):
	headers = {
	    'authority': 'api.downloadsound.cloud',
	    'accept': 'application/json, text/plain, */*',
	    'accept-language': 'ar-IQ,ar;q=0.9,en-US;q=0.8,en;q=0.7',
	    'content-type': 'application/json;charset=UTF-8',
	    'origin': 'https://downloadsound.cloud',
	    'referer': 'https://downloadsound.cloud/',
	    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
	    'sec-ch-ua-mobile': '?1',
	    'sec-ch-ua-platform': '"Android"',
	    'sec-fetch-dest': 'empty',
	    'sec-fetch-mode': 'cors',
	    'sec-fetch-site': 'same-site',
	    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
	}
	
	json_data = {
	    'url': url
	}
	
	r = requests.post('https://api.downloadsound.cloud/track', headers=headers, json=json_data).json()
	audio_url = r["url"]
	image_url = r["imageURL"]
	title = r["title"]
	performer = r["author"]["username"]
	return {
	"url":audio_url,
	"image_url":image_url,
	"title":title,
	"performer":performer
	}
