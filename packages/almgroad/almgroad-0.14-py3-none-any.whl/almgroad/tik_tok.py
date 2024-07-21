import requests
def Tik_Tok(url):
	headers = {
    		'authority': 'lovetik.com',
    		'accept': '*/*',
    		'accept-language': 'ar,en-US;q=0.9,en;q=0.8',
    		'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    		'origin': 'https://lovetik.com',
    		'referer': 'https://lovetik.com/',
    		'sec-fetch-dest': 'empty',
    		'sec-fetch-mode': 'cors',
    		'sec-fetch-site': 'same-origin',
    		'sec-gpc': '1',
    		'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36',
    		'x-requested-with': 'XMLHttpRequest',
    	}
	data = {
    		'query': url}
	try:
		result = requests.post('https://lovetik.com/api/ajax/search', headers=headers, data=data).json()["links"][0]["a"]
		return {"url":result,"PROGRAMMER":"IBRAHIM : TELEGRAM :@q3oooo"}
	except Exception as e:
		return f"error : {e}"