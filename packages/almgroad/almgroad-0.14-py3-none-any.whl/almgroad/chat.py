import requests
def GPT(q):
	r = requests.get(f"https://chatgpt.apinepdev.workers.dev/?question={q}").json()["answer"]
	return {"answer":r,"PROGRAMMER":"IBRAHIM : TELEGRAM :@q3oooo"}