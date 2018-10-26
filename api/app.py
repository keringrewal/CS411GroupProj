from instagram.client import InstagramAPI

access_token = "14089449.89b4fdb.3d5bf5cc1d0642b5a2571a24e6cab38a"
client_secret = "e0da15aecf104b498ea16f13fff8c53d"
api = InstagramAPI(access_token=access_token, client_secret=client_secret)
x = api.user_search('keringrewal')
print(x)
recent_media= api.user_recent_media(user_id="userid", count=10)
for media in recent_media:
   print(media.caption.text)


api_token = "14089449.89b4fdb.3d5bf5cc1d0642b5a2571a24e6cab38a"

api_url_base = "https://api.instagram.com/v1/media/popular?access_token=" + api_token
