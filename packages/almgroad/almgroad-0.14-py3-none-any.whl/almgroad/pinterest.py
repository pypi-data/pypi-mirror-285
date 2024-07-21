#pylint:disable=W0702
import requests
def Pinterest_Download(url):
	cookies = {
	    'ci_session': 'hfnl4v6a5cbo52i780gt4ga58vivv6ir',
	    '_ga_E7SFLTHFL8': 'GS1.1.1718732070.1.0.1718732070.0.0.0',
	    '_ga': 'GA1.1.502498875.1718732071',
	    '__eoi': 'ID=acfffee1f4317260:T=1718732073:RT=1718732073:S=AA-AfjY_z617vIN3hiN2Yif8Y54N',
	    'FCNEC': '%5B%5B%22AKsRol9sdfw-w_GNNAWHxxjXcu0l75zIsFKGYrUM8cp_xWAn3YFOhFva0KvcQ4voGA--uklb6TiwRi1LorSqsNbwcuOxYx2hEQaYw58jE9t0wU4kmEDiV-fk1TZaZzqA0e4raWfKXFFfPVeJAyjM7JbLExRbZuOp8A%3D%3D%22%5D%5D',
	}
	
	headers = {
	    'authority': 'pinterestdownloader.io',
	    'accept': '*/*',
	    'accept-language': 'ar-IQ,ar;q=0.9,en-US;q=0.8,en;q=0.7',
	    'referer': 'https://pinterestdownloader.io/',
	    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
	    'sec-ch-ua-mobile': '?1',
	    'sec-ch-ua-platform': '"Android"',
	    'sec-fetch-dest': 'empty',
	    'sec-fetch-mode': 'cors',
	    'sec-fetch-site': 'same-origin',
	    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
	}
	try:
		r = requests.get(
		    f'https://pinterestdownloader.io/frontendService/DownloaderService?url={url}',
		    cookies=cookies,
		    headers=headers,
		).json()["medias"][2]["url"]
		return {
		"is_photo":False,
		"url":r
		}
	except:
		y = requests.get(
		    f'https://pinterestdownloader.io/frontendService/DownloaderService?url={url}',
		    cookies=cookies,
		    headers=headers,
		).json()["medias"][1]["url"]
		return {
		"is_photo":True ,
		"url":y
		}