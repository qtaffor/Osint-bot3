import telebot
import requests
import re
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# ===== КОНФИГ =====
TOKEN = "8605143642:AAHE0UQ3Y2A9KX9LW12MxNrX0KUpGjtRJ9U"
bot = telebot.TeleBot(TOKEN)

# ===== HTTP-ПИНГ ДЛЯ RENDER =====
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
def run_health_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()
threading.Thread(target=run_health_server, daemon=True).start()

# ===== ОСНОВНЫЕ ФУНКЦИИ ПРОБИВА =====

def get_operator_region(phone):
    clean = re.sub(r'[^0-9]', '', phone)
    if clean.startswith('7') and len(clean) == 11:
        code = clean[1:4]
        operators = {
            '910': 'МТС', '915': 'МТС', '916': 'МТС', '917': 'МТС', '918': 'МТС', '919': 'МТС',
            '920': 'МТС', '921': 'МТС', '922': 'МТС', '923': 'МТС', '924': 'МТС', '925': 'МТС',
            '926': 'МТС', '927': 'МТС', '928': 'МТС', '929': 'МТС', '930': 'МТС',
            '903': 'Билайн', '905': 'Билайн', '906': 'Билайн', '909': 'Билайн',
            '960': 'Билайн', '961': 'Билайн', '962': 'Билайн', '963': 'Билайн',
            '964': 'Билайн', '965': 'Билайн', '966': 'Билайн', '967': 'Билайн',
            '968': 'Билайн', '969': 'Билайн', '980': 'Билайн', '981': 'Билайн',
            '982': 'Билайн', '983': 'Билайн', '984': 'Билайн', '985': 'Билайн',
            '986': 'Билайн', '987': 'Билайн', '988': 'Билайн', '989': 'Билайн',
            '900': 'Мегафон', '902': 'Мегафон', '904': 'Мегафон', '908': 'Мегафон'
        }
        operator = operators.get(code, 'Неизвестный')
        msk_codes = ['495', '499', '903', '905', '906', '909', '910', '915', '916', '917', '918', '919',
                     '920', '921', '922', '923', '924', '925', '926', '927', '928', '929', '930']
        region = "Москва и область" if code in msk_codes else "Другой регион"
        return operator, region
    return "Неизвестный", "Неизвестный"

def check_telegram(username):
    try:
        url = f"https://t.me/{username.replace('@', '')}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and "tgme_page_extra" in r.text:
            return "Найден"
        return "Не найден"
    except:
        return "Ошибка"

def search_socials(username):
    """Ищет аккаунты на 5 основных платформах"""
    platforms = {
        "VK": f"https://vk.com/{username}",
        "Instagram": f"https://instagram.com/{username}",
        "TikTok": f"https://tiktok.com/@{username}",
        "YouTube": f"https://youtube.com/@{username}",
        "Twitter": f"https://twitter.com/{username}"
    }
    found = []
    for name, url in platforms.items():
        try:
            r = requests.get(url, timeout=3, allow_redirects=True)
            if r.status_code == 200:
                found.append(f"{name}: {url}")
        except:
            pass
        time.sleep(0.2)
    return found if found else ["Не найдено"]

def check_email_leaks(email):
    """Проверяет email через публичные утечки (mock)"""
    try:
        url = f"https://leakcheck.net/api/public?check={email}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get('found'):
                return f"Найдено в утечках: {data.get('sources', 'неизвестно')}"
            return "Не найдено в утечках"
    except:
        pass
    return "Ошибка проверки"

def get_phone_info(phone):
    """Собирает всё по номеру"""
    clean = re.sub(r'[^0-9]', '', phone)
    result = {"phone": clean, "operator": "", "region": "", "telegram": ""}
    if clean.startswith('7') and len(clean) == 11:
        result["operator"], result["region"] = get_operator_region(clean)
        result["telegram"] = check_telegram(clean)
    return result

# ===== КОМАНДЫ БОТА =====

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🚀 МАКСИМАЛЬНЫЙ OSINT-БОТ\n\n"
        "Отправь данные для полного пробива:\n"
        "- Телефон: 79151812030\n"
        "- Email: name@mail.com\n"
        "- Никнейм: @username\n\n"
        "Бот соберёт всю доступную информацию автоматически."
    )

@bot.message_handler(func=lambda msg: True)
def handle_query(message):
    text = message.text.strip()
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, 'typing')

    response = ""

    # ===== ТЕЛЕФОН =====
    if re.search(r'7\d{10}|8\d{10}|\+7\d{10}', text):
        phone_info = get_phone_info(text)
        response = f"📞 ПО НОМЕРУ: {phone_info['phone']}\n"
        response += f"📡 Оператор: {phone_info['operator']}\n"
        response += f"📍 Регион: {phone_info['region']}\n"
        response += f"📱 Telegram: {phone_info['telegram']}\n"
        response += "\n🔹 Попробуй также пробить через ботов:\n"
        response += "@Kropiva_uabot\n"
        response += "@dyxless_infoo_bot\n"
        response += "@GtaSearchOsntBot\n"
        response += "@Himera_Search_Nebot"

    # ===== EMAIL =====
    elif '@' in text and '.' in text and ' ' not in text:
        leaks = check_email_leaks(text)
        response = f"📧 ПО ПОЧТЕ: {text}\n"
        response += f"🔍 Утечки: {leaks}\n"
        response += "\n🔹 Попробуй также:\n"
        response += "https://haveibeenpwned.com\n"
        response += "https://intelx.io"

    # ===== НИКНЕЙМ =====
    elif text.startswith('@') or (len(text) < 30 and ' ' not in text):
        username = text.replace('@', '')
        socials = search_socials(username)
        response = f"👤 ПО НИКНЕЙМУ: {username}\n"
        response += f"📱 Telegram: {check_telegram(username)}\n"
        response += "\n🌐 НАЙДЕННЫЕ АККАУНТЫ:\n"
        response += "\n".join(socials)

    else:
        response = "Не распознал формат. Отправь телефон, email или никнейм."

    bot.send_message(chat_id, response[:4000])  # Telegram лимит

# ===== ЗАПУСК =====
print("🔥 OSINT-Бот запущен!")
bot.infinity_polling()
