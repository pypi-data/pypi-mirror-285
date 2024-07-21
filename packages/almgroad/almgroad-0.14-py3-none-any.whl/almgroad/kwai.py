import yt_dlp
def Kwai_Download(url):
	ydl_opts = {
	    'format': 'best',
	    'outtmpl': '%(title)s.%(ext)s',
	    'nocheckcertificate': True
	}
	try:
		with yt_dlp.YoutubeDL(ydl_opts) as ydl:
		    info = ydl.extract_info(url,download=False)["formats"][0]["url"]
		    return info
	except Exception as e:
		return e
