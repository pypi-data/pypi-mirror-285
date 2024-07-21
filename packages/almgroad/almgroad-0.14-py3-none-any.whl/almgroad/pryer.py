import requests
def prayer_times(name):
	try:
		r = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={name}&country={name}&method=8").json()["data"]["timings"]
		all = {"الفجر":r['Fajr'],
		"الشروق":r['Sunrise'],
		"الظهر":r['Dhuhr'],
		"العصر":r['Asr'],
		"المغرب":r['Maghrib'],
		"العشاء":r['Isha']}
		return all
	except:
		return "حدث خطأ : تاكد من كتابة اسم المدينة بشكل صحيح"
