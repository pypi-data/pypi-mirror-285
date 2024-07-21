import yt_dlp 
def Likee_Download(url):
	dl = {
    'format': 'best',
    'outtmpl': '%(title)s.%(ext)s',
}
	with yt_dlp.YoutubeDL(dl) as d:
		info = d.extract_info(url,download=False)
		try:
			re = info['formats'][0]['url']
			return {
			"url":re
			}
		except Exception as e:
			return e 
print(Likee_Download("https://l.likee.video/v/6BjmZl"))