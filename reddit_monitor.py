import praw
import discord
import re
import time
import requests
from datetime import datetime
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import asyncio

# الإحصائيات
stats = {
    'total_checks': 0,
    'codes_sent': 0,
    'codes_rejected': 0,
    'images_scanned': 0,
    'start_time': datetime.now(),
    'last_code_time': None,
    'codes_list': [],
    'reddit_codes': 0,
    'discord_codes': 0
}

# HTTP Server لـ Render Health Check
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        uptime = datetime.now() - stats['start_time']
        total_seconds = int(uptime.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        total_codes = stats['codes_sent'] + stats['codes_rejected']
        success_rate = (stats['codes_sent'] / total_codes * 100) if total_codes > 0 else 0
        
        last_code_info = "No codes sent yet"
        if stats['last_code_time']:
            time_since = datetime.now() - stats['last_code_time']
            last_code_info = f"{int(time_since.total_seconds())}s ago"
        
        recent_codes = ", ".join(stats['codes_list'][-5:]) if stats['codes_list'] else "None"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="refresh" content="30">
            <title>Reddit + Discord Monitor - Dashboard</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    padding: 30px;
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    color: #eee;
                    margin: 0;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                h1 {{
                    text-align: center;
                    color: #00d4ff;
                    font-size: 2.5em;
                    margin-bottom: 10px;
                    text-shadow: 0 0 10px rgba(0,212,255,0.5);
                }}
                .subtitle {{
                    text-align: center;
                    color: #aaa;
                    margin-bottom: 40px;
                    font-size: 1.1em;
                }}
                .status-badge {{
                    display: inline-block;
                    background: #00ff88;
                    color: #000;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 0.9em;
                    margin: 0 5px;
                }}
                .grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .card {{
                    background: rgba(42, 42, 58, 0.8);
                    padding: 25px;
                    border-radius: 15px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }}
                .card h2 {{
                    margin-top: 0;
                    color: #00d4ff;
                    font-size: 1.3em;
                    border-bottom: 2px solid #00d4ff;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }}
                .stat-row {{
                    display: flex;
                    justify-content: space-between;
                    padding: 12px 0;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }}
                .stat-row:last-child {{
                    border-bottom: none;
                }}
                .stat-label {{
                    color: #aaa;
                    font-weight: 500;
                }}
                .stat-value {{
                    color: #fff;
                    font-weight: bold;
                    font-size: 1.1em;
                }}
                .highlight {{
                    color: #00ff88;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                    color: #888;
                    font-size: 0.9em;
                }}
                .codes-list {{
                    background: rgba(0, 0, 0, 0.3);
                    padding: 15px;
                    border-radius: 8px;
                    font-family: 'Courier New', monospace;
                    color: #00ff88;
                    font-size: 1.1em;
                    word-break: break-all;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Multi-Source Sora Monitor</h1>
                <div class="subtitle">
                    <span class="status-badge">REDDIT ACTIVE</span>
                    <span class="status-badge">DISCORD ACTIVE</span>
                    <br>Real-time OpenAI Sora 2 Invite Code Detection
                </div>
                
                <div class="grid">
                    <div class="card">
                        <h2>System Status</h2>
                        <div class="stat-row">
                            <span class="stat-label">Status</span>
                            <span class="stat-value highlight">Online</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">Uptime</span>
                            <span class="stat-value">{hours}h {minutes}m {seconds}s</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">OCR Engine</span>
                            <span class="stat-value">Enabled</span>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h2>Statistics</h2>
                        <div class="stat-row">
                            <span class="stat-label">Total Codes</span>
                            <span class="stat-value highlight">{stats['codes_sent']}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">Reddit Codes</span>
                            <span class="stat-value">{stats['reddit_codes']}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">Discord Codes</span>
                            <span class="stat-value">{stats['discord_codes']}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">Success Rate</span>
                            <span class="stat-value">{success_rate:.1f}%</span>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h2>Performance</h2>
                        <div class="stat-row">
                            <span class="stat-label">Total Checks</span>
                            <span class="stat-value">{stats['total_checks']}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">Check Interval</span>
                            <span class="stat-value">10 seconds</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">Last Code</span>
                            <span class="stat-value">{last_code_info}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">Images Scanned</span>
                            <span class="stat-value">{stats['images_scanned']}</span>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h2>Recent Codes (Last 5)</h2>
                    <div class="codes-list">
                        {recent_codes}
                    </div>
                </div>
                
                <div class="footer">
                    Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Auto-refresh: 30s
                    <br>Monitoring: r/OpenAI + Discord Channel
                </div>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))
    
    def log_message(self, format, *args):
        pass

def start_http_server():
    """بدء HTTP Server"""
    port = int(os.getenv('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"HTTP Server started on port {port}")
    server.serve_forever()

# إعدادات Reddit API
reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_SECRET'),
    user_agent='OpenAI_Sora2/1.0'
)

# إعدادات Telegram Bot
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# إعدادات Discord Self-Bot
DISCORD_USER_TOKEN = os.getenv('DISCORD_USER_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID', '1424089559330721852'))

# OCR.Space API Key
OCR_API_KEY = os.getenv('OCR_API_KEY')
OCR_ENABLED = True

# Regex للبحث عن الأكواد
CODE_PATTERN = re.compile(r'\b[A-Za-z0-9]{6}\b')

# لتتبع الأكواد المرسلة
sent_codes = set()
processed_comments = set()
processed_discord_messages = set()

def extract_text_from_image(image_url):
    """استخراج النص من الصورة"""
    try:
        payload = {
            'url': image_url,
            'apikey': OCR_API_KEY,
            'language': 'eng',
            'isOverlayRequired': False,
            'detectOrientation': True,
            'scale': True,
            'OCREngine': 2
        }
        
        response = requests.post(
            'https://api.ocr.space/parse/image',
            data=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            return ""
        
        result = response.json()
        
        if result.get('IsErroredOnProcessing', True):
            return ""
        
        parsed_results = result.get('ParsedResults', [])
        if not parsed_results:
            return ""
        
        extracted_text = parsed_results[0].get('ParsedText', '')
        stats['images_scanned'] += 1
        
        return extracted_text.upper()
        
    except Exception as e:
        return ""

def send_telegram_message(code, source_url="", seconds_ago=0, source="reddit"):
    """إرسال رسالة إلى Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    if code in ["REPORT", "START"]:
        return True
    
    source_emoji = "🔴" if source == "reddit" else "💜"
    source_name = "Reddit" if source == "reddit" else "Discord"
    
    message = f"🎯 <b>SORA 2 INVITE CODE DETECTED</b>\n"
    message += f"{'='*30}\n"
    message += f"🔑 Code: <code>{code}</code>\n"
    message += f"⏰ Posted: {int(seconds_ago)}s ago\n"
    message += f"{source_emoji} Source: {source_name}\n"
    message += f"{'='*30}"
    
    if source_url:
        message += f"\n\n🔗 <a href='{source_url}'>View Source</a>"
    
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        return False

def is_valid_code(code):
    """فحص ذكي للأكواد"""
    code_upper = code.upper()
    
    if len(code_upper) != 6:
        return False, "wrong_length"
    
    has_letter = any(c.isalpha() for c in code_upper)
    has_digit = any(c.isdigit() for c in code_upper)
    
    if not (has_letter and has_digit):
        return False, "not_mixed"
    
    blacklist = {
        'ANYONE', 'PLEASE', 'THANKS', 'UPDATE', 'POSTED', 'DELETE',
        'THREAD', 'INVITE', 'WITHIN', 'SECOND', 'TRIPLE', 'PROMPT',
        'OPENAI', 'REDDIT', 'REPORT', 'START', 'GIVING', 'TAKING',
        'FRIEND', 'PEOPLE', 'PERSON', 'SINGLE', 'DOUBLE', 'FOLLOW',
        'RECENT', 'RANDOM', 'PUBLIC', 'BUTTON', 'SUBMIT', 'CANCEL',
        'TEST01', 'TEST02', 'DEMO01', 'SAMPLE', 'XXXXXX', 'ABCDEF',
        '123456', 'ABC123', 'XYZ789', 'START1', 'ERROR1'
    }
    
    if code_upper in blacklist:
        return False, "blacklist"
    
    if code_upper.isalpha() or code_upper.isdigit():
        return False, "homogeneous"
    
    return True, "valid"

def get_image_urls_from_comment(comment):
    """استخراج روابط الصور من Reddit"""
    image_urls = []
    
    try:
        url_pattern = re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+')
        urls = url_pattern.findall(comment.body)
        
        for url in urls:
            if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                image_urls.append(url)
            elif 'i.redd.it' in url or 'preview.redd.it' in url:
                image_urls.append(url)
            elif 'imgur.com' in url and '/a/' not in url:
                if not url.endswith(('.jpg', '.png', '.gif')):
                    url = url + '.jpg'
                image_urls.append(url)
    except:
        pass
    
    return image_urls

def monitor_reddit_post(post_url):
    """مراقبة منشور Reddit"""
    print("Reddit Monitor Started")
    print(f"OCR: {'Enabled' if OCR_ENABLED else 'Disabled'}")
    print(f"Check Interval: 10 seconds")
    
    try:
        submission = reddit.submission(url=post_url)
        print(f"Connected to Reddit: {submission.title}")
    except Exception as e:
        print(f"Reddit Error: {e}")
        return
    
    loop_count = 0
    
    while True:
        try:
            loop_count += 1
            current_time = time.time()
            stats['total_checks'] += 1
            
            if loop_count % 30 == 0:
                print(f"Reddit Cycle #{loop_count} - {datetime.now().strftime('%H:%M:%S')}")
            
            submission = reddit.submission(url=post_url)
            submission.comment_sort = 'new'
            submission.comments.replace_more(limit=0)
            
            all_comments = list(submission.comments)
            
            for comment in all_comments[:20]:
                if comment.id in processed_comments:
                    continue
                
                time_diff = current_time - comment.created_utc
                seconds_ago = int(time_diff)
                
                if seconds_ago > 120:
                    continue
                
                processed_comments.add(comment.id)
                
                text_codes = CODE_PATTERN.findall(comment.body)
                
                for code in text_codes:
                    code_upper = code.upper()
                    
                    if code_upper in sent_codes:
                        continue
                    
                    sent_codes.add(code_upper)
                    
                    is_valid, reason = is_valid_code(code)
                    
                    if not is_valid:
                        stats['codes_rejected'] += 1
                        sent_codes.remove(code_upper)
                        continue
                    
                    comment_url = f"https://reddit.com{comment.permalink}"
                    
                    if send_telegram_message(code_upper, comment_url, seconds_ago, "reddit"):
                        stats['codes_sent'] += 1
                        stats['reddit_codes'] += 1
                        stats['last_code_time'] = datetime.now()
                        stats['codes_list'].append(code_upper)
                        print(f"     [REDDIT] CODE: {code_upper}")
                    else:
                        sent_codes.remove(code_upper)
                
                if OCR_ENABLED:
                    image_urls = get_image_urls_from_comment(comment)
                    
                    for img_url in image_urls[:2]:
                        try:
                            ocr_text = extract_text_from_image(img_url)
                            
                            if not ocr_text:
                                continue
                            
                            image_codes = CODE_PATTERN.findall(ocr_text)
                            
                            for code in image_codes:
                                code_upper = code.upper()
                                
                                if code_upper in sent_codes:
                                    continue
                                
                                sent_codes.add(code_upper)
                                
                                is_valid, reason = is_valid_code(code)
                                
                                if not is_valid:
                                    stats['codes_rejected'] += 1
                                    sent_codes.remove(code_upper)
                                    continue
                                
                                comment_url = f"https://reddit.com{comment.permalink}"
                                
                                if send_telegram_message(code_upper, comment_url, seconds_ago, "reddit"):
                                    stats['codes_sent'] += 1
                                    stats['reddit_codes'] += 1
                                    stats['last_code_time'] = datetime.now()
                                    stats['codes_list'].append(code_upper)
                                    print(f"     [REDDIT-IMG] CODE: {code_upper}")
                                else:
                                    sent_codes.remove(code_upper)
                        except:
                            pass
            
            if len(processed_comments) > 500:
                processed_comments.clear()
            
            time.sleep(10)
            
        except Exception as e:
            print(f"Reddit Error: {e}")
            time.sleep(30)

# Discord Self-Bot
class DiscordSelfBot(discord.Client):
    def __init__(self):
        super().__init__()
    
    async def on_ready(self):
        print(f'Discord Self-Bot Connected: {self.user}')
        print(f'Monitoring Channel ID: {DISCORD_CHANNEL_ID}')
    
    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if message.channel.id != DISCORD_CHANNEL_ID:
            return
        
        if message.id in processed_discord_messages:
            return
        
        processed_discord_messages.add(message.id)
        
        current_time = datetime.now(message.created_at.tzinfo)
        time_diff = (current_time - message.created_at).total_seconds()
        
        print(f"[DISCORD] New message from {message.author}")
        
        text_codes = CODE_PATTERN.findall(message.content)
        
        for code in text_codes:
            code_upper = code.upper()
            
            if code_upper in sent_codes:
                continue
            
            sent_codes.add(code_upper)
            
            is_valid, reason = is_valid_code(code)
            
            if not is_valid:
                stats['codes_rejected'] += 1
                sent_codes.remove(code_upper)
                continue
            
            if hasattr(message, 'guild') and message.guild:
                message_url = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
            else:
                message_url = f"https://discord.com/channels/@me/{message.channel.id}/{message.id}"
            
            if send_telegram_message(code_upper, message_url, int(time_diff), "discord"):
                stats['codes_sent'] += 1
                stats['discord_codes'] += 1
                stats['last_code_time'] = datetime.now()
                stats['codes_list'].append(code_upper)
                print(f"     [DISCORD] CODE: {code_upper}")
            else:
                sent_codes.remove(code_upper)
        
        if OCR_ENABLED and message.attachments:
            for attachment in message.attachments:
                if any(attachment.filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                    try:
                        print(f"     [DISCORD] Scanning image: {attachment.filename}")
                        ocr_text = extract_text_from_image(attachment.url)
                        
                        if not ocr_text:
                            continue
                        
                        image_codes = CODE_PATTERN.findall(ocr_text)
                        
                        for code in image_codes:
                            code_upper = code.upper()
                            
                            if code_upper in sent_codes:
                                continue
                            
                            sent_codes.add(code_upper)
                            
                            is_valid, reason = is_valid_code(code)
                            
                            if not is_valid:
                                stats['codes_rejected'] += 1
                                sent_codes.remove(code_upper)
                                continue
                            
                            if hasattr(message, 'guild') and message.guild:
                                message_url = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
                            else:
                                message_url = f"https://discord.com/channels/@me/{message.channel.id}/{message.id}"
                            
                            if send_telegram_message(code_upper, message_url, int(time_diff), "discord"):
                                stats['codes_sent'] += 1
                                stats['discord_codes'] += 1
                                stats['last_code_time'] = datetime.now()
                                stats['codes_list'].append(code_upper)
                                print(f"     [DISCORD-IMG] CODE: {code_upper}")
                            else:
                                sent_codes.remove(code_upper)
                    except Exception as e:
                        print(f"     [DISCORD] OCR Error: {e}")
        
        if len(processed_discord_messages) > 500:
            processed_discord_messages.clear()

async def start_discord_selfbot():
    """بدء Discord Self-Bot"""
    client = DiscordSelfBot()
    try:
        await client.start(DISCORD_USER_TOKEN, bot=False)
    except Exception as e:
        print(f"Discord Self-Bot Error: {e}")

def run_discord_selfbot():
    """تشغيل Discord Self-Bot في thread منفصل"""
    asyncio.run(start_discord_selfbot())

if __name__ == "__main__":
    # HTTP Server
    http_thread = Thread(target=start_http_server, daemon=True)
    http_thread.start()
    
    # Discord Self-Bot (إذا كان Token موجود)
    if DISCORD_USER_TOKEN and DISCORD_USER_TOKEN != 'your_discord_user_token':
        discord_thread = Thread(target=run_discord_selfbot, daemon=True)
        discord_thread.start()
        print("Discord Self-Bot starting...")
    else:
        print("Discord monitoring disabled (no token provided)")
    
    # Reddit Monitor (main thread)
    POST_URL = "https://www.reddit.com/r/OpenAI/comments/1nz31om/new_sora_2_invite_code_megathread/"
    
    print("Initializing Multi-Source Monitor...")
    print(f"OCR: {'Enabled' if OCR_ENABLED else 'Disabled'}")
    time.sleep(3)
    
    retry_count = 0
    while retry_count < 10:
        try:
            monitor_reddit_post(POST_URL)
        except KeyboardInterrupt:
            break
        except Exception as e:
            retry_count += 1
            print(f"Fatal: {e}")
            time.sleep(60)
