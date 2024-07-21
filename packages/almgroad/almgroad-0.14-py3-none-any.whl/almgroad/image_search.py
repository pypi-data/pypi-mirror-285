import requests 
def Img_Search(word):
	list = []
	url = "https://api.pexels.com/v1/search"
	headers={
		"Authorization":"rYzMnZVxnzkcLMVu3VkxdkzdCeF4vaH0EF312uczsSWgejlK7SbGWEKZ"
		}
	data = {
		"query":word,
		"page":1,
		"per_page":10
		}
	r = requests.get(url ,headers=headers ,params=data).json()["photos"]
	for pho in r:
		list.append(pho["url"])
	return list
