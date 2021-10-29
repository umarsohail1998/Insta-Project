from instagram_private_api import Client, ClientCompatPatch, ClientCookieExpiredError, ClientLoginRequiredError, ClientChallengeRequiredError
from instagram_web_api import Client as Web_client
import hashlib
import urllib.request as urllib
import string
import random
import json
import codecs
import os
import datetime
import os.path
import time
import uuid
from dateutil.tz import tzoffset

settings_file_path = 'cache.txt'

user_name = 0 
password = 0

def init(u_name, pas):
    global user_name, password
    user_name = u_name
    password = pas

class MyWeb_client(Web_client):

    @staticmethod
    def _extract_rhx_gis(html):
        options = string.ascii_lowercase + string.digits
        text = ''.join([random.choice(options) for _ in range(8)])
        return hashlib.md5(text.encode()).hexdigest()

    def login(self):
        """Login to the web site."""
        if not self.username or not self.password:
            raise ClientError('username/password is blank')

        time = str(int(datetime.datetime.now().timestamp()))
        enc_password = f"#PWD_INSTAGRAM_BROWSER:0:{time}:{self.password}"

        params = {'username': self.username, 'enc_password': enc_password, 'queryParams': '{}', 'optIntoOneTap': False}
        self._init_rollout_hash()
        login_res = self._make_request('https://www.instagram.com/accounts/login/ajax/', params=params)
        if not login_res.get('status', '') == 'ok' or not login_res.get ('authenticated'):
            raise ClientLoginError('Unable to login')

        if self.on_login:
            on_login_callback = self.on_login
            on_login_callback(self)
        return login_res

def to_json(python_object):
    if isinstance(python_object, bytes):
        return {'__class__': 'bytes',
                '__value__': codecs.encode(python_object, 'base64').decode()}
    raise TypeError(repr(python_object) + ' is not JSON serializable')


def from_json(json_object):
    if '__class__' in json_object and json_object['__class__'] == 'bytes':
        return codecs.decode(json_object['__value__'].encode(), 'base64')
    return json_object


def onlogin_callback(api, new_settings_file):
    cache_settings = api.settings
    with open(new_settings_file, 'w') as outfile:
        json.dump(cache_settings, outfile, default=to_json)
        print('SAVED: {0!s}'.format(new_settings_file))

def get_web_api():
    cached_auth = None
    if ('WEB' + settings_file_path) and os.path.isfile(('WEB' + settings_file_path)):
        with open(('WEB' + settings_file_path)) as file_data:
            cached_auth = json.load(file_data, object_hook=from_json)

    api = None
    if not cached_auth and user_name and password:
        # Start afresh without existing auth
        try:
            print('New login.')
            api = MyWeb_client(
                auto_patch=True, drop_incompat_keys=False,
                username=user_name, password=password, authenticate=True)
        except Exception as e:
            print(e)

        cached_auth = api.settings

        # This auth cache can be re-used for up to 90 days
        with open(('WEB' + settings_file_path), 'w') as outfile:
            json.dump(cached_auth, outfile, default=to_json)

    elif cached_auth and user_name and password:
        try:
            print('Reuse login.')
            api = MyWeb_client(
                auto_patch=True, drop_incompat_keys=False,
                username=user_name,
                password=password,
                settings=cached_auth)
        except ClientCookieExpiredError:
            print('Cookie Expired. Please discard cached auth and login again.')

    return api

def get_api():
    try:
        
        settings_file = settings_file_path
        if not os.path.isfile(settings_file):
            # settings file does not exist
            print('Unable to find file: {0!s}'.format(settings_file))
            print('New Login')
            api = Client(
                user_name, password,
                on_login=lambda x: onlogin_callback(x, settings_file_path))
        else:
            with open(settings_file) as file_data:
                cached_settings = json.load(file_data, object_hook=from_json)
            print('Reusing settings: {0!s}'.format(settings_file))

            device_id = cached_settings.get('device_id')
            # reuse auth settings
            api = Client(
                user_name, password,
                settings=cached_settings)

    except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
        print('ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e))

        # Login expired
        # Do relogin but use default ua, keys and such
        api = Client(
            user_name, password,
            device_id=device_id,
            on_login=lambda x: onlogin_callback(x, settings_file_path))
    except Exception as e:
        print(e)
    return api

def download_file(url, path, attempt=0):
	try:
		urllib.urlretrieve(url, path)
		urllib.urlcleanup()
	except Exception as e:
		if not attempt == 3:
			attempt += 1
			print("[E] ({:d}) Download failed: {:s}.".format(attempt, str(e)))
			print("[W] Trying again in 5 seconds.")
			time.sleep(5)
			download_file(url, path, attempt)
		else:
			print("[E] Retry failed three times, skipping file.")
			print('-' * 70)

def username_to_id(username):
    api = get_api()

    time.sleep(random.randint(10, 200)/100)

    return api.username_info(username)['user']['pk']

def user_data(user):
    api = get_api()

    id = username_to_id(user)

    time.sleep(random.randint(10, 200)/100)

    info = api.user_info(id)

    time.sleep(random.randint(10, 200)/100)

    if not(os.path.exists(user)):
            os.mkdir(user)

    with open(f'{user}/info.txt', 'w+') as f:
        for key in info['user']:
            f.write(f'{key}: {info["user"][key]}\n')

    return info

def user_stories(username):
    api = get_api()
    try:
        id = username_to_id(username)
    except:
        print("May be Given username not found")
        return
    # print(id)
    time.sleep(random.randint(10, 200)/100)

    feed = api.user_story_feed(id)
    # print(feed)
    # print(type(feed))
    # return
    # with open('data.json', 'w') as fp:
    #     json.dump(feed, fp,  indent=4)
        
    isfound = False
    if feed['reel']:
        for reel in feed['reel']['items']:
            isfound=True

            list_video = []
            list_image = []

            is_video = 'video_versions' in reel and 'image_versions2' in reel

            if 'video_versions' in reel:
                    list_video.append([reel['video_versions'][0]['url']])
            if 'image_versions2' in reel:
                if not is_video:
                    list_image.append([reel['image_versions2']['candidates'][0]['url']])

            name = username

            if list_image:
                u = list_image[0][0]
            else:
                u = list_video[0][0]

            index = u.index('_') - 1
            n = ''

            while True:
                if u[index] == '/':
                    break
                n += u[index]
                index -= 1

            # name += f'_{n}'
            name+='_'+reel['id'].split('_')[0]

            # value = datetime.datetime.fromtimestamp(reel["taken_at"]).replace(tzinfo=tzoffset("UTC+1",0))

            # name += f'_{value.strftime("%d-%m-%Y_%H-%M-%S")}'
            if 'location' in reel.keys():
                # name += "_#" + reel["location"]["short_name"].replace(' ', '_')
                name += "_#" + reel["location"]["name"]
                
                # with open('data.json', 'w') as fp:
                #     json.dump(feed, fp,  indent=4)
                    # raise "Error Found"

            if 'reel_mentions' in reel:
                for u in reel['reel_mentions']:
                    name += f'_@{u["user"]["username"]}'
            print(name)

            if not(os.path.exists(username)):
                os.mkdir(username)
            # if not(os.path.exists(f'{username}/stories')):
                # os.mkdir(f'{username}/stories')

            if list_video:
                # save_path = f'{username}/stories/{name}.mp4'
                save_path = f'{username}/{name}.mp4'
            else:
                # save_path = f'{username}/stories/{name}.jpg'
                save_path = f'{username}/{name}.jpg'

            if not os.path.exists(save_path):

                try:
                    if list_video:
                        download_file(list_video[0][0], save_path)

                    else:
                        download_file(list_image[0][0], save_path)


                except Exception as e:
                    print("[W] An error occurred while iterating video stories: " + str(e))            

            else:
                print("[I] Story already exists: {:s}".format(name))
    else:
        print("No Story Found")
    
def user_posts(username, ext=False):
    api = get_api()
    id = username_to_id(username)

    time.sleep(random.randint(10, 200)/100)

    posts = []

    max_id = 0

    while True:
        if max_id:
            p = api.user_feed(id, max_id=max_id)
        else:
            p = api.user_feed(id)

        posts += p['items']
        if max_id == None:
            break
        try:
            max_id = p['next_max_id']
        except:
            break

        print(max_id)

        if len(p['items']) == 0:
            break

        time.sleep(random.randint(10, 100)/100)

    for post in posts:
        user_download_post(post, username, ext)


def user_download_post(post, username, ext):

    if 'carousel_media' in post:
        for media in post['carousel_media']:

            list_video = []
            list_image = []

            is_video = 'video_versions' in media and 'image_versions2' in media

            if 'video_versions' in media:
                list_video.append([media['video_versions'][0]['url']])
            if 'image_versions2' in media:
                if not is_video:
                    list_image.append([media['image_versions2']['candidates'][0]['url']])

            if not(list_video or list_image):
                print(media)

            name = username

            name += str(media['pk'])

            value = datetime.datetime.fromtimestamp(post["taken_at"]).replace(tzinfo=tzoffset("UTC+1",0))
            value.strftime('%Y-%m-%d %H:%M:%S')
            name += f'_{value.strftime("%d-%m-%Y-%H-%M-%S")}'
            if 'location' in post.keys():
                name += "_#" + post["location"]["short_name"].replace(' ', '_')

            if not(os.path.exists(username)):
                    os.mkdir(username)
            if not(os.path.exists(f'{username}/posts')):
                os.mkdir(f'{username}/posts')

            if list_video:
                    save_path = f'{username}/posts/{name}.mp4'
            else:
                save_path = f'{username}/posts/{name}.jpg'

            if not os.path.exists(save_path):

                try:
                    if list_video:
                        download_file(list_video[0][0], save_path)

                    else:
                        download_file(list_image[0][0], save_path)


                except Exception as e:
                    print("[W] An error occurred while iterating video stories: " + str(e))
            else:
                print("[I] Story already exists: {:s}".format(name))
    else:
        list_video = []
        list_image = []

        is_video = 'video_versions' in post and 'image_versions2' in post

        if 'video_versions' in post:
            list_video.append([post['video_versions'][0]['url']])
        if 'image_versions2' in post:
            if not is_video:
                list_image.append([post['image_versions2']['candidates'][0]['url']])

        name = username

        name += str(post['pk'])

        if not(list_video or list_image):
                print(post)

        value = datetime.datetime.fromtimestamp(post["taken_at"]).replace(tzinfo=tzoffset("UTC+1",0))
        value.strftime('%Y-%m-%d %H:%M:%S')
        name += f'_{value.strftime("%d-%m-%Y-%H-%M-%S")}'
        if 'location' in post.keys():
            name += "_#" + post["location"]["short_name"].replace(' ', '_')

        if not(os.path.exists(username)):
                os.mkdir(username)
        if not(os.path.exists(f'{username}/posts')):
            os.mkdir(f'{username}/posts')

        if list_video:
                save_path = f'{username}/posts/{name}.mp4'
        else:
            save_path = f'{username}/posts/{name}.jpg'

        if not os.path.exists(save_path):

            try:
                if list_video:
                    download_file(list_video[0][0], save_path)

                else:
                    download_file(list_image[0][0], save_path)


            except Exception as e:
                print("[W] An error occurred while iterating video stories: " + str(e))
        else:
            print("[I] Story already exists: {:s}".format(name))
            
    '''
    if ext:
        print(post.keys())
        try:
            download_post_likers(post, username, (name + '_LIKERS'))
        except:
            pass'''

def download_post_likers(post, username, name):
    with open(f'{username}/posts/{name}.txt', 'w+') as f:
        for liker in post['likers']:
            f.write((liker + '\n'))

def user_highlights(username):
    api = get_api()
    web_api = get_web_api()
    id = username_to_id(username)

    time.sleep(random.randint(10, 200)/100)

    feed = api.highlights_user_feed(id)

    ids = []

    for tray in feed['tray']:
        ids.append(tray['id'][10:])

    highlights = web_api.highlight_reel_media(ids)
    for highlight in highlights['data']['reels_media']:

        name = highlight['owner']['username']

        url = highlight['items'][0]['video_resources'][0]['src']

        index = url.index('_') - 1
        n = ''

        while True:
            if url[index] == '/':
                break
            n += url[index]
            index -= 1

        name += f'_{n}'

        value = datetime.datetime.fromtimestamp(highlight['items'][0]["taken_at_timestamp"]).replace(tzinfo=tzoffset("UTC+1",0))
        name += f'_{value.strftime("%d-%m-%Y_%H-%M-%S")}'

        name += '.mp4'

        print('SUKA')
        if not(os.path.exists(username)):
            print('SUKABLYAT')
            os.mkdir(username)
        if not(os.path.exists(f'{username}/highlights')):
            print('SUKANAHUI')
            os.mkdir(f'{username}/highlights')

        save_path = f'{username}/highlights/{name}'
        download_file(url, save_path)

    return highlights

def download_followers(username):
    api = get_api()
    id = username_to_id(username)

    time.sleep(random.randint(10, 200)/100)

    users = []
    max_id = 0

    while True:
        if max_id:
            us = api.user_followers(id, api.generate_uuid(seed='gay'), max_id=max_id)
        else:
            us = api.user_followers(id, api.generate_uuid(seed='gay'))

        users += us['users']
        if max_id == None:
            break
        try:
            max_id = us['next_max_id']
        except:
            break

        if len(us['users']) == 0:
            break

        time.sleep(random.randint(10, 200)/100)

    if not(os.path.exists(username)):
            os.mkdir(username)
    if not(os.path.exists(f'{username}/followers')):
        os.mkdir(f'{username}/followers')

    with open(f'{username}/followers/followers.txt', 'w+') as f:
        for user in users:
            f.write((user['username'] + '\n'))

def download_following(username):
    api = get_api()
    id = username_to_id(username)

    time.sleep(random.randint(10, 200)/100)

    users = []
    max_id = 0

    while True:
        if max_id:
            us = api.user_following(id, api.generate_uuid(seed='gay'), max_id=max_id)
        else:
            us = api.user_following(id, api.generate_uuid(seed='gay'))

        users += us['users']
        if max_id == None:
            break
        try:
            max_id = us['next_max_id']
        except:
            break

        print(max_id)

        if len(us['users']) == 0:
            break

        time.sleep(random.randint(10, 100)/100)

    if not(os.path.exists(username)):
            os.mkdir(username)
    if not(os.path.exists(f'{username}/followers')):
        os.mkdir(f'{username}/followers')

    with open(f'{username}/followers/following.txt', 'w+') as f:
        for user in users:
            f.write((user['username'] + '\n'))

def follow(username):
    api = get_api()
    id = username_to_id(username)

    time.sleep(random.randint(10, 200)/100)

    friendships_create(id)

def getLikers(username,limit,post=1):

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)

    driver.get('https://www.instagram.com/' + post)

    time.sleep(2)
    #Open Dialog
    followersLinkX = driver.find_element_by_xpath('//button[@class="sqdOP yWX7d     _8A5w5    "]')
    followersLinkX.click()
    time.sleep(1)
    #Get Dialog
    xxx = driver.find_element_by_xpath('//div[@role="dialog"]/div[1]/div[2]/div[1]/div[1]')
    #Focus on and Scroll
    xxx.click()
    # step 3
    actionChain = webdriver.ActionChains(driver)

    count = 0

    while(count < limit):
        for i in range(1,1000):
            try:
                users.append(driver.find_element_by_xpath('//div[@role="dialog"]/div[1]/div[2]/div[1]/div[1]/div['+ str(i) +']/div[2]/div[1]/div[1]').text)
                count+=1
            except:
                break
        actionChain.key_down(Keys.SPACE).key_up(Keys.SPACE).perform()
        time.sleep(0.5)

    return users