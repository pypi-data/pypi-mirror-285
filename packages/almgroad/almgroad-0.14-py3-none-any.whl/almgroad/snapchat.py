import requests
def SnapChat_Download(url):
	cookies = {
	    'pp_main_cfa30a47f874cfe393cba764dea7b4ac': '1',
	    '_ga_4ZL7M2PHGQ': 'GS1.1.1718952323.1.0.1718952323.0.0.0',
	    '_ga': 'GA1.1.1347181821.1718952324',
	    'sb_main_6ce5a3cd556fc238fcd84f9b57ea3731': '1',
	    'dom3ic8zudi28v8lr6fgphwffqoz0j6c': '4ee8cbeb-e1fe-47a9-9299-c322abf98eb9%3A1%3A1',
	    'pll_language': 'ar',
	    'pp_sub_cfa30a47f874cfe393cba764dea7b4ac': '1',
	    'pp_delay_cfa30a47f874cfe393cba764dea7b4ac': '1',
	    'cf_clearance': 'kZcuWbI9JGhJqmQyQodj.gc7pVIAnhvB9S_8NbbEVC0-1718952342-1.0.1.1-VtblgercOHBN9vxelvOEKYC82qTLyaEgtqRtgrbpWCxFh9eKO3oPUn472vHJ.aLNDD.ngWdXgESlouGyMmYNkg',
	    'sb_count_6ce5a3cd556fc238fcd84f9b57ea3731': '2',
	}
	
	headers = {
	    'authority': 'davapps.com',
	    'accept': '*/*',
	    'accept-language': 'ar-IQ,ar;q=0.9,en-US;q=0.8,en;q=0.7',
	    'content-type': 'application/x-www-form-urlencoded',
	    # 'cookie': 'pp_main_cfa30a47f874cfe393cba764dea7b4ac=1; _ga_4ZL7M2PHGQ=GS1.1.1718952323.1.0.1718952323.0.0.0; _ga=GA1.1.1347181821.1718952324; sb_main_6ce5a3cd556fc238fcd84f9b57ea3731=1; dom3ic8zudi28v8lr6fgphwffqoz0j6c=4ee8cbeb-e1fe-47a9-9299-c322abf98eb9%3A1%3A1; pll_language=ar; pp_sub_cfa30a47f874cfe393cba764dea7b4ac=1; pp_delay_cfa30a47f874cfe393cba764dea7b4ac=1; cf_clearance=kZcuWbI9JGhJqmQyQodj.gc7pVIAnhvB9S_8NbbEVC0-1718952342-1.0.1.1-VtblgercOHBN9vxelvOEKYC82qTLyaEgtqRtgrbpWCxFh9eKO3oPUn472vHJ.aLNDD.ngWdXgESlouGyMmYNkg; sb_count_6ce5a3cd556fc238fcd84f9b57ea3731=2',
	    'origin': 'https://davapps.com',
	    'referer': 'https://davapps.com/ar/snapchat-%D8%AA%D9%86%D8%B2%D9%8A%D9%84-%D8%A7%D9%84%D9%81%D9%8A%D8%AF%D9%8A%D9%88snapchat/',
	    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
	    'sec-ch-ua-mobile': '?1',
	    'sec-ch-ua-platform': '"Android"',
	    'sec-fetch-dest': 'empty',
	    'sec-fetch-mode': 'cors',
	    'sec-fetch-site': 'same-origin',
	    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
	}
	
	data = {
	    'url': str(url),
	    'token': 'ea1aeb76ac11b5f3c82a692af37c9b52a1820b29664fc08739856b46063b1c15',
	    'hash': 'aHR0cHM6Ly9zbmFwY2hhdC5jb20vdC9WanlYQXd1Vg==1031YWlvLWRs',
	}
	try:
		response = requests.post('https://davapps.com/wp-json/aio-dl/video-data/', cookies=cookies, headers=headers, data=data)
		if response.status_code == 200:
			res = response.json()["medias"][0]["url"]
			return res
		else:
			return "حدث خطأ"
	except Exception as e:
		print(e)