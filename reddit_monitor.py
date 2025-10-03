import praw
import re
import time
import requests
from datetime import datetime
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# الإحصائيات
stats = {
    'total_checks': 0,
    'codes_sent': 0,
    'codes_rejected': 0,
    'images_scanned': 0,
    'start_time': datetime.now(),
    'last_code_time': None,
    'codes_list': []
}

# HTTP Server لـ Render Health Check
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        uptime = datetime.now() - stats['start_time']
        hours = int(uptime.total_seconds() / 3600)
        minutes = int((uptime.total_seconds() % 3600) / 60)
        
        html = f"""
        <html>
        <head><title>Reddit Sora Monitor</title></head>
        <body style="font-family: Arial; padding: 20px; background: #1a1a1a; color: #fff;">
            <h1>Reddit Monitor Status</h1>
            <div style="background: #2a2a2a; padding: 20px; border-radius: 10px;">
                <p><strong>Status:</strong> Running</p>
                <p><strong>Uptime:</strong> {hours}h {minutes}m</p>
                <p><strong>Codes Sent:</strong> {stats['codes_sent']}</p>
                <p><strong>Codes Rejected:</strong> {stats['codes_rejected']}</p>
                <p><strong>Images Scanned:</strong> {stats['images_scanned']}</p>
                <p><strong>Total Checks:</strong> {stats['total_checks']}</p>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode())
    
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

# OCR.Space API Key
OCR_API_KEY = os.getenv('OCR_API_KEY')
OCR_ENABLED = True

# Regex للبحث عن الأكواد
CODE_PATTERN = re.compile(r'\b[A-Za-z0-9]{6}\b')

# لتتبع الأكواد المرسلة والتعليقات المفحوصة
sent_codes = set()
processed_comments = set()

def extract_text_from_image(image_url):
    """استخراج النص من الصورة"""
    try:
        print(f"     OCR scanning...")
        
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

def send_telegram_message(code, comment_url="", username="", seconds_ago=0, source_type="text"):
    """إرسال رسالة إلى Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    if code == "REPORT":
        uptime = datetime.now() - stats['start_time']
        total_seconds = int(uptime.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        # حساب معدل النجاح
        total_codes = stats['codes_sent'] + stats['codes_rejected']
        success_rate = (stats['codes_sent'] / total_codes * 100) if total_codes > 0 else 0
        
        # حساب آخر كود
        last_code_info = "No codes sent yet"
        if stats['last_code_time']:
            time_since = datetime.now() - stats['last_code_time']
            last_code_info = f"{int(time_since.total_seconds())}s ago"
        
        message = f"<b>REDDIT MONITOR - HOURLY REPORT</b>\n"
        message += f"{'='*35}\n\n"
        message += f"<b>SYSTEM STATUS</b>\n"
        message += f"Status: Running\n"
        message += f"Uptime: {hours}h {minutes}m {seconds}s\n"
        message += f"Platform: Render.com\n"
        message += f"OCR: Enabled\n\n"
        message += f"<b>STATISTICS</b>\n"
        message += f"Codes Sent: {stats['codes_sent']}\n"
        message += f"Codes Rejected: {stats['codes_rejected']}\n"
        message += f"Success Rate: {success_rate:.1f}%\n"
        message += f"Images Scanned: {stats['images_scanned']}\n"
        message += f"Total Checks: {stats['total_checks']}\n\n"
        message += f"<b>PERFORMANCE</b>\n"
        message += f"Check Interval: 10s\n"
        message += f"Last Code: {last_code_info}\n"
        message += f"Avg Codes/Hour: {stats['codes_sent'] / max(hours, 1):.1f}\n\n"
        message += f"<b>RECENT CODES</b>\n"
        recent_codes = stats['codes_list'][-5:] if stats['codes_list'] else ["None"]
        message += f"{', '.join(recent_codes)}\n\n"
        message += f"{'='*35}\n"
        message += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
    elif code == "START":
        ocr_status = "Enabled" if OCR_ENABLED else "Disabled"
        message = f"<b>REDDIT MONITOR STARTED</b>\n"
        message += f"{'='*30}\n\n"
        message += f"Target: OpenAI Sora 2\n"
        message += f"Max Age: 2 minutes\n"
        message += f"Check Interval: 10 seconds\n"
        message += f"OCR: {ocr_status}\n"
        message += f"Platform: Render.com\n\n"
        message += f"{'='*30}\n"
        message += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
    else:
        source_label = "IMAGE" if source_type == "image" else "TEXT"
        
        message = f"<b>SORA 2 INVITE CODE DETECTED</b>\n"
        message += f"{'='*30}\n\n"
        message += f"Code: <code>{code}</code>\n"
        message += f"Posted: {int(seconds_ago)}s ago\n"
        message += f"Source: {source_label}\n"
        message += f"Found: {datetime.now().strftime('%H:%M:%S')}\n"
        message += f"\n{'='*30}"
        
        if comment_url:
            message += f"\n\n<a href='{comment_url}'>View on Reddit</a>"
    
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
    """استخراج روابط الصور"""
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
        print(f"Connected: {submission.title}")
    except Exception as e:
        print(f"Error: {e}")
        return
    
    loop_count = 0
    last_report_time = time.time()
    
    while True:
        try:
            loop_count += 1
            current_time = time.time()
            stats['total_checks'] += 1
            
            if current_time - last_report_time >= 3600:
                send_telegram_message("REPORT", "", "", 0)
                last_report_time = current_time
            
            print(f"\n{'='*60}")
            print(f"Cycle #{loop_count} - {datetime.now().strftime('%H:%M:%S')}")
            
            submission = reddit.submission(url=post_url)
            submission.comment_sort = 'new'
            submission.comments.replace_more(limit=0)
            
            all_comments = list(submission.comments)
            print(f"Comments: {len(all_comments)}")
            
            if len(all_comments) == 0:
                time.sleep(5)
                continue
            
            new_codes = []
            checked = 0
            
            for comment in all_comments[:20]:
                if comment.id in processed_comments:
                    continue
                
                time_diff = current_time - comment.created_utc
                seconds_ago = int(time_diff)
                
                if seconds_ago > 120:  # 2 minutes
                    continue
                
                checked += 1
                processed_comments.add(comment.id)
                
                # فحص النص
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
                    
                    if send_telegram_message(code_upper, comment_url, str(comment.author), seconds_ago, "text"):
                        new_codes.append(f"{code_upper}(T)")
                        stats['codes_sent'] += 1
                        stats['last_code_time'] = datetime.now()
                        stats['codes_list'].append(code_upper)
                        print(f"     CODE: {code_upper} ({seconds_ago}s)")
                    else:
                        sent_codes.remove(code_upper)
                        print(f"     Failed to send: {code_upper}")
                
                # فحص الصور
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
                                
                                if send_telegram_message(code_upper, comment_url, str(comment.author), seconds_ago, "image"):
                                    new_codes.append(f"{code_upper}(I)")
                                    stats['codes_sent'] += 1
                                    stats['last_code_time'] = datetime.now()
                                    stats['codes_list'].append(code_upper)
                                    print(f"     IMAGE CODE: {code_upper} ({seconds_ago}s)")
                                else:
                                    sent_codes.remove(code_upper)
                                    print(f"     Failed to send image code: {code_upper}")
                        except:
                            pass
            
            if new_codes:
                print(f"NEW: {new_codes}")
            
            if len(processed_comments) > 500:
                processed_comments.clear()
            
            # انتظار 10 ثواني فقط للفحص الأسرع
            time.sleep(10)
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    # بدء HTTP Server في الخلفية
    http_thread = Thread(target=start_http_server, daemon=True)
    http_thread.start()
    
    POST_URL = "https://www.reddit.com/r/OpenAI/comments/1nukmm2/open_ai_sora_2_invite_codes_megathread/"
    
    print("Initializing...")
    time.sleep(2)
    send_telegram_message("START", "", "", 0)
    
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
