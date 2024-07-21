import requests
def Spotify_Download(url):
	urll = url.split("/")[-1].split("?")[0]
	headers = {
	    'authority': 'api.spotifydown.com',
	    'accept': '*/*',
	    'accept-language': 'ar-IQ,ar;q=0.9,en-US;q=0.8,en;q=0.7',
	    'origin': 'https://spotifydown.com',
	    'referer': 'https://spotifydown.com/',
	    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
	    'sec-ch-ua-mobile': '?1',
	    'sec-ch-ua-platform': '"Android"',
	    'sec-fetch-dest': 'empty',
	    'sec-fetch-mode': 'cors',
	    'sec-fetch-site': 'same-site',
	    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
	}
	try:
		r = requests.get(f'https://api.spotifydown.com/download/{urll}', headers=headers).json()
		return {
		"url":r["link"],
		"title":r['metadata']['title'],
		"artist": r['metadata']['artists'],
		"photo":r['metadata']['cover'],
		}
	except Exception as e:
		return e 
