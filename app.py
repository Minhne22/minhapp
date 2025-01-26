from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime
import requests
import json
from threading import Thread
import random
import time


app = Flask(__name__)
app.secret_key = "supersecretkey"
socketio = SocketIO(app)

# Kết nối MongoDB
client = MongoClient("mongodb+srv://hahawelookcat:iXdyJYg1PSV140SZ@cluster0.my3yb.mongodb.net/")

db = client["fb_cmt_manage"]

proxy_collection = db["proxies"]
link_collection = db["facebook_links"]
comment_collection = db["user"]
token_collection = db["tokens"]



# ==========================
# Quản lý hàm
# ==========================
def get_comment_func(link_post, proxy={}, credential={}):
    # Config Session
    session = requests.Session()
    ipport = f'{proxy["ip"]}:{proxy["port"]}' if not proxy['user'] else f'{proxy["user"]}:{proxy["password"]}@{proxy["ip"]}:{proxy["port"]}'
    proxy = {
        'http': f'http://{ipport}',
        'https': f'http://{ipport}'
    }
    session.proxies = proxy
    
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
    
    # cookies = {
    #     'datr': 'W06SZ_48TKb0XgBDj5NmAmV4',
    #     'sb': 'W06SZweBwrhWi9P0gH85_X0b',
    #     'dpr': '1.5',
    #     'wd': '819x551',
    # }
    
    session.headers.update(headers)
    # session.cookies.update(cookies)
    try:
        response = session.get(
            link_post
        ).text
        
        with open('./main.html', 'w+', encoding='utf8') as f:
            f.write(response)
        
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
        
        response = session.post(
            'https://www.facebook.com/api/graphql/',
            data=data
        ).json()
        
        with open('./main.json', 'w+', encoding='utf8') as f:
            f.write(json.dumps(response))
        
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
            link_pro5 = info['author']['id']
            print(link_pro5)
            # Get ID Int
            data = {
                'link': f'https://www.facebook.com/{link_pro5}',
            }

            response = session.post('https://id.traodoisub.com/api.php', data=data)
            print(response.text)
            uid = response.json()['id']
            
            data = {
                'post_id': pid,
                'text': info['body']['text'],
                'name': info['author']['name'],
                'time': info['comment_action_links'][0]['comment']['created_time'],
                'author_id': uid
            }
        
        return data
    
    except IndexError:
        post_id = response.split('"post_id":"')[1].split('"')[0] if '"post_id":"' in response\
            else response.split("'post_id': '")[1].split('\'')[0]
        if '"group_id":"' in response:
            grid = response.split('"group_id":"')[1].split('"')[0] if '"group_id":"' in response\
                else response.split("'group_id': '")[1].split('\'')[0]
            pid = f'{grid}_{post_id}'
        else:
            pid = post_id
        cookie, token = credential['cookie'], credential['token']
        response = requests.get(
            f'https://graph.facebook.com/{pid}',
            params={
                'access_token': token,
                'order': 'reverse_chronological',
                'fields': 'created_time,message,id,from'
            },
            headers={
                'cookie': cookie
            }
        ).json()['data'][0]
        
        return {
                'post_id': post_id,
                'text': response['message'],
                'name': response['from']['name'],
                'time': response['created_time'].split('+')[0].replace('T', ' '),
                'author_id': response['from']['id']
            }
        
    except Exception as e:
        with open('logs.txt', 'a+', encoding='utf8') as f:
            now = datetime.datetime.now()
            # Định dạng thời gian thành chuỗi
            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f'[{formatted_time}] - {e}\n')
        return None

def don_luong(link):
    # return
    while True:
        print(link)
        try:
            data = get_comment_func(link, random.choice(proxies), random.choice(credentials))
            print(data)
            if data:
                filter_condition = {"author_id": data["author_id"], "post_id": data["post_id"]}
                comment_collection.update_one(filter_condition, {"$set": data}, upsert=True)
        except Exception as e:
            with open('logs.txt', 'a+', encoding='utf8') as f:
                now = datetime.datetime.now()
                # Định dạng thời gian thành chuỗi
                formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f'[{formatted_time}] - {e}\n')
        time.sleep(time_delay)
                
                
        

# ==========================
# Quản lý Comment gần nhất (Trang chính)
# ==========================
@app.route("/")
def comments():
    comments = list(comment_collection.find().sort("time", -1).limit(10))
    print(comments)
    for comment in comments:
        # Định dạng thời gian (tùy chỉnh)
        comment["time"] = datetime.datetime.fromtimestamp(comment["time"]).strftime("%Y-%m-%d %H:%M:%S")
    return render_template("comments.html", comments=comments)

from flask import jsonify

@app.route("/comments/api", methods=["GET"])
def get_comments_api():
    comments = list(comment_collection.find().sort("time", -1))  # Sắp xếp theo thời gian mới nhất
    for comment in comments:
        comment["_id"] = str(comment["_id"])  # Convert ObjectId to string
    return jsonify(comments)


# ==========================
# Quản lý Proxy
# ==========================
@app.route("/proxies")
def proxies():
    global proxies
    proxies = list(proxy_collection.find())
    print(proxies)
    return render_template("proxies.html", proxies=proxies)

@app.route("/proxies/add", methods=["GET", "POST"])
def add_proxy():
    if request.method == "POST":
        proxy_data = request.form.get("proxy")

        if not proxy_data:
            flash("Vui lòng nhập thông tin proxy.", "error")
            return redirect(url_for("add_proxy"))

        # Phân tích chuỗi proxy (ip:port hoặc ip:port:user:pass)
        parts = proxy_data.split(":")
        if len(parts) == 2:  # Chỉ có IP và Port
            ip, port = parts
            user, password = None, None
        elif len(parts) == 4:  # Có IP, Port, User, Password
            ip, port, user, password = parts
        else:
            flash("Định dạng proxy không hợp lệ. Vui lòng sử dụng ip:port hoặc ip:port:user:pass.", "error")
            return redirect(url_for("add_proxy"))

        # Thêm vào cơ sở dữ liệu
        proxy_collection.insert_one({
            "ip": ip.strip(),
            "port": port.strip(),
            "user": user.strip() if user else None,
            "password": password.strip() if password else None
        })

        flash("Đã thêm proxy thành công!", "success")
        return redirect(url_for("proxies"))

    return render_template("add_proxy.html")


@app.route("/proxies/delete/<id>", methods=["POST"])
def delete_proxy(id):
    proxy_collection.delete_one({"_id": ObjectId(id)})
    flash("Đã xóa proxy thành công!", "success")
    return redirect(url_for("proxies"))

# ==========================
# Quản lý Link bài viết Facebook
# ==========================
@app.route("/links")
def links():
    global links
    links = list(link_collection.find())
    return render_template("links.html", links=links)

@app.route("/links/add", methods=["GET", "POST"])
def add_link():
    if request.method == "POST":
        url = request.form.get("url")
        description = request.form.get("description")

        if not url:
            flash("Vui lòng nhập URL bài viết.", "error")
            return redirect(url_for("add_link"))
        
        Thread(target=don_luong, args=(url, )).start()

        link_collection.insert_one({"url": url.strip(), "description": description.strip()})
        flash("Đã thêm link bài viết thành công!", "success")
        return redirect(url_for("links"))

    return render_template("add_link.html")

@app.route("/links/delete/<id>", methods=["POST"])
def delete_link(id):
    link_collection.delete_one({"_id": ObjectId(id)})
    flash("Đã xóa link bài viết thành công!", "success")
    return redirect(url_for("links"))

# ==========================
# Quản lý Cookie/Token
# ==========================
@app.route("/tokens", methods=["GET"])
def tokens():
    global credentials
    tokens = list(token_collection.find())
    # print(tokens)
    credentials = [
        x for x in tokens for x in tokens if x['status'] == 'live'
    ]
    # Rút gọn cookie và token trước khi gửi qua HTML
    for token in tokens:
        token["short_cookie"] = shorten_text(token["cookie"])
        tok = token.get("token")
        token["short_token"] = shorten_text(tok if tok else "Chưa có")
    return render_template("tokens.html", tokens=tokens)

@app.route("/tokens/add", methods=["POST"])
def add_tokens():
    cookies_data = request.form.get("cookie").strip()
    if not cookies_data:
        flash("Vui lòng nhập ít nhất một cookie.", "error")
        return redirect(url_for("tokens"))

    cookies = cookies_data.split("\n")  # Mỗi dòng là một cookie
    for cookie in cookies:
        cookie = cookie.strip()
        if cookie:
            # Kiểm tra trùng lặp trong database trước khi thêm
            if not token_collection.find_one({"cookie": cookie}):
                token_collection.insert_one({"cookie": cookie, "token": None, "status": "Chưa kiểm tra"})
    
    flash(f"Đã thêm {len(cookies)} cookie thành công!", "success")
    return redirect(url_for("tokens"))


@app.route("/tokens/delete/<id>", methods=["POST"])
def delete_token(id):
    token_collection.delete_one({"_id": ObjectId(id)})
    flash("Đã xóa cookie/token thành công!", "success")
    return redirect(url_for("tokens"))

@app.route("/tokens/get_token/<id>", methods=["POST"])
def get_token(id):
    # Lấy cookie từ database
    token_data = token_collection.find_one({"_id": ObjectId(id)})

    if not token_data:
        flash("Không tìm thấy cookie/token.", "error")
        return redirect(url_for("tokens"))

    cookie = token_data["cookie"]

    # Code giả lập xử lý lấy token từ cookie (thay bằng logic của bạn)
    # Ví dụ: Hàm `fetch_token_from_cookie` trả về token từ cookie
    try:
        token = fetch_token_from_cookie(cookie)  # Thay bằng logic thật của bạn
        if not token:
            flash("Không thể lấy token từ cookie.", "error")
            return redirect(url_for("tokens"))

        # Cập nhật token và trạng thái vào cơ sở dữ liệu
        token_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"token": token, "status": "live"}}
        )
        flash("Đã lấy token thành công!", "success")
    except Exception as e:
        token_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"status": "error"}}
        )
        flash(f"Không thể lấy token: {e}", "error")

    return redirect(url_for("tokens"))

def shorten_text(text, length=20):
    """
    Rút gọn chuỗi, giữ phần đầu và phần cuối.
    Ví dụ: "abcdef1234567890" → "abcde...7890"
    """
    if len(text) > length:
        return text[:length // 2] + "..." + text[-length // 2 :]
    return text


def fetch_token_from_cookie(cookie):
    """
    Giả lập xử lý lấy token từ cookie. Thay thế logic này bằng thực tế.
    """
    
    print(cookie)
    
    cookies = {
        x.split('=')[0]: x.split('=')[1]
        for x in cookie.replace(" ", "").split(';') if x
    }
    
    print(cookies)
        
    
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        # 'cookie': 'datr=QYuEZ_z_-ErmElrzCBe57uaW; sb=QYuEZ4lOEbFodz4x2Z-YGvqQ; ps_l=1; ps_n=1; locale=vi_VN; c_user=100034994394353; vpd=v1%3B464x310x2.0000000596046448; wl_cbv=v2%3Bclient_version%3A2723%3Btimestamp%3A1737643388; fbl_st=100421630%3BT%3A28960723; dpr=1.5; ar_debug=1; wd=1280x551; presence=EDvF3EtimeF1737868185EuserFA21B34994394353A2EstateFDutF0CEchF_7bCC; fr=11tikGa2z3xhZHECe.AWUtth9yIBR4qSXVTwCKIZDWeYo.BnlcPz..AAA.0.0.BnlcPz.AWWFU9_C4Bg; xs=16%3Amg6IEZfvivGF4A%3A2%3A1737636239%3A-1%3A6328%3A%3AAcVZ18h7ledKKNssXOHNTrvqhZ4j03a7yC-puBWgV7o; usida=eyJ2ZXIiOjEsImlkIjoiQXNxb2o1ZDFnM25mcG4iLCJ0aW1lIjoxNzM3ODY4Mzc5fQ%3D%3D',
        'priority': 'u=1, i',
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'none',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
    }

    response = requests.get('https://adsmanager.facebook.com/adsmanager/manage/campaigns', cookies=cookies, headers=headers).text

    
    # with open('./main.html', 'w+', encoding='utf8') as f:
    #     f.write(response)
    
    token = response.split('__accessToken="')[1].split('"')[0] if "__accessToken=" in response else None
    
    print(token)
    
    return token

if __name__ == "__main__":
    links = list(link_collection.find())
    proxies = list(proxy_collection.find())
    credentials = [x for x in list(token_collection.find()) if x['status'] == 'live']

    time_delay = 5
    
    for url in links:
        print(url)
        Thread(target=don_luong, args=(url['url'], )).start()
        time.sleep(2)
    socketio.run(app, '0.0.0.0', 443)
