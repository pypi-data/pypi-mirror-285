import requests
class ibrahim:
	def information(username):	    
		try:
			info=requests.get('https://anonyig.com/api/ig/userInfoByUsername/'+username).json()
		except :
			info = False
		try:
		    Id =info['result']['user']['pk_id']
		except :
		    Id = None
		try:
		    followers = info['result']['user']['follower_count']
		except :
		    followers = None
		try:
		    following = info['result']['user']['following_count']
		except :
			following = None
		try:
		    post = info['result']['user']['media_count']
		except :
		    post = None
		try:
		    name = info['result']['user']['full_name']
		except :
		    name = None
		try:
		    is_verified = info['result']['user']["is_verified"]
		except:
		    is_verified = None
		try:
		    is_private= info['result']['user']['is_private']
		except:
		    is_private = None
		try:
		    biography = info['result']['user']['biography']
		except:
		    biography = None
		try:
			if int(Id) >1 and int(Id)<1279000:
				date =  "2010"
			elif int(Id)>1279001 and int(Id)<17750000:
				date =  "2011"
			elif int(Id) > 17750001 and int(Id)<279760000:
				date =  "2012"
			elif int(Id)>279760001 and int(Id)<900990000:
				date =  "2013"
			elif int(Id)>900990001 and int(Id)< 1629010000:
				date =  "2014"
			elif int(Id)>1900000000 and int(Id)<2500000000:
				date =  "2015"
			elif int(Id)>2500000000 and int(Id)<3713668786:
				date =  "2016"
			elif int(Id)>3713668786 and int(Id)<5699785217:
				date =  "2017"
			elif int(Id)>5699785217 and int(Id)<8507940634:
				date =  "2018"
			elif int(Id)>8507940634 and int(Id)<21254029834:
				date =  "2019"	         
			else:
				date= "2020-2023"
		except :
		    pass
		return {
		    "name" : name ,
		    "username" : username ,
		    "followers" : followers , 
		    "following" : following ,
		    "date" : date ,
		    "id" : Id ,
		    "post" : post , 
		    "bio" : biography , 
		    "is_verified" : is_verified , 
		    'is_private' : is_private , 		    
		    }	    
