import requests
from user_agent import generate_user_agent 
def Rest_Instagram(user):
	cookies = {
	    'csrftoken': 'Y4N_IrXQK-p-l108uERtub',
	    'dpr': '3',
	    'ig_did': '2AF51DB2-0013-475E-B89C-826B1EDA4E71',
	    'ig_nrcb': '1',
	    'mid': 'ZmqLCwABAAH6LKjIfRUXUi9x_I3_',
	    'datr': 'C4tqZuGp2A8V407XZdMEcURo',
	    'wd': '360x657',
	}
	
	headers = {
	    'authority': 'www.instagram.com',
	    'accept': '*/*',
	    'accept-language': 'ar-IQ,ar;q=0.9,en-US;q=0.8,en;q=0.7',
	    'content-type': 'application/x-www-form-urlencoded',
	    # 'cookie': 'csrftoken=Y4N_IrXQK-p-l108uERtub; dpr=3; ig_did=2AF51DB2-0013-475E-B89C-826B1EDA4E71; ig_nrcb=1; mid=ZmqLCwABAAH6LKjIfRUXUi9x_I3_; datr=C4tqZuGp2A8V407XZdMEcURo; wd=360x657',
	    'origin': 'https://www.instagram.com',
	    'referer': 'https://www.instagram.com/accounts/password/reset/',
	    'sec-ch-prefers-color-scheme': 'dark',
	    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
	    'sec-ch-ua-full-version-list': '"Not-A.Brand";v="99.0.0.0", "Chromium";v="124.0.6327.4"',
	    'sec-ch-ua-mobile': '?1',
	    'sec-ch-ua-model': '"JKM-LX1"',
	    'sec-ch-ua-platform': '"Android"',
	    'sec-ch-ua-platform-version': '"9.0.0"',
	    'sec-fetch-dest': 'empty',
	    'sec-fetch-mode': 'cors',
	    'sec-fetch-site': 'same-origin',
	    'user-agent': generate_user_agent(),
	    'x-asbd-id': '129477',
	    'x-csrftoken': 'Y4N_IrXQK-p-l108uERtub',
	    'x-ig-app-id': '1217981644879628',
	    'x-ig-www-claim': '0',
	    'x-instagram-ajax': '1014260056',
	    'x-requested-with': 'XMLHttpRequest',
	}
	
	data = {
	    'email_or_username': user,
	}
	
	response = requests.post(
	    'https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/',
	    cookies=cookies,
	    headers=headers,
	    data=data,
	).json()
	return {"message":response}
