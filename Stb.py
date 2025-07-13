# tatasky_m3u_generator.py
import requests
import time

BASE_URL = "http://play.tatasky.xyz/stalker_portal/c/"
MAC_ADDRESS = "00:1A:79:00:00:9F"
SN = "D2DF98F4AE9C4"
DEVICE_ID = "6DF3279B906BFC94AE027940C1DA84B87AA0CF24A5FA591DC8C7FB310642DAD9"
STB_TYPE = "MAG270"
OUTPUT_M3U = "tatasky_channels.m3u"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C)",
    "X-User-Agent": f"Model: {STB_TYPE}; Link: Ethernet",
    "Authorization": "",
    "Referer": f"{BASE_URL}index.html",
    "Cookie": f"mac={MAC_ADDRESS}; stb_lang=en; timezone=Asia/Kolkata"
}

session = requests.Session()
session.headers.update(HEADERS)

def get_auth_token(retries=3, delay=2):
    url = f"{BASE_URL}auth/get_token?JsHttpRequest=1-xml"
    params = {
        "device_id": DEVICE_ID,
        "device_id2": DEVICE_ID,
        "mac": MAC_ADDRESS,
        "sn": SN
    }
    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, params=params)
            if resp.status_code != 200:
                print(f"[❌] Attempt {attempt}: HTTP {resp.status_code}")
                print(resp.text)
                time.sleep(delay)
                continue

            json_data = resp.json()
            token = json_data['js']['token']
            print(f"[✅] Authenticated successfully. Token: {token}")
            return token
        except Exception as e:
            print(f"[❌] Attempt {attempt}: Failed to parse JSON.")
            print("Response content:", resp.text)
            if attempt < retries:
                print(f"[🔁] Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise e

def get_profile(token):
    session.get(f"{BASE_URL}portal.php", params={
        "type": "stb", "action": "handshake", "token": token, "JsHttpRequest": "1-xml"
    })
    session.get(f"{BASE_URL}portal.php", params={
        "type": "stb", "action": "get_profile", "JsHttpRequest": "1-xml"
    })

def get_channels():
    r = session.get(f"{BASE_URL}portal.php", params={
        "type": "itv", "action": "get_all_channels", "JsHttpRequest": "1-xml"
    })
    try:
        return r.json()["js"]["data"]
    except Exception:
        print("[❌] Failed to fetch or parse channel list.")
        print("Response content:", r.text)
        raise

def generate_m3u(channels):
    with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
        f.write("#EXTM3U
")
        for ch in channels:
            name = ch.get("name", "NoName")
            logo = ch.get("logo", "")
            cmd = ch.get("cmd", "")
            stream_url = BASE_URL + cmd.replace("ffmpeg ", "").strip()
            f.write(f'#EXTINF:-1 tvg-logo="{logo}",{name}
{stream_url}
')
    print(f"[📁] M3U file saved as: {OUTPUT_M3U}")

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
