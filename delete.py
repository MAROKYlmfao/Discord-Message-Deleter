import requests, json, time, os, threading, base64

os.system("cls")
channel_id = input("Channel id: ")
TOKEN = input("Your discord token: ")
path = './proxy.txt'
if os.path.exists(path):
    with open("proxy.txt", "r") as f:
        proxy = f.readlines()
        proxy = proxy[0]
else:
    proxyask = input("Do you want to use proxy? y/n: ")
    if proxyask.lower() == "y":
        with open("proxy.txt", "w") as f:
            f.write("user:pass@ip:port")
            f.close()
        os.system("cls")
        print("\nProcess closed. Add your proxy to `proxy.txt` and start again.")
        time.sleep(3)
        exit()
    else:
        os.system("cls")
        print("\nProcess using local ip...")
        proxy = None

print("\nYour discord token wont be saved/used anywhere else. Its only for the request to find your account.")
print("\nStarting...")
time.sleep(3)


xsuper = "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEwMS4yNDAuOTUgKEludGVybmV0KS5TY3JpcHQvMTAuMDsgV2Ugbm8t) {x-super}"

headers = {
    "Authorization": TOKEN,
    "Connection": "keep-alive",
    "Content-Length": "0",
    "Host": "discord.com",
    "Origin": "https://discord.com",
    "Referer": "https://discord.com/channels/@me",
    "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "X-Debug-Options": "bugReporterEnabled",
    "X-Discord-Locale": "en-US",
    "X-Discord-Timezone": "Asia/Colombo",
    "X-Super-Properties": xsuper
}



def get_user_id(token, headers, proxy):
    if proxy == None:
        response = requests.get("https://discord.com/api/v10/users/@me", headers=headers)
    else:
        proxylist = {
            "http://":proxy,
            "https://":proxy
        }
        response = requests.get("https://discord.com/api/v10/users/@me", headers=headers, proxies=proxylist)

    if response.status_code == 200:
        user_data = response.json()
        user_id = user_data['id']
        return user_id
    else:
        print("Failed to get user information. Check your token.")
        return None

def get_messages(channel_id, your_user_id, proxy):
    
    message_ids = []
    before_message_id = None

    for _ in range(10):
        try:
            params = {
                "limit": 100,
                "before": before_message_id
            }
            if proxy == None:
                t = requests.get(url=f"https://discord.com/api/v9/channels/{channel_id}/messages", headers=headers, params=params)
            else:
                proxylist = {
                    "http://":proxy,
                    "https://":proxy
                }
                t = requests.get(url=f"https://discord.com/api/v9/channels/{channel_id}/messages", headers=headers, params=params, proxies=proxylist)

            if t.status_code == 200:
                messages = t.json()

                if not messages:
                    break

                for message in messages:
                    if message["author"]["id"] == your_user_id:
                        message_ids.append(message["id"])
                        print(f"Grabbed message: {message['id']}")

                before_message_id = messages[-1]["id"]
            else:
                print(f"Failed to retrieve messages. Status code: {t.status_code}")
                break
        except Exception as e:
            print(f"Error: {str(e)}")

    return message_ids


def delete(message_id, channel_id, proxy=None):
    global rate_limit_reset

    if proxy is None:
        t = requests.delete(url=f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}", headers=headers)
    else:
        proxylist = {
            "http": proxy,
            "https": proxy
        }
        t = requests.delete(url=f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}", headers=headers, proxies=proxylist)

    if t.status_code == 204:
        print(f"Deleted Message: {message_id}")
    elif t.status_code == 429:
        retry_after = int(t.headers.get('Retry-After', 0))
        print(f"!RETRY! RATE LIMIT!! Waiting {retry_after} seconds")
        time.sleep(retry_after)
        delete(message_id, channel_id, proxy)
    elif t.status_code == 403:
        print("Cannot delete system message.")
    else:
        print(f"Error: {t.status_code}")
        print(t.text)

your_user_id = get_user_id(TOKEN, headers, proxy)
message_ids = get_messages(channel_id, your_user_id, proxy)
print("\nGrabbed all messages...")
time.sleep(3)
threadarray = []
for message_id in message_ids:
    time.sleep(0.3)
    thread = threading.Thread(target=delete, args=(message_id, channel_id, proxy,), daemon=False)
    thread.start()
    threadarray.append(thread)

for thread in threadarray:
    thread.join()
    

print("Done. :)")
