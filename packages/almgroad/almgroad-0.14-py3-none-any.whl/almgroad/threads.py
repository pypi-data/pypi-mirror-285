import requests
def Threads_Download(url):
	g = url.split("/")[-2]
	headers = {
	    'Upgrade-Insecure-Requests': '1',
	    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
	    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
	    'sec-ch-ua-mobile': '?1',
	    'sec-ch-ua-platform': '"Android"',
	}
	try:
		r = requests.get(f'https://threadster.app/download/{g}', headers=headers).text.split('<a download class="btn download__item__info__actions__button" href="')[1].split('"')[0]
		return {
		"url":r
		}
	except Exception as e:
		return e 
	
	