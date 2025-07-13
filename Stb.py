import requests
import json
import time

# === Configuration ===
BASE_URL = "http://play.tatasky.xyz/stalker_portal/c/"
MAC_ADDRESS = "00:1A:79:00:00:9F"
SN = "D2DF98F4AE9C4"
DEVICE_ID = "6DF3279B906BFC94AE027940C1DA84B87AA0CF24A5FA591DC8C7FB310642DAD9"
STB_TYPE = "MAG270"
OUTPUT_M3U = "tatasky_channels.m3u"

# === Headers and Cookies ===
HEADERS = {
    "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C)",
    "X-User-Agent": f"Model: {STB_TYPE}; Link: Ethernet",
    "Authorization": "",
    "Referer": f"{BASE_URL}index.html",
    "Cookie": f"mac={MAC_ADDRESS}; stb_lang=en; timezone=Asia/Kolkata"
}

session = requests.Session()
session.headers.update(HEADERS)

# === Step 1: Auth ===
def get_auth_token():
    url = f"{BASE_URL}auth/get_token?JsHttpRequest=1-xml"
    params = {
        "device_id": DEVICE_ID,
        "device_id2": DEVICE_ID,
        "mac": MAC_ADDRESS,
        "sn": SN
    }
    resp = session.get(url, params=params)
    token = resp.json()['js']['token']
    return token

# === Step 2: Get Profile Info (includes available services) ===
def get_profile(token):
    url = f"{BASE_URL}portal.php"
    params = {
        "type": "stb",
        "action": "handshake",
        "token": token,
        "JsHttpRequest": "1-xml"
    }
    session.get(url, params=params)

    url = f"{BASE_URL}portal.php"
    params = {
        "type": "stb",
        "action": "get_profile",
        "JsHttpRequest": "1-xml"
    }
    r = session.get(url, params=params)
    return r.json()

# === Step 3: Fetch Available Channels ===
def get_channels():
    url = f"{BASE_URL}portal.php"
    params = {
        "type": "itv",
        "action": "get_all_channels",
        "JsHttpRequest": "1-xml"
    }
    r = session.get(url, params=params)
    return r.json()["js"]["data"]

# === Step 4: Generate M3U Playlist ===
def generate_m3u(channels):
    with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch in channels:
            name = ch.get("name", "NoName")
            logo = ch.get("logo", "")
            cmd = ch.get("cmd", "")
            stream_url = BASE_URL + cmd.replace("ffmpeg ", "").strip()
            f.write(f'#EXTINF:-1 tvg-logo="{logo}",{name}\n{stream_url}\n')
    print(f"[✅] M3U file saved: {OUTPUT_M3U}")

# === Main Execution ===
def main():
    print("[🔑] Authenticating...")
    token = get_auth_token()
    print("[📡] Fetching profile...")
    get_profile(token)
    print("[📺] Fetching channels list...")
    channels = get_channels()
    print(f"[📃] Total channels fetched: {len(channels)}")
    generate_m3u(channels)

if __name__ == "__main__":
    main()
