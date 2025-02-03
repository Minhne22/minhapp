import httpx
import aiofiles
import asyncio
from pymongo import MongoClient
import datetime
import random
import threading
import os

time_delay = 5

client = MongoClient("mongodb+srv://hahawelookcat:iXdyJYg1PSV140SZ@cluster0.my3yb.mongodb.net/")
if not os.path.exists('./uid.cache'):
    open('./uid.cache', 'w+').close()
uid_cache = open('./uid.cache', encoding='utf8').read()


db = client["fb_cmt_manage"]

proxy_collection = db["proxies"]
link_collection = db["facebook_links"]
comment_collection = db["user"]
token_collection = db["tokens"]

async def get_comment_func(link_post, proxy={}, credential={}):
    global uid_cache
    # Config Session
    ipport = f'{proxy["ip"]}:{proxy["port"]}' if not proxy['user'] else f'{proxy["user"]}:{proxy["password"]}@{proxy["ip"]}:{proxy["port"]}'
    # proxy = {
    #     'http': f'http://{ipport}',
    #     'https': f'http://{ipport}'
    # }
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': 'datr=W06SZ_48TKb0XgBDj5NmAmV4; sb=W06SZweBwrhWi9P0gH85_X0b; dpr=1.5; wd=819x551',
        'dpr': '1.5',
        'priority': 'u=0, i',
        'sec-ch-prefers-color-scheme': 'light',
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
        'sec-ch-ua-full-version-list': '"Not A(Brand";v="8.0.0.0", "Chromium";v="132.0.6834.110", "Google Chrome";v="132.0.6834.110"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-platform-version': '"19.0.0"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'viewport-width': '819',
    }
    
    session = httpx.AsyncClient(proxy=f'http://{ipport}', headers=headers)

    
    # cookies = {
    #     'datr': 'W06SZ_48TKb0XgBDj5NmAmV4',
    #     'sb': 'W06SZweBwrhWi9P0gH85_X0b',
    #     'dpr': '1.5',
    #     'wd': '819x551',
    # }
    
    # session.cookies.update(cookies)
    try:
        response = await session.get(
            link_post
        )
        
        response = response.text
        
        # with open('./main.html', 'w+', encoding='utf8') as f:
        #     f.write(response)
        
        post_id = response.split('"parent_feedback":{"id":"')[1].split('"')[0] if '"parent_feedback":{"id":"' in response \
            else response.split("'parent_feedback': {'id': '")[1].split('\'')[0]
        pid = response.split('"post_id":"')[1].split('"')[0] if '"post_id":"' in response\
            else response.split("'post_id': '")[1].split('\'')[0]
        
        
        lsd = response.split('"LSD",[],{"token":"')[1].split('"')[0] if '"LSD",[],{"token":"' in response else \
                response.split("['LSD', [], {'token': '")[1].split('\'')[0]
        
        data = {
            'av': '0',
            '__aaid': '0',
            '__user': '0',
            '__a': '1',
            '__req': 's',
            '__hs': '',
            'dpr': '1',
            '__ccg': 'GOOD',
            '__rev': '',
            '__s': '',
            '__hsi': '',
            '__dyn': '',
            '__csr': '',
            '__comet_req': '15',
            'lsd': lsd,
            'jazoest': '2914',
            '__spin_r': '',
            '__spin_b': '',
            '__spin_t': '',
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'CommentListComponentsRootQuery',
            'variables': '{"commentsIntentToken":"RECENT_ACTIVITY_INTENT_V1","feedLocation":"TAHOE","feedbackSource":2,"focusCommentID":null,"scale":1,"useDefaultActor":false,"id":"' + post_id + '","__relay_internal__pv__IsWorkUserrelayprovider":false}',
            'server_timestamps': 'true',
            'doc_id': '8894656107282580',
        }
        
        response = await session.post(
            'https://www.facebook.com/api/graphql/',
            data=data
        )
        
        response = response.json()
        
        # with open('./main.json', 'w+', encoding='utf8') as f:
        #     f.write(json.dumps(response))
        
        comment = response['data']['node']['comment_rendering_instance_for_feed_location']['comments']['edges'][0]
        info = comment['node']
        try: 
            data = {
                'post_id': pid,
                'text': info['body']['text'],
                'name': info['author']['name'],
                'time': info['comment_action_links'][0]['comment']['created_time'],
                'author_id': info['discoverable_identity_badges_web'][0]['serialized'].split('actor_id')[1].split(':')[1].split(',')[0]
            }
        
        except IndexError:
            link_pro5 = str(info['author']['id'])
            if link_pro5.isnumeric():
                uid = link_pro5
            else:
                if link_pro5 in uid_cache:
                    uid = uid_cache.split(f'{link_pro5}|')[1].split('\n')[0]
                else:
                    data = {
                        'link': f'https://www.facebook.com/{link_pro5}',
                    }
                    while True:
                        response = await session.post('https://id.traodoisub.com/api.php', data=data)
                        response = response.json()
                        if 'id' not in response:
                            await asyncio.sleep(3)
                            print('Get lai ID')
                        else:
                            print('Done')
                            break
                            
                    uid = response['id']
                    uid_cache += f'{link_pro5}|{uid}\n'
                    with open('./uid.cache', 'w+', encoding='utf8') as f:
                        f.write(uid_cache)
            
            
            data = {
                'post_id': pid,
                'text': info['body']['text'],
                'name': info['author']['name'],
                'time': info['comment_action_links'][0]['comment']['created_time'],
                'author_id': uid
            }
        
        await session.aclose()
        
        return data
    
    except IndexError:
        with open('main.txt', 'w+', encoding='utf8') as f:
            f.write(response)
        post_id = response.split('"story_token":"')[1].split('"')[0] if '"story_token":"' in response\
            else response.split("'story_token': '")[1].split('\'')[0]
        if '"group_id":"' in response:
            grid = response.split('"group_id":"')[1].split('"')[0] if '"group_id":"' in response\
                else response.split("'group_id': '")[1].split('\'')[0]
            pid = f'{grid}_{post_id}'
        else:
            pid = post_id
        cookie, token = credential['cookie'], credential['token']
        async with httpx.AsyncClient(proxy=f'http://{ipport}', headers={
                    'cookie': cookie
                }) as client:
            response = await client.get(
                f'https://graph.facebook.com/{pid}',
                params={
                    'access_token': token,
                    'order': 'reverse_chronological',
                    'fields': 'created_time,message,id,from'
                }
            )
            
            response = response.json()['data'][0]
        
        return {
                'post_id': post_id,
                'text': response['message'],
                'name': response['from']['name'],
                'time': response['created_time'].split('+')[0].replace('T', ' '),
                'author_id': response['from']['id']
            }
        
    except Exception as e:
        async with aiofiles.open('logs.txt', 'a+', encoding='utf8') as f:
            now = datetime.datetime.now()
            # Định dạng thời gian thành chuỗi
            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
            await f.write(f'[{formatted_time}] - {e}\n')
        return None


async def don_luong(link):
    try:
        data = await get_comment_func(link, random.choice(proxies), random.choice(credentials))
        print(data)
        if data:
            filter_condition = {"author_id": data["author_id"], "post_id": data["post_id"]}
            comment_collection.update_one(filter_condition, {"$set": data}, upsert=True)
    except Exception as e:
        async with aiofiles.open('logs.txt', 'a+', encoding='utf8') as f:
            now = datetime.datetime.now()
            # Định dạng thời gian thành chuỗi
            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
            await f.write(f'[{formatted_time}] - {e}\n')

async def quan_ly_luong():
    while True:
        global proxies, links, credentials
        tokens = list(token_collection.find())
        proxies = list(proxy_collection.find())
        links = list(link_collection.find())
        credentials = [
            x for x in tokens for x in tokens if x['status'] == 'live'
        ]
        tasks = []
        print(len(links))
        for url in links:
            # print(url)
            # Tạo và thêm các công việc vào danh sách tasks
            tasks.append(don_luong(url['url']))
        
        # Chờ tất cả các công việc trong tasks hoàn thành
        await asyncio.gather(*tasks)
        await asyncio.sleep(time_delay)
                
def start_background_task():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(quan_ly_luong())
    loop.run_forever()

thread = threading.Thread(target=start_background_task, daemon=True)
thread.start()
thread.join()
