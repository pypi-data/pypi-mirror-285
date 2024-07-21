import requests
from bs4 import BeautifulSoup as bs 
import json

def instagram(url):
    com = []
    cookies = {
        '_ga_HYFL742GNR': 'GS1.1.1717265838.1.0.1717265838.0.0.0',
        '_ga': 'GA1.1.1268182027.1717265838',
        '__gads': 'ID=ee92df8e37a22417:T=1717265839:RT=1717265839:S=ALNI_Maf1lAc8gh_k213_o0h9Lb0q3BOHA',
        '__gpi': 'UID=00000e39bc9df11d:T=1717265839:RT=1717265839:S=ALNI_MYg36c1aJEVTsrrq7SWBJdh7Y8LPg',
        '__eoi': 'ID=2013eb5969ce8efb:T=1717265839:RT=1717265839:S=AA-Afjb0NEbplYb8UrZHDhGpYGDB',
        '__gsas': 'ID=3c5ca9f6240fb535:T=1717265847:RT=1717265847:S=ALNI_MZxouHjuMrMafM_CQMczxdJmDvkrw',
        'FCNEC': '%5B%5B%22AKsRol96yZWx7FK5sPkCWa1kmfU6tsXGconfu10nsHP9CB3x2vDd-oFwIPpJp-oxaQleN0SpAaw5YK8pVDRsL447EoZLPPe9ld_nFbhUCDqyErJh1YwpJZ1Pj58v12_WItXE_CCWIVa4RkTuSulwNUJfXDd0AemQNw%3D%3D%22%5D%5D',
    }
    
    headers = {
        'authority': 'snapinsta.io',
        'accept': '*/*',
        'accept-language': 'ar-US,ar;q=0.9,en-US;q=0.8,en;q=0.7,ku;q=0.6',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://snapinsta.io',
        'referer': 'https://snapinsta.io/en20',
        'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    
    data = {
        'q': url, 
        't': 'media',
        'lang': 'en',
    }
    
    r = requests.post('https://snapinsta.io/api/ajaxSearch', cookies=cookies, headers=headers, data=data).text
    res = json.loads(r)
    con = res.get('data', '')
    
    if con:
        soup = bs(con, "html.parser")
        find = soup.find_all("div", {"class": "download-items__btn"})
        
        for div in find:
            a_tag = div.find("a", {"class": "abutton is-success is-fullwidth btn-premium mt-3"})
            if a_tag:
                href = a_tag.get('href')
                com.append(href)
        return com  
    else:
        return com  

