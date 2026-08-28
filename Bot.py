import telebot
import requests
import re
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# ===== КОНФИГУРАЦИЯ =====
TOKEN = "8605143642:AAHE0UQ3Y2A9KX9LW12MxNrX0KUpGjtRJ9U"  # замени на реальный
bot = telebot.TeleBot(TOKEN)

# ===== HTTP-СЕРВЕР ДЛЯ RENDER (чтобы был открытый порт) =====
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()

# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

def get_operator_region(phone):
    """Определяет оператора и регион по номеру"""
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
            '900': 'Мегафон', '902': 'Мегафон', '904': 'Мегафон', '908': 'Мегафон',
            '920': 'Мегафон', '921': 'Мегафон', '922': 'Мегафон', '923': 'Мегафон',
            '924': 'Мегафон', '925': 'Мегафон', '926': 'Мегафон', '927': 'Мегафон',
            '928': 'Мегафон', '929': 'Мегафон', '930': 'Мегафон', '931': 'Мегафон',
            '932': 'Мегафон', '933': 'Мегафон', '934': 'Мегафон', '935': 'Мегафон',
            '936': 'Мегафон', '937': 'Мегафон', '938': 'Мегафон', '939': 'Мегафон',
            '940': 'Мегафон', '941': 'Мегафон', '942': 'Мегафон', '943': 'Мегафон',
            '944': 'Мегафон', '945': 'Мегафон', '946': 'Мегафон', '947': 'Мегафон',
            '948': 'Мегафон', '949': 'Мегафон', '950': 'Мегафон'
        }
        operator = operators.get(code, 'Неизвестный')
        msk_codes = ['495', '499', '903', '905', '906', '909', '910', '915', '916', '917', '918', '919',
                     '920', '921', '922', '923', '924', '925', '926', '927', '928', '929', '930', '931',
                     '932', '933', '934', '935', '936', '937', '938', '939', '940', '941', '942', '943',
                     '944', '945', '946', '947', '948', '949', '950']
        region = "Москва и область" if code in msk_codes else "Другой регион"
        return operator, region
    return "Неизвестный", "Неизвестный"

def check_telegram(username):
    """Проверяет, существует ли пользователь в Telegram"""
    try:
        url = f"https://t.me/{username.replace('@', '')}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and "tgme_page_extra" in r.text:
            return "Найден"
        return "Не найден"
    except:
        return "Ошибка проверки"

# ===== КОМАНДЫ БОТА =====

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("Поиск по никнейму")
    btn2 = telebot.types.KeyboardButton("Поиск по email")
    btn3 = telebot.types.KeyboardButton("Поиск по телефону")
    btn4 = telebot.types.KeyboardButton("Проверка ссылки")
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(
        message.chat.id,
        "ROCKET OSINT BOT\n\n"
        "Отправь данные в свободной форме:\n"
        "- Никнейм: username или @username\n"
        "- Email: mail@example.com\n"
        "- Телефон: 79151812030 или +79151812030\n"
        "- Ссылка: https://...",
        reply_markup=markup
    )

@bot.message_handler(func=lambda msg: True)
def handle_query(message):
    text = message.text.strip()
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, 'typing')

    # Поиск по никнейму
    if text.startswith('@') or (len(text) < 30 and ' ' not in text and '@' not in text and '.' not in text):
        username = text.replace('@', '')
        response = f"Поиск по никнейму: {username}\n\n"
        response += f"Telegram: {check_telegram(username)}\n\n"
        response += "Ссылки для ручного пробива:\n"
        response += f"https://vk.com/foaf.php?q={username}\n"
        response += f"https://intelx.io/?s={username}\n"
        response += f"https://x-ray.contact/search?query={username}"
        bot.send_message(chat_id, response)

    # Поиск по email
    elif '@' in text and '.' in text and ' ' not in text:
        email = text
        response = f"Поиск по email: {email}\n\n"
        response += "Проверь утечки:\n"
        response += f"https://intelx.io/?s={email}\n"
        response += "https://haveibeenpwned.com"
        bot.send_message(chat_id, response)

    # Поиск по телефону
    elif re.search(r'7\d{10}|8\d{10}|\+7\d{10}', text) or re.search(r'^\+?\d{10,15}$', text):
        clean = re.sub(r'[^0-9]', '', text)
        if len(clean) == 11 and clean.startswith('7'):
            operator, region = get_operator_region(clean)
            response = f"Поиск по телефону: +{clean}\n\n"
            response += f"Оператор: {operator}\n"
            response += f"Регион: {region}\n"
            response += f"Telegram: {check_telegram(clean)}\n\n"
            response += "Глубокий пробив (боты):\n"
            response += "@Kropiva_uabot\n"
            response += "@dyxless_infoo_bot\n"
            response += "@GtaSearchOsntBot\n"
            response += "@Himera_Search_Nebot\n"
            response += "@goodsearch_robot\n"
            response += "@getairplane_bot\n"
            response += "@sensor_dsbot\n"
            response += "@CheckID_AIDbot"
            bot.send_message(chat_id, response)

    # Проверка ссылки
    elif text.startswith('http://') or text.startswith('https://'):
        response = f"Проверка ссылки: {text}\n\n"
        response += "Проверь через VirusTotal:\n"
        response += "https://www.virustotal.com/gui/home/url"
        bot.send_message(chat_id, response)

    # Неизвестный формат
    else:
        bot.send_message(
            chat_id,
            "Не распознал формат. Попробуй:\n"
            "- Никнейм: @username\n"
            "- Email: mail@example.com\n"
            "- Телефон: 79151812030\n"
            "- Ссылка: https://example.com"
        )

# ===== ЗАПУСК БОТА =====
print("Бот ROCKET OSINT запущен и готов к работе!")
bot.infinity_polling()
