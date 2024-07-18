import os
try:
	import re
	import json
	import random
	import requests
	import urllib.request
	from user_agent import generate_user_agent
except:
	libraries = [
		"requests",
		"user_agent"
	]
	for lib in libraries:
		os.system(f"pip install {lib}")
class TikTok:
	@staticmethod
	def info(user):
		try:
			if "@" in user:
				user = str(user).replace("@", "")
			url = 'https://www.tiktok.com/@'+user
			page = urllib.request.urlopen(url)
			content = (page.read()).decode('utf-8')
			user_id_match = re.search(r'"id":"(\d+)"', content)
			user_id = user_id_match.group(1) if user_id_match else None
			
			unique_id_match = re.search(r'"uniqueId":"([^"]+)"', content)
			unique_id = unique_id_match.group(1) if unique_id_match else None
			
			nickname_match = re.search(r'"nickname":"([^"]+)"', content)
			nickname = nickname_match.group(1) if nickname_match else None
			
			follower_count_match = re.search(r'"followerCount":(\d+)', content)
			follower_count = follower_count_match.group(1) if follower_count_match else None
			
			following_count_match = re.search(r'"followingCount":(\d+)', content)
			following_count = following_count_match.group(1) if following_count_match else None
			
			heart_count_match = re.search(r'"heartCount":(\d+)', content)
			heart_count = heart_count_match.group(1) if heart_count_match else None
			
			avatar_url_match = re.search(r'"avatarLarger":"([^"]+)"', content)
			avatar_url = avatar_url_match.group(1).replace(r'\u002F', '/') if avatar_url_match else None
			
			video_count_match = re.search(r'"videoCount":(\d+)', content)
			video_count = video_count_match.group(1) if video_count_match else None
			
			bio_match = re.search(r'"signature":"([^"]+)"', content)
			bio = bio_match.group(1) if bio_match else None
			verified_match = re.search(r'"verified":(\w+)', content)
			verified = verified_match.group(1) if verified_match else None
			if user_id == None and unique_id == None and nickname == None and follower_count == None and following_count == None and heart_count == None and avatar_url == None and video_count == None and verified == None and bio == None:
				data = {"status_code": 400}
				json_string = json.dumps(data)
				return json_string
			else:
				data = {"status_code": 200, "info": {"user_id": user_id, "unique_id": unique_id, "nickname": nickname, "follower": follower_count, "following": following_count, "hearts": heart_count, "avatar": avatar_url, "video": video_count, "verified": verified, "bio": bio}}
				json_string = json.dumps(data, ensure_ascii=False)
				return json_string
		except:
			data = {"status_code": 400}
			json_string = json.dumps(data)
			return json_string
		
	def video(url):
		try:
			if "https://vt.tiktok.com/" in url:
				headers = {
				    'authority': 'ytshorts.savetube.me',
				    'accept': 'application/json, text/plain, */*',
				    'accept-language': 'ar-IQ,ar;q=0.9,en-US;q=0.8,en;q=0.7',
				    'content-type': 'application/json',
				    'origin': 'https://ytshorts.savetube.me',
				    'referer': 'https://ytshorts.savetube.me/ar/tiktok-downloader-online?id=521909177',
				    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
				    'sec-ch-ua-mobile': '?1',
				    'sec-ch-ua-platform': '"Android"',
				    'sec-fetch-dest': 'empty',
				    'sec-fetch-mode': 'cors',
				    'sec-fetch-site': 'same-origin',
				    'user-agent': str(generate_user_agent()),
				}
				json_data = {
				    'url': url,
				}
				
				res = requests.post('https://ytshorts.savetube.me/api/v1/tiktok-downloader', headers=headers, json=json_data).json()
				video = res["response"]["resolutions"]["HD Video"]
				thumbnail = res["response"]["thumbnail"]
				data = {"status_code": 200, "data": {"video": video, "thumbnail": thumbnail}}
				json_string = json.dumps(data)
				return json_string
			else:
				data = {"status_code": 400}
				json_string = json.dumps(data)
				return json_string
		except:
			data = {"status_code": 400}
			json_string = json.dumps(data)
			return json_string
		
	def image(url):
		try:
			if "https://vt.tiktok.com/" in url:
				headers = {
				    'authority': 'ytshorts.savetube.me',
				    'accept': 'application/json, text/plain, */*',
				    'accept-language': 'ar-IQ,ar;q=0.9,en-US;q=0.8,en;q=0.7',
				    'content-type': 'application/json',
				    'origin': 'https://ytshorts.savetube.me',
				    'referer': 'https://ytshorts.savetube.me/ar/tiktok-photo-downloader',
				    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
				    'sec-ch-ua-mobile': '?1',
				    'sec-ch-ua-platform': '"Android"',
				    'sec-fetch-dest': 'empty',
				    'sec-fetch-mode': 'cors',
				    'sec-fetch-site': 'same-origin',
				    'user-agent': str(generate_user_agent()),
				}
				
				json_data = {
				    'url': url,
				    'apiUrl': '/tiktok-picture-downloader',
				}
				res = requests.post('https://ytshorts.savetube.me/api/v1/downloader-api', headers=headers, json=json_data).json()
				images = res["response"]["images"]
				thumbnail = res["response"]["thumbnail"]
				title = res["response"]["title"]
				data = {"status_code": 200, "data": {"images": images, "thumbnail": thumbnail, "title": title}}
				json_string = json.dumps(data)
				return json_string
			else:
				data = {"status_code": 400}
				json_string = json.dumps(data)
				return json_string
		except:
			data = {"status_code": 400}
			json_string = json.dumps(data)
			return json_string
class Instagram:
	@staticmethod
	def info(user):
		try:
			if "@" in user:
				user = str(user).replace("@", "")
			cookies = {
		        'mid': 'ZmfzjgALAAEnjB7-RAixescoB3z7',
		        'ig_did': 'EA8D00A2-81B9-47A0-B6AF-963A57C95154',
		        'datr': 'jvNnZtzL8MXVowB19i-f101u',
		        'ps_n': '1',
		        'ps_l': '1',
		        'ig_nrcb': '1',
		        'csrftoken': 'mFcLz5S7aKKvWLBOWjTVqtpJAGYmjgqg',
		        'ds_user_id': '51221166926',
		        'shbid': '"3394\\05451221166926\\0541750359334:01f7f147c8a86f07bad755288e89f7ba9a3f63f9c510c51ad232b91242ada7b803f1b10c"',
		        'shbts': '"1718823334\\05451221166926\\0541750359334:01f7fff7ce057a3c7843501337d51bec1e6226ea67399d53bb2bed6de02f872acdcfe5ee"',
		        'fbm_124024574287414': 'base_domain=.instagram.com',
		        'fbsr_124024574287414': '2HnRAOYB6oY99gWlzHq7aURnMdXo5mL7jWxj0eHEoTo.eyJ1c2VyX2lkIjoiMTAwMDI3MDMzNTYxMTc2IiwiY29kZSI6IkFRRHJNZFhlRVpjQzlyMVVaSFVWeGNGQ0hHUF93OFRlVmg1TExEZ2IyT01YX1BxdlJnbUFLbUtCeFJBcm03NVdPMWt6OUMxYXVpcFkyWkRacThXWjBtOV9JcWVkdWNKeFhyN05nSzlWbVNBZ2VBcWh6VkhYS1RNZF9mR2hxVnZhazZ0VTJUb3dvRm40RHhNSjBNMU5paHFsczV6UlU1RDRiV1l4NXNqNTUzNHFXZTl0QXV4cjFwV1hmUTV0Y2RMRUN1WUtmOTBCM1pEQ2tzNlFYTjdUQ0lvNnM0d1R0OXVjNm0xaFdQa0lnNU9hcXJyQl95QXQ2czRiUG5Xd3hZeTd5c0h3R2lIZ3psYzRnV0Y1S2hyTjBuVmtsWEpsN08yUXRlc2JVN2tYN0p1dXdkR0FHT3BEQUNIeVVWREdlRF8wNkxUNVVoTzNSYk1iUGowNWNmQnBTSE81Iiwib2F1dGhfdG9rZW4iOiJFQUFCd3pMaXhuallCT3l4Q2xwQVFEMU9nU0kxZDFCbU9aQ21OS0xIZDljbHFnc1pBWTlPM2V1Z1pCcGxoVXFTYm0zYTFzQmZtVjdkUGtYWkNaQkthb2VOTFpCUGxHaFJNdk04R1FZWkFUY2dLaEd5NjVKTTAxWVpBOG9YSU5FS3lPTXZRT0h2TXpWdXlSdldBM01XS0xXek5mQUZXNUFTYkRmN24xWkFuU3RXcmw5SWZaQlVZU0hxMHpvNmVsQ3N1Qm5EY0ZaQjB2Y1pEIiwiYWxnb3JpdGhtIjoiSE1BQy1TSEEyNTYiLCJpc3N1ZWRfYXQiOjE3MTg4MjM4MzN9',
		        'rur': '"ODN\\05451221166926\\0541750359834:01f70bb4fb42d9e6636e765489fcaa8808f464fcb4c7fbc54471d07650a50f7522af191c"',
		        'fbsr_124024574287414': '2HnRAOYB6oY99gWlzHq7aURnMdXo5mL7jWxj0eHEoTo.eyJ1c2VyX2lkIjoiMTAwMDI3MDMzNTYxMTc2IiwiY29kZSI6IkFRRHJNZFhlRVpjQzlyMVVaSFVWeGNGQ0hHUF93OFRlVmg1TExEZ2IyT01YX1BxdlJnbUFLbUtCeFJBcm03NVdPMWt6OUMxYXVpcFkyWkRacThXWjBtOV9JcWVkdWNKeFhyN05nSzlWbVNBZ2VBcWh6VkhYS1RNZF9mR2hxVnZhazZ0VTJUb3dvRm40RHhNSjBNMU5paHFsczV6UlU1RDRiV1l4NXNqNTUzNHFXZTl0QXV4cjFwV1hmUTV0Y2RMRUN1WUtmOTBCM1pEQ2tzNlFYTjdUQ0lvNnM0d1R0OXVjNm0xaFdQa0lnNU9hcXJyQl95QXQ2czRiUG5Xd3hZeTd5c0h3R2lIZ3psYzRnV0Y1S2hyTjBuVmtsWEpsN08yUXRlc2JVN2tYN0p1dXdkR0FHT3BEQUNIeVVWREdlRF8wNkxUNVVoTzNSYk1iUGowNWNmQnBTSE81Iiwib2F1dGhfdG9rZW4iOiJFQUFCd3pMaXhuallCT3l4Q2xwQVFEMU9nU0kxZDFCbU9aQ21OS0xIZDljbHFnc1pBWTlPM2V1Z1pCcGxoVXFTYm0zYTFzQmZtVjdkUGtYWkNaQkthb2VOTFpCUGxHaFJNdk04R1FZWkFUY2dLaEd5NjVKTTAxWVpBOG9YSU5FS3lPTXZRT0h2TXpWdXlSdldBM01XS0xXek5mQUZXNUFTYkRmN24xWkFuU3RXcmw5SWZaQlVZU0hxMHpvNmVsQ3N1Qm5EY0ZaQjB2Y1pEIiwiYWxnb3JpdGhtIjoiSE1BQy1TSEEyNTYiLCJpc3N1ZWRfYXQiOjE3MTg4MjM4MzN9',
		        'wd': '811x633',
			}
			headers = {
		        'accept': '*/*',
		        'accept-language': 'ar-IQ,ar;q=0.9,en-US;q=0.8,en;q=0.7',
		        'priority': 'u=1, i',
		        'referer': 'https://www.instagram.com/dfff/',
		        'sec-ch-prefers-color-scheme': 'dark',
		        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
		        'sec-ch-ua-full-version-list': '"Not/A)Brand";v="8.0.0.0", "Chromium";v="126.0.6478.63", "Google Chrome";v="126.0.6478.63"',
		        'sec-ch-ua-mobile': '?0',
		        'sec-ch-ua-model': '""',
		        'sec-ch-ua-platform': '"Windows"',
		        'sec-ch-ua-platform-version': '"15.0.0"',
		        'sec-fetch-dest': 'empty',
		        'sec-fetch-mode': 'cors',
		        'sec-fetch-site': 'same-origin',
		        'user-agent': str(generate_user_agent()),
		        'x-asbd-id': '129477',
		        'x-csrftoken': 'mFcLz5S7aKKvWLBOWjTVqtpJAGYmjgqg',
		        'x-ig-app-id': '936619743392459',
		        'x-ig-www-claim': 'hmac.AR0fGZoPQ-j-C_EKa-30eRy8QiaGt06DMNBdwNzemsN0qW5C',
		        'x-requested-with': 'XMLHttpRequest',
			}
			params = {
			        'username': user,
			}
			response = requests.get(
			        'https://www.instagram.com/api/v1/users/web_profile_info/',
			        params=params,
			        cookies=cookies,
			        headers=headers,
			).json()
			name = response['data']['user']['full_name']
			username = response['data']['user']['username']
			bio = response['data']['user']['biography']
			id = response['data']['user']['id']
			followers = response['data']['user']['edge_followed_by']['count']
			following = response['data']['user']['edge_follow']['count']
			posts = response['data']['user']['edge_owner_to_timeline_media']['count']
			data = {"status_code": 200, "data": {"username": username, "name": name, "UID": id, "followers": followers, "following": following, "posts": posts, "bio": bio}}
			json_string = json.dumps(data)
			return json_string
		except:
			data = {"status_code": 400}
			json_string = json.dumps(data)
			return json_string
			
	def reset(email):
		try:
			if "@gmail.com" in email:
				url = 'https://www.instagram.com/accounts/account_recovery_send_ajax/'
				headers = {
				'accept': '*/*',
				'accept-encoding': 'gzip, deflate, br',
				'accept-language': 'ar,en-US;q=0.9,en;q=0.8',
				'content-length': '95',
				'content-type': 'application/x-www-form-urlencoded',
				'cookie': 'mid=Ypaq3AAEAAEIg549huD6OhdbB3BL; ig_did=5B9391EE-6FDB-4A05-851C-C678AAEBDA6C; ig_nrcb=1; datr=XOGYYoO6snvNKmgxjZ0ArAMI; csrftoken=Zj3ynb6WTBG2etZOvWCYCyIb75PLCJoP',
				'origin': 'https://www.instagram.com',
				'referer': 'https://www.instagram.com/accounts/password/reset/',
				'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
				'sec-ch-ua-mobile': '?0',
				'sec-ch-ua-platform': '"Windows"',
				'sec-fetch-dest': 'empty',
				'sec-fetch-mode': 'cors',
				'sec-fetch-site': 'same-origin',
				'user-agent': generate_user_agent(),
				'x-asbd-id': '198387',
				'x-csrftoken': 'Zj3ynb6WTBG2etZOvWCYCyIb75PLCJoP',
				'x-ig-app-id': '936619743392459',
				'x-ig-www-claim': '0',
				'x-instagram-ajax': 'fb462f0c47ed',
				'x-requested-with': 'XMLHttpRequest',
				}
				data ={
				'email_or_username': email,
				'recaptcha_challenge_field': '',
				'flow': '',
				'app_id': '',
				'source_account_id': '',
				}
				res = requests.post(url, headers=headers, data=data).json()
				if res["recovery_method"]:
					recovery_method = res["recovery_method"]
				else:recovery_method = None
				if res["can_recover_with_code"]:
					can_recover_with_code = res["can_recover_with_code"]
				else:can_recover_with_code = None
				if res["contact_point"]:
					contact_point = res["contact_point"]
				else:contact_point = None
				if res["toast_message"]:
					toast_message = res["toast_message"]
				else:toast_message = None
				data = {"status_code": 200, "data": {"recovery_method": recovery_method, "can_recover_with_code": can_recover_with_code, "contact_point": contact_point, "toast_message": toast_message}}
				json_string = json.dumps(data, ensure_ascii=False)
				return json_string
			else:
				data = {"status_code": 400}
				json_string = json.dumps(data)
				return json_string
		except:
			data = {"status_code": 400}
			json_string = json.dumps(data)
			return json_string
			
def Telegram_Support(text):
	if "str" in str(type(text)):
		rand = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
		email = str(''.join(random.choice(rand) for i in range(int(random.randint(6,9)))))+random.choice(["@gmail.com","@hotmail.com","@yahoo.com","@live.com"])
		rand = ["1","2","3","4","5","6","7","8","9","0"]
		rand_num = str(''.join(random.choice(rand) for i in range(int((10)))))
		phone_1 = "+1"+rand_num
		phone_2 = "+7"+rand_num
		phone_3 = "+44"+rand_num
		phonse = phone_1,phone_2,phone_3
		phone = random.choice(phonse)
		Countries = "English","Español","Français","Italiano","Українська"
		country = random.choice(Countries)
		
		cookies = {
			'cookie': 'stel_ssid=e903cc958eed67339f_11355632487222066292'
		}
		headers = {
		    'authority': 'telegram.org',
		    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
		    'accept-language': 'ar-IQ,ar;q=0.9,en-US;q=0.8,en;q=0.7',
		    'cache-control': 'max-age=0',
		    'content-type': 'application/x-www-form-urlencoded',
		    'origin': 'https://telegram.org',
		    'referer': 'https://telegram.org/support',
		    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
		    'sec-ch-ua-mobile': '?1',
		    'sec-ch-ua-platform': '"Android"',
		    'sec-fetch-dest': 'document',
		    'sec-fetch-mode': 'navigate',
		    'sec-fetch-site': 'same-origin',
		    'sec-fetch-user': '?1',
		    'upgrade-insecure-requests': '1',
		    'user-agent': str(generate_user_agent()),
		}
		data = {
		    'message': text,
		    'email': email,
		    'phone': phone,
		    'setln': country,
		}
		try:
			response = requests.post('https://telegram.org/support', headers=headers, cookies=cookies, data=data).text
		except requests.exceptions.ConnectionError:
			Telegram_Support(text)
		res_get = re.compile(r'<div class="alert alert-success"><b>(.*?)</b><br/>(.*?)</div>', re.DOTALL)
		match = res_get.search(response)
		if match:
			responses = match.group(1) + " " + match.group(2)
			rand = ["1","2","3","4","5","6","7","8","9","0"]
			rand_num = str(''.join(random.choice(rand) for i in range(int((10)))))
			if "شكرًا على بلاغك&#33; سنحاول الرّد بأسرع ما يمكن." in responses:
				data = {"status_code": 200, "data": {"message": "Success"}}
				json_string = json.dumps(data)
				return json_string
			else:
				data = {"status_code": 200, "data": {"message": "unSuccess"}}
				json_string = json.dumps(data)
				return json_string
		else:
			data = {"status_code": 200, "data": {"message": "try again later ."}}
			json_string = json.dumps(data)
	else:
		data = {"status_code": 400}
		json_string = json.dumps(data)