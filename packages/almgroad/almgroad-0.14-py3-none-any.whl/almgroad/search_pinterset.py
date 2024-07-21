import requests 
def Search_Pinterest(word):
	labl = []
	url = 'https://www.pinterest.com/resource/BaseSearchResource/get/?source_url=/search/my_pins/?q=avengers&rs=rs&eq=naruto%208K&etslf=15092&term_meta[]=avengers%7Crecentsearch%7C4&data={"options":{"article":null,"applied_filters":null,"appliedProductFilters":null,"auto_correction_disabled":false,"corpus":null,"customized_rerank_type":null,"filters":null,"query":"'+word+'","query_pin_sigs":null,"redux_normalize_feed":true,"rs":"direct_navigation","scope":"pins","source_id":null,"no_fetch_context_on_resource":false},"context":{}}&_=1662617352806'
	try:
		r = requests.get(url).json()['resource_response']['data']['results']
		for imag in r:
			hh = imag['images']['orig']['url']
			labl.append(hh)
		return {"urls":labl,"Programmer":"Ibrahim : Telegram : @B_xxBx"}
	except:
		return {"message":"حدث خطأ حاول من جديد مع كلمة اخرى","Programmer":"Ibrahim : Telegram : @B_xxBx"}

        