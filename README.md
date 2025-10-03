# 🚀 Reddit Sora Monitor

> Automated Reddit monitoring bot that detects OpenAI Sora 2 invite codes and sends them via Telegram in real-time.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Render](https://img.shields.io/badge/Deploy-Render-purple.svg)](https://render.com)

## 📋 Table of Contents

- [Features](#features)
- [Demo](#demo)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Configuration](#configuration)
- [Local Usage](#local-usage)
- [Deploy to Render](#deploy-to-render)
- [Environment Variables](#environment-variables)
- [Contributing](#contributing)
- [Contact](#contact)
- [License](#license)

## ✨ Features

- **Real-time Monitoring**: Scans Reddit posts every 20 seconds for fresh invite codes
- **Smart Code Detection**: Uses regex patterns to identify valid 6-character alphanumeric codes
- **OCR Support**: Extracts codes from images using OCR.Space API
- **Telegram Integration**: Instant notifications with formatted messages
- **Duplicate Prevention**: Advanced filtering to avoid sending the same code twice
- **Web Dashboard**: Built-in HTTP server showing live statistics
- **24/7 Operation**: Designed for continuous deployment on cloud platforms
- **Error Recovery**: Automatic reconnection and error handling

## 🎮 Demo

Want to see the bot in action? Check out our live demo:

📱 **Telegram Channel**: [@Sora2_invite_bot](https://t.me/Sora2_invite_bot)

*Join the channel to see real-time Sora 2 invite codes as they're detected!*

## 🔄 How It Works

1. **Connect** to Reddit API and monitor specific posts
2. **Scan** new comments (posted within last 2 minutes)
3. **Extract** codes from both text and images (OCR)
4. **Validate** codes using smart filtering algorithms
5. **Send** unique codes instantly to your Telegram
6. **Track** statistics via web dashboard

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Reddit Developer Account
- Telegram Bot
- OCR.Space API Key (free)

### Quick Start

1. **Clone the repository**
    git clone https://github.com/Official-Abode/reddit-sora-monitor.git
    cd reddit-sora-monitor

2. **Install dependencies**
    pip install -r requirements.txt

3. **Set up your configuration** (see [Configuration](#configuration))

4. **Run the script**
    python reddit_monitor.py

## ⚙️ Configuration

### 1. Reddit API Setup

1. Visit [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Click **"Create App"** or **"Create Another App"**
3. Fill in the details:
- **Name**: Any name for your app
- **App type**: Select **"script"**
- **Redirect URI**: `http://localhost:8080`
4. Note your **Client ID** (under app name) and **Secret**

### 2. Telegram Bot Setup

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the instructions
3. Save your **Bot Token**
4. Get your **Chat ID**:
- Send a message to your bot
- Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
- Find your `chat.id` in the response

### 3. OCR.Space API Setup

1. Sign up at [OCR.Space](https://ocr.space/ocrapi)
2. Get your free **API Key** (25,000 requests/month)

## 🖥️ Local Usage

Create a `.env` file in the project root:
    REDDIT_CLIENT_ID=your_reddit_client_id
    REDDIT_SECRET=your_reddit_secret
    TELEGRAM_TOKEN=your_telegram_bot_token
    TELEGRAM_CHAT_ID=your_telegram_chat_id
    OCR_API_KEY=your_ocr_space_api_key

Run the script:
    python reddit_monitor.py

Visit `http://localhost:10000` to see the dashboard.

## ☁️ Deploy to Render

### Step 1: Prepare Your Repository

Ensure your repository contains:
- `reddit_monitor.py` (main script)
- `requirements.txt` (dependencies)

### Step 2: Deploy to Render

1. **Sign up** at [Render.com](https://render.com)
2. **Connect your GitHub** repository
3. **Create a new Web Service**
4. Configure the service:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python reddit_monitor.py`
   - **Environment**: `Python 3`
   - **Plan**: Free

### Step 3: Set Environment Variables

In Render dashboard, add these environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `REDDIT_CLIENT_ID` | Reddit app client ID | ✅ |
| `REDDIT_SECRET` | Reddit app secret | ✅ |
| `TELEGRAM_TOKEN` | Telegram bot token | ✅ |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID | ✅ |
| `OCR_API_KEY` | OCR.Space API key | ✅ |

### Step 4: Deploy

Click **"Create Web Service"** and wait for deployment (5-10 minutes).

Your bot will be live at: `https://your-service-name.onrender.com`

## 🔧 Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REDDIT_CLIENT_ID` | Reddit API client ID | - | ✅ |
| `REDDIT_SECRET` | Reddit API secret | - | ✅ |
| `TELEGRAM_TOKEN` | Telegram bot token | - | ✅ |
| `TELEGRAM_CHAT_ID` | Telegram chat ID | - | ✅ |
| `OCR_API_KEY` | OCR.Space API key | - | ✅ |
| `PORT` | HTTP server port | 10000 | ❌ |

## 📊 Dashboard

The script includes a built-in web dashboard showing:
- ✅ Service status
- ⏱️ Uptime
- 🔑 Codes sent
- ❌ Codes rejected
- 🖼️ Images scanned
- 🔄 Total checks performed

Access it at your deployment URL or `http://localhost:10000` when running locally.

## 🔍 How Codes Are Detected

### Text Detection
- Scans comment text for 6-character alphanumeric patterns
- Requires mix of letters and numbers
- Filters out common English words

### Image Detection (OCR)
- Downloads images from comments
- Uses OCR.Space API for text extraction
- Applies same validation rules

### Smart Filtering
- Prevents duplicate sends
- Blacklists common false positives
- Only processes comments from last 2 minutes

## 📝 Sample Output

### Telegram Message Format

    🎯 OpenAI Sora 2 Invite Code
    🔑 Code: A7B9X2
    ⏰ Posted: 0.3m ago
    📱 Source: 💬 Text
    🕐 Found: 15:30:45
    🔗 View Comment

### Console Logs

    🚀 Reddit Monitor Started
    🖼️ OCR: Enabled
    ✅ Connected: Open AI Sora 2 Invite Codes Megathread
    📝 Comments: 128
    ✅ CODE: A7B9X2
    🎉 NEW: ['A7B9X2(T)']

## 🛠️ Troubleshooting

### Common Issues

**"Invalid credentials"**
- Check your Reddit API credentials
- Ensure Environment Variables are set correctly

**"No open ports detected"**
- Normal for first deployment on Render
- The HTTP server will start automatically

**"OCR API Error"**
- Verify your OCR.Space API key
- Check if you've exceeded free tier limits

**Duplicate codes**
- Script prevents duplicates automatically
- Check logs for "Already sent" messages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Contact

**Developer**: [Bedo151907](https://www.facebook.com/Bedo151907)

For questions, suggestions, or support, feel free to reach out via Facebook!

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational purposes only. Make sure to:
- Respect Reddit's Terms of Service
- Use responsibly and avoid spam
- Follow rate limits and API guidelines
- Respect others' privacy

## 🙏 Acknowledgments

- [PRAW](https://praw.readthedocs.io/) - Python Reddit API Wrapper
- [OCR.Space](https://ocr.space/) - Free OCR API
- [Render](https://render.com/) - Free hosting platform
- [Telegram Bot API](https://core.telegram.org/bots/api) - Bot integration

---

**Made with ❤️ for the OpenAI community**

*If you found this project helpful, please give it a ⭐ on GitHub!*

### 🔗 Quick Links

- 📱 **Live Demo**: [@Sora2_invite_bot](https://t.me/Sora2_invite_bot)
- 👨‍💻 **Developer**: [Facebook](https://www.facebook.com/Bedo151907)
- 📚 **Documentation**: [GitHub Repository](https://github.com/Official-Abode/reddit-sora-monitor)
