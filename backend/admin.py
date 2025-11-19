from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import json
import shutil
from datetime import datetime
from typing import Optional
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Admin Panel - Muji")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

current_dir = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(current_dir, "data.json")
UPLOAD_DIR = os.path.join(current_dir, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "profiles": [],
            "vip_profiles": [],
            "chats": [],
            "messages": [],
            "comments": [],
            "promocodes": [],
            "settings": {
                "crypto_wallets": {
                    "trc20": "TY76gU8J9o8j7U6tY5r4E3W2Q1",
                    "erc20": "0x8a9C6e5D8b0E2a1F3c4B6E7D8C9A0B1C2D3E4F5",
                    "bnb": "bnb1q3e5r7t9y1u3i5o7p9l1k3j5h7g9f2d4s6q8w0"
                },
                "banner": {
                    "text": "Special Offer: 15% discount with promo code WELCOME15",
                    "visible": True,
                    "link": "https://t.me/yourchannel",
                    "link_text": "Join Channel"
                },
                "vip_catalogs": {
                    "vip": {
                        "name": "VIP Catalog",
                        "price": 100,
                        "redirect_url": "https://t.me/vip_channel",
                        "visible": True
                    },
                    "extra_vip": {
                        "name": "Extra VIP",
                        "price": 200,
                        "redirect_url": "https://t.me/extra_vip_channel",
                        "visible": True
                    },
                    "secret": {
                        "name": "Secret Catalog",
                        "price": 300,
                        "redirect_url": "https://t.me/secret_channel",
                        "visible": True
                    }
                }
            }
        }
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
            if "settings" not in data:
                data["settings"] = {
                    "crypto_wallets": {
                        "trc20": "TY76gU8J9o8j7U6tY5r4E3W2Q1",
                        "erc20": "0x8a9C6e5D8b0E2a1F3c4B6E7D8C9A0B1C2D3E4F5",
                        "bnb": "bnb1q3e5r7t9y1u3i5o7p9l1k3j5h7g9f2d4s6q8w0"
                    },
                    "banner": {
                        "text": "Special Offer: 15% discount with promo code WELCOME15",
                        "visible": True,
                        "link": "https://t.me/yourchannel",
                        "link_text": "Join Channel"
                    },
                    "vip_catalogs": {
                        "vip": {
                            "name": "VIP Catalog",
                            "price": 100,
                            "redirect_url": "https://t.me/vip_channel",
                            "visible": True
                        },
                        "extra_vip": {
                            "name": "Extra VIP",
                            "price": 200,
                            "redirect_url": "https://t.me/extra_vip_channel",
                            "visible": True
                        },
                        "secret": {
                            "name": "Secret Catalog",
                            "price": 300,
                            "redirect_url": "https://t.me/secret_channel",
                            "visible": True
                        }
                    }
                }
            if "promocodes" not in data:
                data["promocodes"] = []
            if "comments" not in data:
                data["comments"] = []
            if "vip_profiles" not in data:
                data["vip_profiles"] = []
            return data
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return {
            "profiles": [],
            "vip_profiles": [],
            "chats": [],
            "messages": [],
            "comments": [],
            "promocodes": [],
            "settings": {
                "crypto_wallets": {
                    "trc20": "TY76gU8J9o8j7U6tY5r4E3W2Q1",
                    "erc20": "0x8a9C6e5D8b0E2a1F3c4B6E7D8C9A0B1C2D3E4F5",
                    "bnb": "bnb1q3e5r7t9y1u3i5o7p9l1k3j5h7g9f2d4s6q8w0"
                },
                "banner": {
                    "text": "Special Offer: 15% discount with promo code WELCOME15",
                    "visible": True,
                    "link": "https://t.me/yourchannel",
                    "link_text": "Join Channel"
                },
                "vip_catalogs": {
                    "vip": {
                        "name": "VIP Catalog",
                        "price": 100,
                        "redirect_url": "https://t.me/vip_channel",
                        "visible": True
                    },
                    "extra_vip": {
                        "name": "Extra VIP",
                        "price": 200,
                        "redirect_url": "https://t.me/extra_vip_channel",
                        "visible": True
                    },
                    "secret": {
                        "name": "Secret Catalog",
                        "price": 300,
                        "redirect_url": "https://t.me/secret_channel",
                        "visible": True
                    }
                }
            }
        }


def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        return False


def save_uploaded_file(file: UploadFile) -> str:
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return f"/uploads/{filename}"
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return ""


def get_file_type(filename: str) -> str:
    extension = filename.lower().split('.')[-1]
    image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
    video_extensions = ['mp4', 'avi', 'mov', 'mkv', 'webm']

    if extension in image_extensions:
        return 'image'
    elif extension in video_extensions:
        return 'video'
    else:
        return 'file'


@app.get("/")
async def admin_dashboard():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Panel - Muji</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
            body { background: #1a1a1a; color: #ffffff; padding: 20px; min-height: 100vh; }
            .container { max-width: 1400px; margin: 0 auto; }

            header { 
                text-align: center; margin-bottom: 30px; padding: 30px; 
                background: linear-gradient(135deg, #ff6b9d 0%, #8b225e 100%); 
                border-radius: 15px; border: 1px solid #ff6b9d;
            }

            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .stat-card { background: rgba(255, 107, 157, 0.2); padding: 25px; border-radius: 15px; text-align: center; border: 1px solid #ff6b9d; }

            .tabs { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
            .tab { padding: 15px 25px; background: #ff6b9d; border: none; color: white; border-radius: 10px; cursor: pointer; font-weight: 600; transition: all 0.3s ease; }
            .tab:hover { background: #ff8fab; transform: translateY(-2px); }
            .tab.active { background: #ff8fab; box-shadow: 0 5px 15px rgba(255, 143, 171, 0.4); }

            .content { display: none; background: rgba(255, 107, 157, 0.1); padding: 30px; border-radius: 15px; margin-bottom: 20px; border: 1px solid #ff6b9d; }
            .content.active { display: block; }

            .profile-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 20px; }
            .profile-card { background: rgba(255, 107, 157, 0.1); padding: 20px; border-radius: 15px; border: 1px solid #ff6b9d; }

            .profile-header { display: flex; align-items: center; gap: 15px; margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid rgba(255, 107, 157, 0.3); }
            .profile-id { background: #ff6b9d; color: white; padding: 5px 10px; border-radius: 8px; font-weight: 600; font-size: 14px; }
            .profile-name { font-size: 18px; font-weight: 700; color: #ff6b9d; }

            .btn { padding: 12px 20px; border: none; border-radius: 8px; cursor: pointer; margin: 5px 2px; font-size: 14px; font-weight: 600; transition: all 0.3s ease; }
            .btn-primary { background: #ff6b9d; color: white; }
            .btn-primary:hover { background: #ff8fab; transform: translateY(-2px); }
            .btn-danger { background: #dc3545; color: white; }
            .btn-danger:hover { background: #e74c3c; transform: translateY(-2px); }
            .btn-success { background: #28a745; color: white; }
            .btn-success:hover { background: #2ecc71; transform: translateY(-2px); }
            .btn-warning { background: #ff8c00; color: white; }
            .btn-warning:hover { background: #ffa500; transform: translateY(-2px); }
            .btn-system { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            .btn-system:hover { background: linear-gradient(135deg, #764ba2 0%, #667eea 100%); transform: translateY(-2px); }
            .btn-info { background: linear-gradient(135deg, #17a2b8 0%, #138496 100%); color: white; }
            .btn-info:hover { background: linear-gradient(135deg, #138496 0%, #117a8b 100%); transform: translateY(-2px); }

            .form-group { margin-bottom: 20px; }
            .form-group label { display: block; margin-bottom: 8px; color: #ff6b9d; font-weight: 600; }
            .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 12px; background: rgba(255, 107, 157, 0.1); border: 1px solid #ff6b9d; border-radius: 8px; color: #fff; font-size: 14px; outline: none; }
            .form-group textarea { min-height: 80px; resize: vertical; }

            .photo-preview { display: flex; gap: 10px; margin: 10px 0; flex-wrap: wrap; }
            .photo-preview img { width: 80px; height: 80px; object-fit: cover; border-radius: 8px; border: 1px solid #ff6b9d; }

            .profile-stats { display: flex; gap: 10px; margin: 10px 0; flex-wrap: wrap; }
            .stat-badge { background: rgba(255, 107, 157, 0.2); padding: 6px 12px; border-radius: 8px; font-size: 12px; border: 1px solid #ff6b9d; color: #ff6b9d; }

            .file-upload {
                margin: 15px 0; padding: 15px;
                background: linear-gradient(135deg, #8b225e 0%, #1a1a1a 50%, #000000 100%);
                border: 2px dashed #ff6b9d; border-radius: 10px; text-align: center; cursor: pointer;
                position: relative; overflow: hidden;
            }
            .file-upload::before {
                content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
                background: linear-gradient(90deg, #ff6b9d, #8b225e, #ff6b9d);
                animation: sunset-glow 2s infinite;
            }
            @keyframes sunset-glow {
                0% { background-position: -200px 0; }
                100% { background-position: 200px 0; }
            }

            .uploaded-photos { display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 10px; margin: 15px 0; }
            .uploaded-photo { position: relative; width: 100px; height: 100px; border-radius: 8px; overflow: hidden; border: 1px solid #ff6b9d; }
            .uploaded-photo img { width: 100%; height: 100%; object-fit: cover; }
            .remove-photo { position: absolute; top: 5px; right: 5px; background: rgba(220, 53, 69, 0.8); color: white; border: none; border-radius: 50%; width: 20px; height: 20px; font-size: 12px; cursor: pointer; }

            .chat-file-upload { margin: 10px 0; padding: 15px; background: rgba(255, 107, 157, 0.05); border: 2px dashed #ff6b9d; border-radius: 8px; text-align: center; }
            .chat-file-list { margin-top: 10px; }
            .file-item { display: flex; align-items: center; gap: 10px; padding: 8px; background: rgba(255, 107, 157, 0.1); border-radius: 6px; margin: 5px 0; font-size: 14px; color: #ff6b9d; }
            .remove-file { color: #ff6b9d; cursor: pointer; font-weight: bold; margin-left: auto; }

            .chat-message { padding: 15px; margin: 10px 0; border-radius: 10px; border: 1px solid #ff6b9d; }
            .user-message { background: rgba(255, 107, 157, 0.1); margin-left: 20px; border-left: 3px solid #ff6b9d; }
            .admin-message { background: rgba(255, 107, 157, 0.2); margin-right: 20px; border-right: 3px solid #ff8fab; }
            .message-sender { font-weight: bold; margin-bottom: 8px; color: #ff6b9d; }
            .back-btn { background: #6c757d; color: white; padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; margin-bottom: 20px; transition: all 0.3s ease; }
            .back-btn:hover { background: #5a6268; transform: translateY(-2px); }
            .chat-attachment { display: flex; gap: 15px; align-items: flex-start; margin: 15px 0; flex-wrap: wrap; }
            .attachment-preview { max-width: 120px; max-height: 120px; border-radius: 8px; border: 1px solid #ff6b9d; }

            /* Стиль для системных сообщений */
            .system-message { text-align: center; margin: 20px 0; }
            .system-bubble { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; padding: 15px 25px; border-radius: 25px; 
                display: inline-block; max-width: 80%; font-size: 14px; font-weight: 500; 
                border: 1px solid rgba(255,255,255,0.2); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
            }

            /* Стили для промокодов */
            .promocode-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
            .promocode-card { background: rgba(255, 107, 157, 0.1); padding: 20px; border-radius: 15px; border: 1px solid #ff6b9d; }
            .promocode-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
            .promocode-code { font-size: 20px; font-weight: 700; color: #ff6b9d; letter-spacing: 2px; }
            .promocode-discount { background: #28a745; color: white; padding: 5px 10px; border-radius: 8px; font-weight: 600; }
            .promocode-status { display: inline-block; padding: 5px 10px; border-radius: 8px; font-size: 12px; font-weight: 600; }
            .status-active { background: #28a745; color: white; }
            .status-inactive { background: #dc3545; color: white; }

            /* Стили для баннера */
            .banner-settings { background: rgba(255, 107, 157, 0.1); padding: 20px; border-radius: 15px; border: 1px solid #ff6b9d; margin-bottom: 20px; }
            .banner-preview { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin: 15px 0; color: white; }
            .banner-text { font-size: 16px; margin-bottom: 10px; }
            .banner-link { color: white; text-decoration: underline; font-weight: 600; }
            .switch { position: relative; display: inline-block; width: 60px; height: 34px; margin-left: 15px; }
            .switch input { opacity: 0; width: 0; height: 0; }
            .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; transition: .4s; border-radius: 34px; }
            .slider:before { position: absolute; content: ""; height: 26px; width: 26px; left: 4px; bottom: 4px; background-color: white; transition: .4s; border-radius: 50%; }
            input:checked + .slider { background-color: #ff6b9d; }
            input:checked + .slider:before { transform: translateX(26px); }

            /* Стили для комментариев */
            .comments-section { margin-top: 30px; }
            .comment { background: rgba(255, 107, 157, 0.05); padding: 15px; border-radius: 10px; margin-bottom: 15px; border: 1px solid rgba(255, 107, 157, 0.2); }
            .comment-header { display: flex; justify-content: between; align-items: center; margin-bottom: 10px; }
            .comment-author { font-weight: 600; color: #ff6b9d; }
            .comment-date { color: #b0b0b0; font-size: 12px; margin-left: auto; }
            .comment-text { color: #ffffff; line-height: 1.5; }
            .comment-actions { margin-top: 10px; }
            .delete-comment { background: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer; font-size: 12px; }
            .delete-comment:hover { background: #c82333; }

            /* Стили для управления комментариями */
            .comments-management { margin-top: 30px; }
            .comment-management-item { background: rgba(255, 107, 157, 0.05); padding: 15px; border-radius: 10px; margin-bottom: 15px; border: 1px solid rgba(255, 107, 157, 0.2); }
            .comment-management-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
            .comment-profile { font-weight: 600; color: #ff6b9d; }

            /* Стили для VIP каталогов */
            .vip-catalogs-settings { background: rgba(255, 107, 157, 0.1); padding: 20px; border-radius: 15px; border: 1px solid #ff6b9d; margin-bottom: 20px; }
            .catalog-item { background: rgba(255, 107, 157, 0.05); padding: 20px; border-radius: 12px; margin-bottom: 15px; border: 1px solid rgba(255, 107, 157, 0.2); }
            .catalog-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
            .catalog-name { font-size: 18px; font-weight: 700; color: #ff6b9d; }
            .catalog-price { background: #28a745; color: white; padding: 5px 10px; border-radius: 8px; font-weight: 600; }

            /* Стили для VIP анкет */
            .vip-profile-card { background: rgba(102, 126, 234, 0.1); padding: 20px; border-radius: 15px; border: 1px solid #667eea; margin-bottom: 15px; }
            .vip-profile-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
            .vip-profile-name { font-size: 18px; font-weight: 700; color: #667eea; }
            .vip-profile-age { background: #667eea; color: white; padding: 5px 10px; border-radius: 8px; font-weight: 600; }

            /* Стили для управления VIP превью */
            .vip-preview-management { background: rgba(102, 126, 234, 0.1); padding: 20px; border-radius: 15px; border: 1px solid #667eea; margin-bottom: 20px; }
            .vip-preview-item { background: rgba(102, 126, 234, 0.05); padding: 15px; border-radius: 10px; margin-bottom: 15px; border: 1px solid rgba(102, 126, 234, 0.2); }
            .vip-preview-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
            .vip-preview-name { font-weight: 600; color: #667eea; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Admin Panel - Muji</h1>
                <p>App Configuration | Crypto Wallets | VIP Catalogs</p>
            </header>

            <div class="stats">
                <div class="stat-card"><h3>Profiles</h3><p id="profiles-count">0</p></div>
                <div class="stat-card"><h3>VIP Profiles</h3><p id="vip-profiles-count">0</p></div>
                <div class="stat-card"><h3>Chats</h3><p id="chats-count">0</p></div>
                <div class="stat-card"><h3>Messages</h3><p id="messages-count">0</p></div>
                <div class="stat-card"><h3>Comments</h3><p id="comments-count">0</p></div>
                <div class="stat-card"><h3>Promocodes</h3><p id="promocodes-count">0</p></div>
            </div>

            <div class="tabs">
                <button class="tab active" onclick="showTab('profiles')">Profiles</button>
                <button class="tab" onclick="showTab('chats')">Chats</button>
                <button class="tab" onclick="showTab('comments')">Comments</button>
                <button class="tab" onclick="showTab('add-profile')">Add Profile</button>
                <button class="tab" onclick="showTab('promocodes')">Promocodes</button>
                <button class="tab" onclick="showTab('banner-settings')">Banner Settings</button>
                <button class="tab" onclick="showTab('crypto-settings')">Crypto Settings</button>
                <button class="tab" onclick="showTab('vip-catalogs')">VIP Catalogs</button>
            </div>

            <div id="profiles" class="content active">
                <h3>Manage Profiles</h3>
                <div id="profiles-list" class="profile-grid"></div>
            </div>


            <div id="chats" class="content">
                <h3>Manage Chats</h3>
                <div id="chats-list"></div>
            </div>

            <div id="comments" class="content">
                <h3>Manage Comments</h3>
                <div class="comments-management">
                    <div id="comments-list-admin"></div>
                </div>
            </div>

            <div id="add-profile" class="content">
                <h3>Add New Profile</h3>
                <form id="add-profile-form" enctype="multipart/form-data">
                    <div class="form-group">
                        <label>Name:</label>
                        <input type="text" id="name" required>
                    </div>

                    <div class="form-group">
                        <label>Age:</label>
                        <input type="number" id="age" required min="18" max="100">
                    </div>

                    <div class="form-group">
                        <label>Gender:</label>
                        <select id="gender" required>
                            <option value="female">Female</option>
                            <option value="male">Male</option>
                            <option value="transgender">Transgender</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Nationality:</label>
                        <input type="text" id="nationality" required placeholder="e.g., Russian, Japanese, Korean">
                    </div>

                    <div class="form-group">
                        <label>City:</label>
                        <input type="text" id="city" required placeholder="e.g., Moscow">
                    </div>

                    <div class="form-group">
                        <label>Travel Cities (comma separated):</label>
                        <input type="text" id="travel-cities" placeholder="Moscow, Saint Petersburg, London">
                        <small style="color: #ff6b9d;">Cities where the profile can travel to</small>
                    </div>

                    <div class="form-group">
                        <label>Height (cm):</label>
                        <input type="number" id="height" required min="120" max="220" value="165">
                    </div>

                    <div class="form-group">
                        <label>Weight (kg):</label>
                        <input type="number" id="weight" required min="35" max="120" value="55">
                    </div>

                    <div class="form-group">
                        <label>Chest size:</label>
                        <select id="chest" required>
                            <option value="1">1 chest</option>
                            <option value="2">2 chest</option>
                            <option value="3" selected>3 chest</option>
                            <option value="4">4 chest</option>
                            <option value="5">5 chest</option>
                            <option value="6">6 chest</option>
                            <option value="7">7 chest</option>
                            <option value="8">8 chest</option>
                            <option value="9">9 chest</option>
                            <option value="10">10 chest</option>
                            <option value="11">11 chest</option>
                            <option value="12">12 chest</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Description:</label>
                        <textarea id="description" required placeholder="Enter profile description..."></textarea>
                    </div>

                    <div class="form-group">
                        <label>Upload Photos:</label>
                        <div class="file-upload">
                            <input type="file" id="photo-upload" accept="image/*" multiple style="display: none;">
                            <button type="button" class="btn btn-primary" onclick="document.getElementById('photo-upload').click()">
                                Select Photos (Multiple)
                            </button>
                            <div class="uploaded-photos" id="uploaded-photos"></div>
                        </div>
                    </div>

                    <button type="submit" class="btn btn-success">Add Profile</button>
                </form>
            </div>


            <div id="promocodes" class="content">
                <h3>Manage Promocodes</h3>
                <div class="form-group">
                    <label>Create New Promocode:</label>
                    <div style="display: flex; gap: 10px;">
                        <input type="text" id="promocode-code" placeholder="Enter promocode (e.g., WELCOME15)" style="flex: 1;">
                        <input type="number" id="promocode-discount" placeholder="Discount %" min="1" max="100" value="15" style="width: 120px;">
                        <button class="btn btn-success" onclick="createPromocode()">Create</button>
                    </div>
                </div>
                <div id="promocodes-list" class="promocode-grid"></div>
            </div>

            <div id="banner-settings" class="content">
                <h3>Banner Settings</h3>
                <div class="banner-settings">
                    <div class="form-group">
                        <label>Banner Text:</label>
                        <input type="text" id="banner-text" placeholder="Enter banner text...">
                    </div>
                    <div class="form-group">
                        <label>Banner Link:</label>
                        <input type="text" id="banner-link" placeholder="https://t.me/yourchannel">
                    </div>
                    <div class="form-group">
                        <label>Link Text:</label>
                        <input type="text" id="banner-link-text" placeholder="Join Channel">
                    </div>
                    <div class="form-group">
                        <label style="display: flex; align-items: center;">
                            Show Banner:
                            <label class="switch">
                                <input type="checkbox" id="banner-visible">
                                <span class="slider"></span>
                            </label>
                        </label>
                    </div>
                    <div class="banner-preview" id="banner-preview">
                        <div class="banner-text" id="preview-text">Banner preview text</div>
                        <a href="#" class="banner-link" id="preview-link">Preview Link</a>
                    </div>
                    <button class="btn btn-primary" onclick="saveBannerSettings()">Save Banner Settings</button>
                </div>
            </div>

            <div id="crypto-settings" class="content">
                <h3>Crypto Wallet Settings</h3>
                <div class="crypto-settings">
                    <div class="form-group">
                        <label>TRC20 Wallet Address:</label>
                        <input type="text" id="trc20-wallet" class="wallet-address" value="TY76gU8J9o8j7U6tY5r4E3W2Q1">
                    </div>
                    <div class="form-group">
                        <label>ERC20 Wallet Address:</label>
                        <input type="text" id="erc20-wallet" class="wallet-address" value="0x8a9C6e5D8b0E2a1F3c4B6E7D8C9A0B1C2D3E4F5">
                    </div>
                    <div class="form-group">
                        <label>BNB Wallet Address:</label>
                        <input type="text" id="bnb-wallet" class="wallet-address" value="bnb1q3e5r7t9y1u3i5o7p9l1k3j5h7g9f2d4s6q8w0">
                    </div>
                    <button class="btn btn-primary" onclick="saveCryptoWallets()">Save Wallet Addresses</button>
                </div>
            </div>

            <div id="vip-catalogs" class="content">
                <h3>VIP Catalogs Settings</h3>
                <div class="vip-catalogs-settings">
                    <div class="catalog-item">
                        <div class="catalog-header">
                            <span class="catalog-name">VIP Catalog</span>
                            <span class="catalog-price">$100</span>
                        </div>
                        <div class="form-group">
                            <label>Catalog Name:</label>
                            <input type="text" id="vip-catalog-name" class="catalog-input" value="VIP Catalog">
                        </div>
                        <div class="form-group">
                            <label>Price ($):</label>
                            <input type="number" id="vip-catalog-price" class="catalog-input" value="100" min="0">
                        </div>
                        <div class="form-group">
                            <label>Redirect URL:</label>
                            <input type="text" id="vip-catalog-url" class="catalog-input" value="https://t.me/vip_channel">
                        </div>
                        <div class="form-group">
                            <label>Preview Profiles Count:</label>
                            <input type="number" id="vip-catalog-preview-count" class="catalog-input" value="3" min="1" max="9">
                            <small style="color: #ff6b9d;">Number of blurred profiles to show in preview</small>
                        </div>

                        <h4 style="margin-top: 20px; color: #ff6b9d;">Preview Profiles</h4>
                        <div class="form-group">
                            <label>Profile 1 Name:</label>
                            <input type="text" id="vip-preview-1-name" class="catalog-input" placeholder="Anna">
                        </div>
                        <div class="form-group">
                            <label>Profile 1 Age:</label>
                            <input type="number" id="vip-preview-1-age" class="catalog-input" placeholder="23" min="18" max="100">
                        </div>
                        <div class="form-group">
                            <label>Profile 1 City:</label>
                            <input type="text" id="vip-preview-1-city" class="catalog-input" placeholder="Moscow">
                        </div>
                        <div class="form-group">
                            <label>Profile 1 Photo:</label>
                            <input type="file" id="vip-preview-1-photo" accept="image/*" style="display: none;">
                            <button type="button" class="btn btn-secondary" onclick="document.getElementById('vip-preview-1-photo').click()">Choose Photo</button>
                            <div id="vip-preview-1-photo-preview" style="margin-top: 10px;"></div>
                        </div>

                        <div class="form-group">
                            <label>Profile 2 Name:</label>
                            <input type="text" id="vip-preview-2-name" class="catalog-input" placeholder="Sofia">
                        </div>
                        <div class="form-group">
                            <label>Profile 2 Age:</label>
                            <input type="number" id="vip-preview-2-age" class="catalog-input" placeholder="21" min="18" max="100">
                        </div>
                        <div class="form-group">
                            <label>Profile 2 City:</label>
                            <input type="text" id="vip-preview-2-city" class="catalog-input" placeholder="Saint Petersburg">
                        </div>
                        <div class="form-group">
                            <label>Profile 2 Photo:</label>
                            <input type="file" id="vip-preview-2-photo" accept="image/*" style="display: none;">
                            <button type="button" class="btn btn-secondary" onclick="document.getElementById('vip-preview-2-photo').click()">Choose Photo</button>
                            <div id="vip-preview-2-photo-preview" style="margin-top: 10px;"></div>
                        </div>

                        <div class="form-group">
                            <label>Profile 3 Name:</label>
                            <input type="text" id="vip-preview-3-name" class="catalog-input" placeholder="Maria">
                        </div>
                        <div class="form-group">
                            <label>Profile 3 Age:</label>
                            <input type="number" id="vip-preview-3-age" class="catalog-input" placeholder="25" min="18" max="100">
                        </div>
                        <div class="form-group">
                            <label>Profile 3 City:</label>
                            <input type="text" id="vip-preview-3-city" class="catalog-input" placeholder="Kazan">
                        </div>
                        <div class="form-group">
                            <label>Profile 3 Photo:</label>
                            <input type="file" id="vip-preview-3-photo" accept="image/*" style="display: none;">
                            <button type="button" class="btn btn-secondary" onclick="document.getElementById('vip-preview-3-photo').click()">Choose Photo</button>
                            <div id="vip-preview-3-photo-preview" style="margin-top: 10px;"></div>
                        </div>

                        <div class="form-group">
                            <label style="display: flex; align-items: center;">
                                Show Catalog:
                                <label class="switch">
                                    <input type="checkbox" id="vip-catalog-visible" checked>
                                    <span class="slider"></span>
                                </label>
                            </label>
                        </div>
                    </div>

                    <div class="catalog-item">
                        <div class="catalog-header">
                            <span class="catalog-name">Extra VIP</span>
                            <span class="catalog-price">$200</span>
                        </div>
                        <div class="form-group">
                            <label>Catalog Name:</label>
                            <input type="text" id="extra-vip-catalog-name" class="catalog-input" value="Extra VIP">
                        </div>
                        <div class="form-group">
                            <label>Price ($):</label>
                            <input type="number" id="extra-vip-catalog-price" class="catalog-input" value="200" min="0">
                        </div>
                        <div class="form-group">
                            <label>Redirect URL:</label>
                            <input type="text" id="extra-vip-catalog-url" class="catalog-input" value="https://t.me/extra_vip_channel">
                        </div>
                        <div class="form-group">
                            <label>Preview Profiles Count:</label>
                            <input type="number" id="extra-vip-catalog-preview-count" class="catalog-input" value="3" min="1" max="9">
                            <small style="color: #ff6b9d;">Number of blurred profiles to show in preview</small>
                        </div>

                        <h4 style="margin-top: 20px; color: #ff6b9d;">Preview Profiles</h4>
                        <div class="form-group">
                            <label>Profile 1 Name:</label>
                            <input type="text" id="extra-vip-preview-1-name" class="catalog-input" placeholder="Elena">
                        </div>
                        <div class="form-group">
                            <label>Profile 1 Age:</label>
                            <input type="number" id="extra-vip-preview-1-age" class="catalog-input" placeholder="22" min="18" max="100">
                        </div>
                        <div class="form-group">
                            <label>Profile 1 City:</label>
                            <input type="text" id="extra-vip-preview-1-city" class="catalog-input" placeholder="Novosibirsk">
                        </div>
                        <div class="form-group">
                            <label>Profile 1 Photo:</label>
                            <input type="file" id="extra-vip-preview-1-photo" accept="image/*" style="display: none;">
                            <button type="button" class="btn btn-secondary" onclick="document.getElementById('extra-vip-preview-1-photo').click()">Choose Photo</button>
                            <div id="extra-vip-preview-1-photo-preview" style="margin-top: 10px;"></div>
                        </div>

                        <div class="form-group">
                            <label>Profile 2 Name:</label>
                            <input type="text" id="extra-vip-preview-2-name" class="catalog-input" placeholder="Victoria">
                        </div>
                        <div class="form-group">
                            <label>Profile 2 Age:</label>
                            <input type="number" id="extra-vip-preview-2-age" class="catalog-input" placeholder="24" min="18" max="100">
                        </div>
                        <div class="form-group">
                            <label>Profile 2 City:</label>
                            <input type="text" id="extra-vip-preview-2-city" class="catalog-input" placeholder="Yekaterinburg">
                        </div>
                        <div class="form-group">
                            <label>Profile 2 Photo:</label>
                            <input type="file" id="extra-vip-preview-2-photo" accept="image/*" style="display: none;">
                            <button type="button" class="btn btn-secondary" onclick="document.getElementById('extra-vip-preview-2-photo').click()">Choose Photo</button>
                            <div id="extra-vip-preview-2-photo-preview" style="margin-top: 10px;"></div>
                        </div>

                        <div class="form-group">
                            <label>Profile 3 Name:</label>
                            <input type="text" id="extra-vip-preview-3-name" class="catalog-input" placeholder="Daria">
                        </div>
                        <div class="form-group">
                            <label>Profile 3 Age:</label>
                            <input type="number" id="extra-vip-preview-3-age" class="catalog-input" placeholder="20" min="18" max="100">
                        </div>
                        <div class="form-group">
                            <label>Profile 3 City:</label>
                            <input type="text" id="extra-vip-preview-3-city" class="catalog-input" placeholder="Krasnoyarsk">
                        </div>
                        <div class="form-group">
                            <label>Profile 3 Photo:</label>
                            <input type="file" id="extra-vip-preview-3-photo" accept="image/*" style="display: none;">
                            <button type="button" class="btn btn-secondary" onclick="document.getElementById('extra-vip-preview-3-photo').click()">Choose Photo</button>
                            <div id="extra-vip-preview-3-photo-preview" style="margin-top: 10px;"></div>
                        </div>

                        <div class="form-group">
                            <label style="display: flex; align-items: center;">
                                Show Catalog:
                                <label class="switch">
                                    <input type="checkbox" id="extra-vip-catalog-visible" checked>
                                    <span class="slider"></span>
                                </label>
                            </label>
                        </div>
                    </div>

                    <div class="catalog-item">
                        <div class="catalog-header">
                            <span class="catalog-name">Secret Catalog</span>
                            <span class="catalog-price">$300</span>
                        </div>
                        <div class="form-group">
                            <label>Catalog Name:</label>
                            <input type="text" id="secret-catalog-name" class="catalog-input" value="Secret Catalog">
                        </div>
                        <div class="form-group">
                            <label>Price ($):</label>
                            <input type="number" id="secret-catalog-price" class="catalog-input" value="300" min="0">
                        </div>
                        <div class="form-group">
                            <label>Redirect URL:</label>
                            <input type="text" id="secret-catalog-url" class="catalog-input" value="https://t.me/secret_channel">
                        </div>
                        <div class="form-group">
                            <label>Preview Profiles Count:</label>
                            <input type="number" id="secret-catalog-preview-count" class="catalog-input" value="3" min="1" max="9">
                            <small style="color: #ff6b9d;">Number of blurred profiles to show in preview</small>
                        </div>

                        <h4 style="margin-top: 20px; color: #ff6b9d;">Preview Profiles</h4>
                        <div class="form-group">
                            <label>Profile 1 Name:</label>
                            <input type="text" id="secret-preview-1-name" class="catalog-input" placeholder="Anastasia">
                        </div>
                        <div class="form-group">
                            <label>Profile 1 Age:</label>
                            <input type="number" id="secret-preview-1-age" class="catalog-input" placeholder="26" min="18" max="100">
                        </div>
                        <div class="form-group">
                            <label>Profile 1 City:</label>
                            <input type="text" id="secret-preview-1-city" class="catalog-input" placeholder="Vladivostok">
                        </div>
                        <div class="form-group">
                            <label>Profile 1 Photo:</label>
                            <input type="file" id="secret-preview-1-photo" accept="image/*" style="display: none;">
                            <button type="button" class="btn btn-secondary" onclick="document.getElementById('secret-preview-1-photo').click()">Choose Photo</button>
                            <div id="secret-preview-1-photo-preview" style="margin-top: 10px;"></div>
                        </div>

                        <div class="form-group">
                            <label>Profile 2 Name:</label>
                            <input type="text" id="secret-preview-2-name" class="catalog-input" placeholder="Polina">
                        </div>
                        <div class="form-group">
                            <label>Profile 2 Age:</label>
                            <input type="number" id="secret-preview-2-age" class="catalog-input" placeholder="23" min="18" max="100">
                        </div>
                        <div class="form-group">
                            <label>Profile 2 City:</label>
                            <input type="text" id="secret-preview-2-city" class="catalog-input" placeholder="Rostov">
                        </div>
                        <div class="form-group">
                            <label>Profile 2 Photo:</label>
                            <input type="file" id="secret-preview-2-photo" accept="image/*" style="display: none;">
                            <button type="button" class="btn btn-secondary" onclick="document.getElementById('secret-preview-2-photo').click()">Choose Photo</button>
                            <div id="secret-preview-2-photo-preview" style="margin-top: 10px;"></div>
                        </div>

                        <div class="form-group">
                            <label>Profile 3 Name:</label>
                            <input type="text" id="secret-preview-3-name" class="catalog-input" placeholder="Alina">
                        </div>
                        <div class="form-group">
                            <label>Profile 3 Age:</label>
                            <input type="number" id="secret-preview-3-age" class="catalog-input" placeholder="21" min="18" max="100">
                        </div>
                        <div class="form-group">
                            <label>Profile 3 City:</label>
                            <input type="text" id="secret-preview-3-city" class="catalog-input" placeholder="Sochi">
                        </div>
                        <div class="form-group">
                            <label>Profile 3 Photo:</label>
                            <input type="file" id="secret-preview-3-photo" accept="image/*" style="display: none;">
                            <button type="button" class="btn btn-secondary" onclick="document.getElementById('secret-preview-3-photo').click()">Choose Photo</button>
                            <div id="secret-preview-3-photo-preview" style="margin-top: 10px;"></div>
                        </div>

                        <div class="form-group">
                            <label style="display: flex; align-items: center;">
                                Show Catalog:
                                <label class="switch">
                                    <input type="checkbox" id="secret-catalog-visible" checked>
                                    <span class="slider"></span>
                                </label>
                            </label>
                        </div>
                    </div>

                    <button class="btn btn-primary" onclick="saveVipCatalogs()">Save VIP Catalogs Settings</button>
                </div>
            </div>

        </div>

        <script>
            let uploadedPhotoFiles = [];
            let uploadedVipPhotoFiles = [];
            let availableVipProfiles = [];
            let selectedPreviewProfiles = [];
            let vipPreviewPhotos = {
                vip: ['', '', ''],
                extra_vip: ['', '', ''],
                secret: ['', '', '']
            };

            // Функции для переключения вкладок
            function showTab(tabName) {
                document.querySelectorAll('.content').forEach(tab => tab.classList.remove('active'));
                document.querySelectorAll('.tab').forEach(btn => btn.classList.remove('active'));
                document.getElementById(tabName).classList.add('active');
                event.target.classList.add('active');

                if (tabName === 'profiles') loadProfiles();
                if (tabName === 'chats') loadChats();
                if (tabName === 'comments') loadCommentsAdmin();
                if (tabName === 'promocodes') loadPromocodes();
                if (tabName === 'banner-settings') loadBannerSettings();
                if (tabName === 'crypto-settings') loadCryptoWallets();
                if (tabName === 'vip-catalogs') loadVipCatalogs();
            }

            // Загрузка статистики
            async function loadStats() {
                try {
                    const response = await fetch('/api/stats');
                    const stats = await response.json();
                    document.getElementById('profiles-count').textContent = stats.profiles_count;
                    document.getElementById('vip-profiles-count').textContent = stats.vip_profiles_count;
                    document.getElementById('chats-count').textContent = stats.chats_count;
                    document.getElementById('messages-count').textContent = stats.messages_count;
                    document.getElementById('comments-count').textContent = stats.comments_count;
                    document.getElementById('promocodes-count').textContent = stats.promocodes_count;
                } catch (error) {
                    console.error('Error loading stats:', error);
                }
            }

            // Загрузка анкет
            async function loadProfiles() {
                try {
                    const response = await fetch('/api/admin/profiles');
                    const data = await response.json();
                    const list = document.getElementById('profiles-list');
                    list.innerHTML = '';

                    data.profiles.forEach(profile => {
                        const travelCities = profile.travel_cities ? profile.travel_cities.join(', ') : 'None';
                        const photosHtml = profile.photos.map(photo => 
                            `<img src="http://localhost:8002${photo}" alt="Profile photo" style="width: 60px; height: 60px; object-fit: cover; border-radius: 8px; border: 1px solid #ff6b9d;">`
                        ).join('');

                        const profileDiv = document.createElement('div');
                        profileDiv.className = 'profile-card';
                        profileDiv.innerHTML = `
                            <div class="profile-header">
                                <span class="profile-id">ID: ${profile.id}</span>
                                <span class="profile-name">${profile.name}</span>
                            </div>
                            <p><strong>Gender:</strong> ${profile.gender || 'Not specified'}</p>
                            <p><strong>Nationality:</strong> ${profile.nationality || 'Not specified'}</p>
                            <p><strong>City:</strong> ${profile.city}</p>
                            <p><strong>Travel Cities:</strong> ${travelCities}</p>
                            <div class="profile-stats">
                                <span class="stat-badge">Height: ${profile.height} cm</span>
                                <span class="stat-badge">Weight: ${profile.weight} kg</span>
                                <span class="stat-badge">Chest: ${profile.chest}</span>
                            </div>
                            <p><strong>Description:</strong> ${profile.description}</p>
                            <p><strong>Status:</strong> ${profile.visible ? 'Visible' : 'Hidden'}</p>
                            <p><strong>Photos:</strong></p>
                            <div class="photo-preview">
                                ${photosHtml}
                            </div>
                            <div style="margin-top: 15px;">
                                <button class="btn btn-warning" onclick="toggleProfile(${profile.id}, ${!profile.visible})">
                                    ${profile.visible ? 'Hide' : 'Show'}
                                </button>
                                <button class="btn btn-danger" onclick="deleteProfile(${profile.id})">
                                    Delete
                                </button>
                            </div>
                        `;
                        list.appendChild(profileDiv);
                    });

                    loadStats();
                } catch (error) {
                    console.error('Error loading profiles:', error);
                }
            }

            // Загрузка VIP анкет
            async function loadVipProfiles() {
                try {
                    const response = await fetch('/api/admin/vip-profiles');
                    const data = await response.json();
                    const list = document.getElementById('vip-profiles-list');
                    list.innerHTML = '';

                    data.profiles.forEach(profile => {
                        const photosHtml = profile.photos.map(photo => 
                            `<img src="http://localhost:8002${photo}" alt="Profile photo" style="width: 60px; height: 60px; object-fit: cover; border-radius: 8px; border: 1px solid #667eea;">`
                        ).join('');

                        const profileDiv = document.createElement('div');
                        profileDiv.className = 'vip-profile-card';
                        profileDiv.innerHTML = `
                            <div class="vip-profile-header">
                                <span class="vip-profile-name">${profile.name}</span>
                                <span class="vip-profile-age">${profile.age} y.o.</span>
                            </div>
                            <p><strong>Gender:</strong> ${profile.gender || 'Not specified'}</p>
                            <p><strong>City:</strong> ${profile.city}</p>
                            <p><strong>Photos:</strong></p>
                            <div class="photo-preview">
                                ${photosHtml}
                            </div>
                            <div style="margin-top: 15px;">
                                <button class="btn btn-danger" onclick="deleteVipProfile(${profile.id})">
                                    Delete
                                </button>
                            </div>
                        `;
                        list.appendChild(profileDiv);
                    });

                    loadStats();
                } catch (error) {
                    console.error('Error loading VIP profiles:', error);
                }
            }

            // Удаление VIP анкеты
            async function deleteVipProfile(profileId) {
                if (!confirm('Delete VIP profile? This action cannot be undone!')) return;

                try {
                    const response = await fetch(`/api/admin/vip-profiles/${profileId}`, {method: 'DELETE'});
                    if (response.ok) {
                        alert('VIP Profile deleted!');
                        loadVipProfiles();
                    } else {
                        alert('Error deleting VIP profile');
                    }
                } catch (error) {
                    console.error('Error deleting VIP profile:', error);
                    alert('Error deleting VIP profile');
                }
            }

            // Переключение видимости анкеты
            async function toggleProfile(profileId, visible) {
                if (!confirm(visible ? 'Show profile?' : 'Hide profile?')) return;

                try {
                    await fetch(`/api/admin/profiles/${profileId}/toggle`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ visible: visible })
                    });
                    loadProfiles();
                } catch (error) {
                    console.error('Error toggling profile:', error);
                    alert('Error updating profile');
                }
            }

            // Удаление анкеты
            async function deleteProfile(profileId) {
                if (!confirm('Delete profile? This action cannot be undone!')) return;

                try {
                    const response = await fetch(`/api/admin/profiles/${profileId}`, {method: 'DELETE'});
                    if (response.ok) {
                        alert('Profile deleted!');
                        loadProfiles();
                    } else {
                        alert('Error deleting profile');
                    }
                } catch (error) {
                    console.error('Error deleting profile:', error);
                    alert('Error deleting profile');
                }
            }

            // Загрузка VIP каталогов
            async function loadVipCatalogs() {
                try {
                    const response = await fetch('/api/vip-catalogs');
                    const catalogs = await response.json();

                    document.getElementById('vip-catalog-name').value = catalogs.vip?.name || 'VIP Catalog';
                    document.getElementById('vip-catalog-price').value = catalogs.vip?.price || 100;
                    document.getElementById('vip-catalog-url').value = catalogs.vip?.redirect_url || 'https://t.me/vip_channel';
                    document.getElementById('vip-catalog-preview-count').value = catalogs.vip?.preview_count || 3;
                    document.getElementById('vip-catalog-visible').checked = catalogs.vip?.visible !== false;
                    if (catalogs.vip?.preview_profiles) {
                        for (let i = 0; i < 3; i++) {
                            const profile = catalogs.vip.preview_profiles[i] || {};
                            document.getElementById(`vip-preview-${i+1}-name`).value = profile.name || '';
                            document.getElementById(`vip-preview-${i+1}-age`).value = profile.age || '';
                            document.getElementById(`vip-preview-${i+1}-city`).value = profile.city || '';
                            vipPreviewPhotos.vip[i] = profile.photo || '';
                            if (profile.photo) {
                                showPhotoPreview(`vip-preview-${i+1}-photo-preview`, profile.photo);
                            }
                        }
                    }

                    document.getElementById('extra-vip-catalog-name').value = catalogs.extra_vip?.name || 'Extra VIP';
                    document.getElementById('extra-vip-catalog-price').value = catalogs.extra_vip?.price || 200;
                    document.getElementById('extra-vip-catalog-url').value = catalogs.extra_vip?.redirect_url || 'https://t.me/extra_vip_channel';
                    document.getElementById('extra-vip-catalog-preview-count').value = catalogs.extra_vip?.preview_count || 3;
                    document.getElementById('extra-vip-catalog-visible').checked = catalogs.extra_vip?.visible !== false;
                    if (catalogs.extra_vip?.preview_profiles) {
                        for (let i = 0; i < 3; i++) {
                            const profile = catalogs.extra_vip.preview_profiles[i] || {};
                            document.getElementById(`extra-vip-preview-${i+1}-name`).value = profile.name || '';
                            document.getElementById(`extra-vip-preview-${i+1}-age`).value = profile.age || '';
                            document.getElementById(`extra-vip-preview-${i+1}-city`).value = profile.city || '';
                            vipPreviewPhotos.extra_vip[i] = profile.photo || '';
                            if (profile.photo) {
                                showPhotoPreview(`extra-vip-preview-${i+1}-photo-preview`, profile.photo);
                            }
                        }
                    }

                    document.getElementById('secret-catalog-name').value = catalogs.secret?.name || 'Secret Catalog';
                    document.getElementById('secret-catalog-price').value = catalogs.secret?.price || 300;
                    document.getElementById('secret-catalog-url').value = catalogs.secret?.redirect_url || 'https://t.me/secret_channel';
                    document.getElementById('secret-catalog-preview-count').value = catalogs.secret?.preview_count || 3;
                    document.getElementById('secret-catalog-visible').checked = catalogs.secret?.visible !== false;
                    if (catalogs.secret?.preview_profiles) {
                        for (let i = 0; i < 3; i++) {
                            const profile = catalogs.secret.preview_profiles[i] || {};
                            document.getElementById(`secret-preview-${i+1}-name`).value = profile.name || '';
                            document.getElementById(`secret-preview-${i+1}-age`).value = profile.age || '';
                            document.getElementById(`secret-preview-${i+1}-city`).value = profile.city || '';
                            vipPreviewPhotos.secret[i] = profile.photo || '';
                            if (profile.photo) {
                                showPhotoPreview(`secret-preview-${i+1}-photo-preview`, profile.photo);
                            }
                        }
                    }
                } catch (error) {
                    console.error('Error loading VIP catalogs:', error);
                }
            }

            // Сохранение VIP каталогов
            async function saveVipCatalogs() {
                try {
                    const catalogs = {
                        vip: {
                            name: document.getElementById('vip-catalog-name').value,
                            price: parseInt(document.getElementById('vip-catalog-price').value),
                            redirect_url: document.getElementById('vip-catalog-url').value,
                            preview_count: parseInt(document.getElementById('vip-catalog-preview-count').value),
                            visible: document.getElementById('vip-catalog-visible').checked,
                            preview_profiles: [
                                {
                                    name: document.getElementById('vip-preview-1-name').value,
                                    age: parseInt(document.getElementById('vip-preview-1-age').value) || 0,
                                    city: document.getElementById('vip-preview-1-city').value,
                                    photo: vipPreviewPhotos.vip[0] || ''
                                },
                                {
                                    name: document.getElementById('vip-preview-2-name').value,
                                    age: parseInt(document.getElementById('vip-preview-2-age').value) || 0,
                                    city: document.getElementById('vip-preview-2-city').value,
                                    photo: vipPreviewPhotos.vip[1] || ''
                                },
                                {
                                    name: document.getElementById('vip-preview-3-name').value,
                                    age: parseInt(document.getElementById('vip-preview-3-age').value) || 0,
                                    city: document.getElementById('vip-preview-3-city').value,
                                    photo: vipPreviewPhotos.vip[2] || ''
                                }
                            ]
                        },
                        extra_vip: {
                            name: document.getElementById('extra-vip-catalog-name').value,
                            price: parseInt(document.getElementById('extra-vip-catalog-price').value),
                            redirect_url: document.getElementById('extra-vip-catalog-url').value,
                            preview_count: parseInt(document.getElementById('extra-vip-catalog-preview-count').value),
                            visible: document.getElementById('extra-vip-catalog-visible').checked,
                            preview_profiles: [
                                {
                                    name: document.getElementById('extra-vip-preview-1-name').value,
                                    age: parseInt(document.getElementById('extra-vip-preview-1-age').value) || 0,
                                    city: document.getElementById('extra-vip-preview-1-city').value,
                                    photo: vipPreviewPhotos.extra_vip[0] || ''
                                },
                                {
                                    name: document.getElementById('extra-vip-preview-2-name').value,
                                    age: parseInt(document.getElementById('extra-vip-preview-2-age').value) || 0,
                                    city: document.getElementById('extra-vip-preview-2-city').value,
                                    photo: vipPreviewPhotos.extra_vip[1] || ''
                                },
                                {
                                    name: document.getElementById('extra-vip-preview-3-name').value,
                                    age: parseInt(document.getElementById('extra-vip-preview-3-age').value) || 0,
                                    city: document.getElementById('extra-vip-preview-3-city').value,
                                    photo: vipPreviewPhotos.extra_vip[2] || ''
                                }
                            ]
                        },
                        secret: {
                            name: document.getElementById('secret-catalog-name').value,
                            price: parseInt(document.getElementById('secret-catalog-price').value),
                            redirect_url: document.getElementById('secret-catalog-url').value,
                            preview_count: parseInt(document.getElementById('secret-catalog-preview-count').value),
                            visible: document.getElementById('secret-catalog-visible').checked,
                            preview_profiles: [
                                {
                                    name: document.getElementById('secret-preview-1-name').value,
                                    age: parseInt(document.getElementById('secret-preview-1-age').value) || 0,
                                    city: document.getElementById('secret-preview-1-city').value,
                                    photo: vipPreviewPhotos.secret[0] || ''
                                },
                                {
                                    name: document.getElementById('secret-preview-2-name').value,
                                    age: parseInt(document.getElementById('secret-preview-2-age').value) || 0,
                                    city: document.getElementById('secret-preview-2-city').value,
                                    photo: vipPreviewPhotos.secret[1] || ''
                                },
                                {
                                    name: document.getElementById('secret-preview-3-name').value,
                                    age: parseInt(document.getElementById('secret-preview-3-age').value) || 0,
                                    city: document.getElementById('secret-preview-3-city').value,
                                    photo: vipPreviewPhotos.secret[2] || ''
                                }
                            ]
                        }
                    };

                    const response = await fetch('/api/vip-catalogs', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(catalogs)
                    });

                    if (response.ok) {
                        alert('VIP catalogs settings saved!');
                    } else {
                        alert('Error saving VIP catalogs settings');
                    }
                } catch (error) {
                    console.error('Error saving VIP catalogs:', error);
                    alert('Error saving VIP catalogs settings');
                }
            }

            // Функция отображения превью фото
            function showPhotoPreview(previewId, photoUrl) {
                const previewDiv = document.getElementById(previewId);
                if (previewDiv) {
                    previewDiv.innerHTML = `<img src="http://localhost:8002${photoUrl}" style="max-width: 200px; max-height: 150px; border-radius: 8px;">`;
                }
            }

            // Обработчики загрузки фото для preview профилей
            document.addEventListener('DOMContentLoaded', () => {
                // VIP catalog
                ['vip', 'extra-vip', 'secret'].forEach(catalog => {
                    for (let i = 1; i <= 3; i++) {
                        const inputId = `${catalog}-preview-${i}-photo`;
                        const previewId = `${catalog}-preview-${i}-photo-preview`;
                        const catalogKey = catalog.replace('-', '_');

                        const input = document.getElementById(inputId);
                        if (input) {
                            input.addEventListener('change', async function(e) {
                                const file = e.target.files[0];
                                if (file) {
                                    const formData = new FormData();
                                    formData.append('file', file);

                                    try {
                                        const response = await fetch('/api/vip-catalogs/upload-preview-photo', {
                                            method: 'POST',
                                            body: formData
                                        });

                                        if (response.ok) {
                                            const data = await response.json();
                                            vipPreviewPhotos[catalogKey][i-1] = data.photo_url;
                                            showPhotoPreview(previewId, data.photo_url);
                                        } else {
                                            alert('Error uploading photo');
                                        }
                                    } catch (error) {
                                        console.error('Error uploading photo:', error);
                                        alert('Error uploading photo');
                                    }
                                }
                            });
                        }
                    }
                });
            });

            // Загрузка управления VIP превью
            async function loadVipPreviewManagement() {
                await loadAvailableVipProfiles();
                await loadVipPreviewProfiles();
            }

            // Загрузка доступных VIP анкет
            async function loadAvailableVipProfiles() {
                try {
                    const response = await fetch('/api/admin/vip-profiles');
                    const data = await response.json();
                    availableVipProfiles = data.profiles;

                    const select = document.getElementById('available-vip-profiles');
                    select.innerHTML = '';

                    availableVipProfiles.forEach(profile => {
                        const option = document.createElement('option');
                        option.value = profile.id;
                        option.textContent = `${profile.name} (${profile.age} y.o., ${profile.city})`;
                        select.appendChild(option);
                    });
                } catch (error) {
                    console.error('Error loading VIP profiles:', error);
                }
            }

            // Загрузка выбранных превью профилей
            async function loadVipPreviewProfiles() {
                const catalogKey = document.getElementById('vip-catalog-select').value;
                // Здесь будет загрузка сохраненных превью профилей для выбранного каталога
                // Пока просто очищаем выбранные профили
                selectedPreviewProfiles = [];
                updateSelectedPreviewDisplay();
            }

            // Обновление отображения выбранных превью профилей
            function updateSelectedPreviewDisplay() {
                const container = document.getElementById('selected-preview-profiles');
                container.innerHTML = '';

                selectedPreviewProfiles.forEach(profileId => {
                    const profile = availableVipProfiles.find(p => p.id == profileId);
                    if (profile) {
                        const profileDiv = document.createElement('div');
                        profileDiv.className = 'vip-preview-item';
                        profileDiv.innerHTML = `
                            <div class="vip-preview-header">
                                <span class="vip-preview-name">${profile.name}</span>
                                <button class="btn btn-danger" onclick="removePreviewProfile(${profile.id})">Remove</button>
                            </div>
                            <p>Age: ${profile.age}</p>
                            <p>City: ${profile.city}</p>
                            <img src="http://localhost:8002${profile.photos[0]}" alt="${profile.name}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 8px;">
                        `;
                        container.appendChild(profileDiv);
                    }
                });
            }

            // Добавление профиля в превью
            function addPreviewProfile() {
                const select = document.getElementById('available-vip-profiles');
                const selectedOptions = Array.from(select.selectedOptions);

                selectedOptions.forEach(option => {
                    const profileId = parseInt(option.value);
                    if (!selectedPreviewProfiles.includes(profileId) && selectedPreviewProfiles.length < 3) {
                        selectedPreviewProfiles.push(profileId);
                    }
                });

                updateSelectedPreviewDisplay();
            }

            // Удаление профиля из превью
            function removePreviewProfile(profileId) {
                selectedPreviewProfiles = selectedPreviewProfiles.filter(id => id !== profileId);
                updateSelectedPreviewDisplay();
            }

            // Сохранение настроек превью
            async function saveVipPreview() {
                const catalogKey = document.getElementById('vip-catalog-select').value;

                // Здесь будет сохранение выбранных профилей для превью
                // Пока просто показываем сообщение
                alert(`Preview settings saved for ${catalogKey} catalog with ${selectedPreviewProfiles.length} profiles`);
            }

            // Загрузка чатов
            async function loadChats() {
                try {
                    const response = await fetch('/api/admin/chats');
                    const data = await response.json();
                    const list = document.getElementById('chats-list');
                    list.innerHTML = '';

                    if (data.chats.length === 0) {
                        list.innerHTML = '<p>No active chats</p>';
                        return;
                    }

                    data.chats.forEach(chat => {
                        const chatDiv = document.createElement('div');
                        chatDiv.className = 'profile-card';
                        chatDiv.innerHTML = `
                            <div class="profile-header">
                                <span class="profile-id">ID: ${chat.profile_id}</span>
                                <span class="profile-name">${chat.profile_name}</span>
                            </div>
                            <p><strong>Created:</strong> ${new Date(chat.created_at).toLocaleString()}</p>
                            <button class="btn btn-primary" onclick="openChat(${chat.profile_id})">
                                Open Chat
                            </button>
                        `;
                        list.appendChild(chatDiv);
                    });
                } catch (error) {
                    console.error('Error loading chats:', error);
                }
            }

            // Открытие чата
            async function openChat(profileId) {
                try {
                    const response = await fetch(`/api/admin/chats/${profileId}/messages`);
                    const messages = await response.json();

                    const list = document.getElementById('chats-list');

                    let messagesHtml = '';
                    messages.messages.forEach(msg => {
                        if (msg.is_system) {
                            // Системное сообщение
                            messagesHtml += `
                                <div class="system-message">
                                    <div class="system-bubble">${msg.text}</div>
                                </div>
                            `;
                        } else if (msg.file_url) {
                            // Сообщение с файлом
                            if (msg.file_type === 'image') {
                                messagesHtml += `
                                    <div class="chat-message ${msg.is_from_user ? 'user-message' : 'admin-message'}">
                                        <div class="message-sender">
                                            ${msg.is_from_user ? 'User' : 'Admin'}:
                                        </div>
                                        <div class="chat-attachment">
                                            <img src="http://localhost:8002${msg.file_url}" alt="Image" class="attachment-preview">
                                            <div>
                                                <div>${msg.text || ''}</div>
                                            </div>
                                        </div>
                                        <small style="color: #ff6b9d; font-size: 12px;">
                                            ${new Date(msg.created_at).toLocaleString()}
                                        </small>
                                    </div>
                                `;
                            } else if (msg.file_type === 'video') {
                                messagesHtml += `
                                    <div class="chat-message ${msg.is_from_user ? 'user-message' : 'admin-message'}">
                                        <div class="message-sender">
                                            ${msg.is_from_user ? 'User' : 'Admin'}:
                                        </div>
                                        <div class="chat-attachment">
                                            <video controls class="attachment-preview">
                                                <source src="http://localhost:8002${msg.file_url}" type="video/mp4">
                                                Your browser does not support video.
                                            </video>
                                            <div>
                                                <div>${msg.text || ''}</div>
                                            </div>
                                        </div>
                                        <small style="color: #ff6b9d; font-size: 12px;">
                                            ${new Date(msg.created_at).toLocaleString()}
                                        </small>
                                    </div>
                                `;
                            } else {
                                messagesHtml += `
                                    <div class="chat-message ${msg.is_from_user ? 'user-message' : 'admin-message'}">
                                        <div class="message-sender">
                                            ${msg.is_from_user ? 'User' : 'Admin'}:
                                        </div>
                                        <div class="file-message">
                                            <strong>File: ${msg.file_name}</strong>
                                            <div>${msg.text || ''}</div>
                                            <a href="http://localhost:8002${msg.file_url}" target="_blank" style="color: #ff6b9d;">Download file</a>
                                        </div>
                                        <small style="color: #ff6b9d; font-size: 12px;">
                                            ${new Date(msg.created_at).toLocaleString()}
                                        </small>
                                    </div>
                                `;
                            }
                        } else {
                            // Текстовое сообщение
                            messagesHtml += `
                                <div class="chat-message ${msg.is_from_user ? 'user-message' : 'admin-message'}">
                                    <div class="message-sender">
                                        ${msg.is_from_user ? 'User' : 'Admin'}:
                                    </div>
                                    <div>${msg.text}</div>
                                    <small style="color: #ff6b9d; font-size: 12px;">
                                        ${new Date(msg.created_at).toLocaleString()}
                                    </small>
                                </div>
                            `;
                        }
                    });

                    list.innerHTML = `
                        <button class="back-btn" onclick="loadChats()">Back to chats</button>
                        <div class="profile-card">
                            <h3>Chat</h3>
                            <div style="margin: 15px 0;">
                                <button class="btn btn-system" onclick="sendSystemMessage(${profileId})">
                                    Send Transaction Success Message
                                </button>
                            </div>
                            <div id="chat-messages" style="max-height: 500px; overflow-y: auto; margin: 20px 0;">
                                ${messagesHtml}
                            </div>
                            <div>
                                <h4>Reply:</h4>
                                <div class="chat-file-upload">
                                    <input type="file" id="admin-chat-file" accept="image/*,video/*,.pdf,.doc,.docx" multiple style="display: none;">
                                    <button type="button" class="btn btn-primary" onclick="document.getElementById('admin-chat-file').click()">
                                        Attach Files
                                    </button>
                                    <div class="chat-file-list" id="chat-file-list"></div>
                                </div>
                                <textarea id="reply-text" rows="3" style="width: 100%; margin: 15px 0; padding: 12px; background: rgba(255, 107, 157, 0.1); color: white; border: 1px solid #ff6b9d; border-radius: 8px;" placeholder="Type your message..."></textarea>
                                <button class="btn btn-primary" onclick="sendAdminReply(${profileId})">
                                    Send Reply
                                </button>
                            </div>
                        </div>
                    `;

                    // Настройка загрузки файлов для чата
                    setupChatFileUpload();

                    // Прокрутка вниз
                    const chatMessages = document.getElementById('chat-messages');
                    if (chatMessages) {
                        chatMessages.scrollTop = chatMessages.scrollHeight;
                    }
                } catch (error) {
                    console.error('Error opening chat:', error);
                    alert('Error opening chat: ' + error.message);
                }
            }

            // Отправка системного сообщения
            async function sendSystemMessage(profileId) {
                if (!confirm('Send transaction success message?')) return;

                try {
                    const response = await fetch(`/api/admin/chats/${profileId}/system-message`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            text: 'Transaction successful, your booking has been confirmed'
                        })
                    });

                    if (response.ok) {
                        openChat(profileId); // Перезагружаем чат
                    } else {
                        alert('Error sending system message');
                    }
                } catch (error) {
                    console.error('Error sending system message:', error);
                    alert('Error sending system message');
                }
            }

            // Настройка загрузки файлов для чата
            function setupChatFileUpload() {
                const fileInput = document.getElementById('admin-chat-file');
                const fileList = document.getElementById('chat-file-list');
                let selectedFiles = [];

                fileInput.addEventListener('change', function(e) {
                    const files = Array.from(e.target.files);
                    selectedFiles = [...selectedFiles, ...files];
                    updateChatFileList();
                });

                function updateChatFileList() {
                    fileList.innerHTML = '';
                    selectedFiles.forEach((file, index) => {
                        const fileItem = document.createElement('div');
                        fileItem.className = 'file-item';
                        fileItem.innerHTML = `
                            <span>${file.name}</span>
                            <span class="remove-file" onclick="removeChatFile(${index})">×</span>
                        `;
                        fileList.appendChild(fileItem);
                    });
                }

                window.removeChatFile = function(index) {
                    selectedFiles.splice(index, 1);
                    updateChatFileList();
                    fileInput.value = '';
                };

                window.getSelectedChatFiles = function() {
                    return selectedFiles;
                };

                window.clearChatFiles = function() {
                    selectedFiles = [];
                    updateChatFileList();
                    fileInput.value = '';
                };
            }

            // Отправка ответа с файлами - ИСПРАВЛЕННАЯ ВЕРСИЯ
            async function sendAdminReply(profileId) {
                const text = document.getElementById('reply-text').value.trim();
                const files = window.getSelectedChatFiles();

                console.log('Sending reply:', { text, files: files.length });

                if (!text && files.length === 0) {
                    alert('Please enter message text or attach files');
                    return;
                }

                try {
                    const formData = new FormData();
                    if (text) {
                        formData.append('text', text);
                    }

                    // Добавляем все файлы
                    files.forEach(file => {
                        formData.append('files', file);
                    });

                    console.log('FormData entries:', Array.from(formData.entries()));

                    const response = await fetch(`/api/admin/chats/${profileId}/reply`, {
                        method: 'POST',
                        body: formData
                    });

                    if (response.ok) {
                        document.getElementById('reply-text').value = '';
                        window.clearChatFiles();
                        openChat(profileId); // Перезагружаем чат
                    } else {
                        const errorData = await response.json();
                        console.error('Server error:', errorData);
                        alert('Error sending message: ' + (errorData.detail || 'Unknown error'));
                    }

                } catch (error) {
                    console.error('Error sending reply:', error);
                    alert('Error sending message: ' + error.message);
                }
            }

            // Управление комментариями
            async function loadCommentsAdmin() {
                try {
                    const response = await fetch('/api/admin/comments');
                    const data = await response.json();
                    const list = document.getElementById('comments-list-admin');
                    list.innerHTML = '';

                    if (data.comments.length === 0) {
                        list.innerHTML = '<p>No comments yet</p>';
                        return;
                    }

                    data.comments.forEach(comment => {
                        const commentDiv = document.createElement('div');
                        commentDiv.className = 'comment-management-item';
                        commentDiv.innerHTML = `
                            <div class="comment-management-header">
                                <span class="comment-profile">Profile ID: ${comment.profile_id}</span>
                                <span class="comment-date">${new Date(comment.created_at).toLocaleString()}</span>
                            </div>
                            <div class="comment-header">
                                <span class="comment-author">${comment.user_name}</span>
                            </div>
                            <div class="comment-text">${comment.text}</div>
                            <div class="comment-actions">
                                <button class="delete-comment" onclick="deleteComment(${comment.profile_id}, ${comment.id})">
                                    Delete Comment
                                </button>
                            </div>
                        `;
                        list.appendChild(commentDiv);
                    });

                    loadStats();
                } catch (error) {
                    console.error('Error loading comments:', error);
                }
            }

            // Удаление комментария
            async function deleteComment(profileId, commentId) {
                if (!confirm('Delete this comment?')) return;

                try {
                    const response = await fetch(`/api/profiles/${profileId}/comments/${commentId}`, {
                        method: 'DELETE'
                    });

                    if (response.ok) {
                        alert('Comment deleted!');
                        loadCommentsAdmin();
                    } else {
                        alert('Error deleting comment');
                    }
                } catch (error) {
                    console.error('Error deleting comment:', error);
                    alert('Error deleting comment');
                }
            }

            // Промокоды
            async function loadPromocodes() {
                try {
                    const response = await fetch('/api/admin/promocodes');
                    const data = await response.json();
                    const list = document.getElementById('promocodes-list');
                    list.innerHTML = '';

                    data.promocodes.forEach(promo => {
                        const promoDiv = document.createElement('div');
                        promoDiv.className = 'promocode-card';
                        promoDiv.innerHTML = `
                            <div class="promocode-header">
                                <span class="promocode-code">${promo.code}</span>
                                <span class="promocode-discount">${promo.discount}% OFF</span>
                            </div>
                            <p><strong>Created:</strong> ${new Date(promo.created_at).toLocaleString()}</p>
                            <p><strong>Status:</strong> 
                                <span class="promocode-status ${promo.is_active ? 'status-active' : 'status-inactive'}">
                                    ${promo.is_active ? 'ACTIVE' : 'INACTIVE'}
                                </span>
                            </p>
                            <p><strong>Used:</strong> ${promo.used_by ? promo.used_by.length : 0} times</p>
                            <div style="margin-top: 15px;">
                                <button class="btn btn-warning" onclick="togglePromocode(${promo.id}, ${!promo.is_active})">
                                    ${promo.is_active ? 'Deactivate' : 'Activate'}
                                </button>
                                <button class="btn btn-danger" onclick="deletePromocode(${promo.id})">
                                    Delete
                                </button>
                            </div>
                        `;
                        list.appendChild(promoDiv);
                    });

                    loadStats();
                } catch (error) {
                    console.error('Error loading promocodes:', error);
                }
            }

            async function createPromocode() {
                const code = document.getElementById('promocode-code').value.trim();
                const discount = parseInt(document.getElementById('promocode-discount').value);

                if (!code) {
                    alert('Please enter promocode');
                    return;
                }

                if (discount < 1 || discount > 100) {
                    alert('Discount must be between 1 and 100%');
                    return;
                }

                try {
                    const response = await fetch('/api/admin/promocodes', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            code: code,
                            discount: discount
                        })
                    });

                    if (response.ok) {
                        alert('Promocode created!');
                        document.getElementById('promocode-code').value = '';
                        loadPromocodes();
                    } else {
                        alert('Error creating promocode');
                    }
                } catch (error) {
                    console.error('Error creating promocode:', error);
                    alert('Error creating promocode');
                }
            }

            async function togglePromocode(promocodeId, active) {
                try {
                    await fetch(`/api/admin/promocodes/${promocodeId}/toggle`, {
                        method: 'POST'
                    });
                    loadPromocodes();
                } catch (error) {
                    console.error('Error toggling promocode:', error);
                    alert('Error updating promocode');
                }
            }

            async function deletePromocode(promocodeId) {
                if (!confirm('Delete promocode? This action cannot be undone!')) return;

                try {
                    const response = await fetch(`/api/admin/promocodes/${promocodeId}`, {method: 'DELETE'});
                    if (response.ok) {
                        alert('Promocode deleted!');
                        loadPromocodes();
                    } else {
                        alert('Error deleting promocode');
                    }
                } catch (error) {
                    console.error('Error deleting promocode:', error);
                    alert('Error deleting promocode');
                }
            }

            // Баннер
            async function loadBannerSettings() {
                try {
                    const response = await fetch('/api/admin/banner');
                    const banner = await response.json();

                    document.getElementById('banner-text').value = banner.text || '';
                    document.getElementById('banner-link').value = banner.link || '';
                    document.getElementById('banner-link-text').value = banner.link_text || '';
                    document.getElementById('banner-visible').checked = banner.visible !== false;

                    updateBannerPreview();
                } catch (error) {
                    console.error('Error loading banner settings:', error);
                }
            }

            function updateBannerPreview() {
                const text = document.getElementById('banner-text').value || 'Banner preview text';
                const link = document.getElementById('banner-link').value || '#';
                const linkText = document.getElementById('banner-link-text').value || 'Preview Link';

                document.getElementById('preview-text').textContent = text;
                document.getElementById('preview-link').textContent = linkText;
                document.getElementById('preview-link').href = link;
            }

            async function saveBannerSettings() {
                try {
                    const banner = {
                        text: document.getElementById('banner-text').value,
                        link: document.getElementById('banner-link').value,
                        link_text: document.getElementById('banner-link-text').value,
                        visible: document.getElementById('banner-visible').checked
                    };

                    const response = await fetch('/api/admin/banner', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(banner)
                    });

                    if (response.ok) {
                        alert('Banner settings saved!');
                        updateBannerPreview();
                    } else {
                        alert('Error saving banner settings');
                    }
                } catch (error) {
                    console.error('Error saving banner settings:', error);
                    alert('Error saving banner settings');
                }
            }

            // Загрузка фото для профиля
            document.getElementById('photo-upload').addEventListener('change', function(e) {
                const files = Array.from(e.target.files);
                const uploadedPhotosContainer = document.getElementById('uploaded-photos');

                files.forEach(file => {
                    if (file.type.startsWith('image/')) {
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            const photoData = e.target.result;
                            uploadedPhotoFiles.push(file);

                            const photoDiv = document.createElement('div');
                            photoDiv.className = 'uploaded-photo';
                            photoDiv.innerHTML = `
                                <img src="${photoData}" alt="Uploaded photo">
                                <button type="button" class="remove-photo" onclick="removeUploadedPhoto(${uploadedPhotoFiles.length - 1})">×</button>
                            `;
                            uploadedPhotosContainer.appendChild(photoDiv);
                        };
                        reader.readAsDataURL(file);
                    }
                });

                this.value = '';
            });

            // Загрузка фото для VIP профиля
            document.getElementById('vip-photo-upload').addEventListener('change', function(e) {
                const files = Array.from(e.target.files);
                const uploadedPhotosContainer = document.getElementById('vip-uploaded-photos');

                files.forEach(file => {
                    if (file.type.startsWith('image/')) {
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            const photoData = e.target.result;
                            uploadedVipPhotoFiles.push(file);

                            const photoDiv = document.createElement('div');
                            photoDiv.className = 'uploaded-photo';
                            photoDiv.innerHTML = `
                                <img src="${photoData}" alt="Uploaded photo">
                                <button type="button" class="remove-photo" onclick="removeVipUploadedPhoto(${uploadedVipPhotoFiles.length - 1})">×</button>
                            `;
                            uploadedPhotosContainer.appendChild(photoDiv);
                        };
                        reader.readAsDataURL(file);
                    }
                });

                this.value = '';
            });

            // Удаление загруженного фото
            window.removeUploadedPhoto = function(index) {
                uploadedPhotoFiles.splice(index, 1);
                updateUploadedPhotosDisplay();
            };

            // Удаление загруженного VIP фото
            window.removeVipUploadedPhoto = function(index) {
                uploadedVipPhotoFiles.splice(index, 1);
                updateVipUploadedPhotosDisplay();
            };

            // Обновление отображения загруженных фото
            function updateUploadedPhotosDisplay() {
                const uploadedPhotosContainer = document.getElementById('uploaded-photos');
                uploadedPhotosContainer.innerHTML = '';

                uploadedPhotoFiles.forEach((file, index) => {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const photoDiv = document.createElement('div');
                        photoDiv.className = 'uploaded-photo';
                        photoDiv.innerHTML = `
                            <img src="${e.target.result}" alt="Uploaded photo">
                            <button type="button" class="remove-photo" onclick="removeUploadedPhoto(${index})">×</button>
                        `;
                        uploadedPhotosContainer.appendChild(photoDiv);
                    };
                    reader.readAsDataURL(file);
                });
            }

            // Обновление отображения загруженных VIP фото
            function updateVipUploadedPhotosDisplay() {
                const uploadedPhotosContainer = document.getElementById('vip-uploaded-photos');
                uploadedPhotosContainer.innerHTML = '';

                uploadedVipPhotoFiles.forEach((file, index) => {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const photoDiv = document.createElement('div');
                        photoDiv.className = 'uploaded-photo';
                        photoDiv.innerHTML = `
                            <img src="${e.target.result}" alt="Uploaded photo">
                            <button type="button" class="remove-photo" onclick="removeVipUploadedPhoto(${index})">×</button>
                        `;
                        uploadedPhotosContainer.appendChild(photoDiv);
                    };
                    reader.readAsDataURL(file);
                });
            }

            // Обработчик формы добавления анкеты
            document.getElementById('add-profile-form').addEventListener('submit', async function(e) {
                e.preventDefault();

                if (uploadedPhotoFiles.length === 0) {
                    alert('Please upload at least one photo');
                    return;
                }

                const travelCities = document.getElementById('travel-cities').value
                    .split(',')
                    .map(city => city.trim())
                    .filter(city => city);

                // Создаем FormData для отправки файлов
                const formData = new FormData();
                formData.append('name', document.getElementById('name').value);
                formData.append('age', document.getElementById('age').value);
                formData.append('gender', document.getElementById('gender').value);
                formData.append('nationality', document.getElementById('nationality').value);
                formData.append('city', document.getElementById('city').value);
                formData.append('travel_cities', JSON.stringify(travelCities));
                formData.append('description', document.getElementById('description').value);
                formData.append('height', document.getElementById('height').value);
                formData.append('weight', document.getElementById('weight').value);
                formData.append('chest', document.getElementById('chest').value);

                // Добавляем фото
                uploadedPhotoFiles.forEach(file => {
                    formData.append('photos', file);
                });

                try {
                    const response = await fetch('/api/admin/profiles', {
                        method: 'POST',
                        body: formData
                    });

                    if (response.ok) {
                        alert('Profile added successfully!');
                        this.reset();
                        uploadedPhotoFiles = [];
                        updateUploadedPhotosDisplay();
                        showTab('profiles');
                    } else {
                        const errorData = await response.json();
                        alert('Error adding profile: ' + (errorData.detail || 'Unknown error'));
                    }
                } catch (error) {
                    console.error('Error adding profile:', error);
                    alert('Error adding profile: ' + error.message);
                }
            });

            // Обработчик формы добавления VIP анкеты
            document.getElementById('add-vip-profile-form').addEventListener('submit', async function(e) {
                e.preventDefault();

                if (uploadedVipPhotoFiles.length === 0) {
                    alert('Please upload at least one photo');
                    return;
                }

                // Создаем FormData для отправки файлов
                const formData = new FormData();
                formData.append('name', document.getElementById('vip-name').value);
                formData.append('age', document.getElementById('vip-age').value);
                formData.append('gender', document.getElementById('vip-gender').value);
                formData.append('city', document.getElementById('vip-city').value);

                // Добавляем фото
                uploadedVipPhotoFiles.forEach(file => {
                    formData.append('photos', file);
                });

                try {
                    const response = await fetch('/api/admin/vip-profiles', {
                        method: 'POST',
                        body: formData
                    });

                    if (response.ok) {
                        alert('VIP Profile added successfully!');
                        this.reset();
                        uploadedVipPhotoFiles = [];
                        updateVipUploadedPhotosDisplay();
                        showTab('vip-profiles');
                    } else {
                        const errorData = await response.json();
                        alert('Error adding VIP profile: ' + (errorData.detail || 'Unknown error'));
                    }
                } catch (error) {
                    console.error('Error adding VIP profile:', error);
                    alert('Error adding VIP profile: ' + error.message);
                }
            });

            // Загрузка крипто-кошельков
            async function loadCryptoWallets() {
                try {
                    const response = await fetch('/api/admin/crypto_wallets');
                    const wallets = await response.json();

                    document.getElementById('trc20-wallet').value = wallets.trc20 || '';
                    document.getElementById('erc20-wallet').value = wallets.erc20 || '';
                    document.getElementById('bnb-wallet').value = wallets.bnb || '';
                } catch (error) {
                    console.error('Error loading crypto wallets:', error);
                }
            }

            // Сохранение крипто-кошельков
            async function saveCryptoWallets() {
                try {
                    const wallets = {
                        trc20: document.getElementById('trc20-wallet').value,
                        erc20: document.getElementById('erc20-wallet').value,
                        bnb: document.getElementById('bnb-wallet').value
                    };

                    const response = await fetch('/api/admin/crypto_wallets', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(wallets)
                    });

                    if (response.ok) {
                        alert('Wallet addresses saved successfully!');
                    } else {
                        alert('Error saving wallet addresses');
                    }
                } catch (error) {
                    console.error('Error saving crypto wallets:', error);
                    alert('Error saving wallet addresses');
                }
            }

            // Загружаем анкеты при старте
            loadProfiles();

            // Обновляем превью баннера при изменении
            document.getElementById('banner-text').addEventListener('input', updateBannerPreview);
            document.getElementById('banner-link').addEventListener('input', updateBannerPreview);
            document.getElementById('banner-link-text').addEventListener('input', updateBannerPreview);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# API endpoints
@app.get("/api/stats")
async def get_stats():
    data = load_data()
    return {
        "profiles_count": len(data["profiles"]),
        "vip_profiles_count": len(data.get("vip_profiles", [])),
        "chats_count": len(data["chats"]),
        "messages_count": len(data["messages"]),
        "comments_count": len(data.get("comments", [])),
        "promocodes_count": len(data.get("promocodes", []))
    }


@app.get("/api/admin/profiles")
async def get_admin_profiles():
    data = load_data()
    return {"profiles": data["profiles"]}


@app.post("/api/admin/profiles")
async def create_profile(
        name: str = Form(...),
        age: int = Form(...),
        gender: str = Form(...),
        nationality: str = Form(...),
        city: str = Form(...),
        travel_cities: str = Form(...),
        description: str = Form(...),
        height: int = Form(...),
        weight: int = Form(...),
        chest: int = Form(...),
        photos: list[UploadFile] = File(...)
):
    data = load_data()

    # Находим максимальный ID
    max_id = max([p["id"] for p in data["profiles"]]) if data["profiles"] else 0

    # Сохраняем загруженные фото
    photo_urls = []
    for photo in photos:
        if photo.filename:
            photo_url = save_uploaded_file(photo)
            if photo_url:
                photo_urls.append(photo_url)

    if not photo_urls:
        raise HTTPException(status_code=400, detail="At least one photo is required")

    # Парсим travel cities
    try:
        travel_cities_list = json.loads(travel_cities)
    except:
        travel_cities_list = [city.strip() for city in travel_cities.split(',') if city.strip()]

    new_profile = {
        "id": max_id + 1,
        "name": name,
        "age": age,
        "gender": gender,
        "nationality": nationality,
        "city": city,
        "travel_cities": travel_cities_list,
        "description": description,
        "photos": photo_urls,
        "height": height,
        "weight": weight,
        "chest": chest,
        "visible": True,
        "created_at": datetime.now().isoformat()
    }

    data["profiles"].append(new_profile)
    save_data(data)
    return {"status": "created", "profile": new_profile}


@app.post("/api/admin/profiles/{profile_id}/toggle")
async def toggle_profile(profile_id: int, visible_data: dict):
    data = load_data()
    profile = next((p for p in data["profiles"] if p["id"] == profile_id), None)
    if profile:
        profile["visible"] = visible_data["visible"]
        save_data(data)
    return {"status": "updated"}


@app.delete("/api/admin/profiles/{profile_id}")
async def delete_profile(profile_id: int):
    data = load_data()

    # Удаляем анкету
    data["profiles"] = [p for p in data["profiles"] if p["id"] != profile_id]

    # Находим чаты связанные с этой анкетой
    profile_chats = [c for c in data["chats"] if c["profile_id"] == profile_id]
    chat_ids = [c["id"] for c in profile_chats]

    # Удаляем чаты
    data["chats"] = [c for c in data["chats"] if c["profile_id"] != profile_id]

    # Удаляем сообщения из этих чатов
    data["messages"] = [m for m in data["messages"] if m["chat_id"] not in chat_ids]

    # Удаляем комментарии к этой анкете
    data["comments"] = [c for c in data.get("comments", []) if c["profile_id"] != profile_id]

    save_data(data)
    return {"status": "deleted"}


@app.get("/api/admin/chats")
async def get_admin_chats():
    data = load_data()
    return {"chats": data["chats"]}


@app.get("/api/admin/chats/{profile_id}/messages")
async def get_chat_messages_admin(profile_id: int):
    data = load_data()
    chat = next((c for c in data["chats"] if c["profile_id"] == profile_id), None)
    if not chat:
        return {"messages": []}
    messages = [m for m in data["messages"] if m["chat_id"] == chat["id"]]
    return {"messages": messages}


@app.post("/api/admin/chats/{profile_id}/reply")
async def send_admin_reply(
        profile_id: int,
        request: Request
):
    data = load_data()

    logger.info(f"📨 Sending reply to profile {profile_id}")

    # Находим профиль для имени
    profile = next((p for p in data["profiles"] if p["id"] == profile_id), None)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    chat = next((c for c in data["chats"] if c["profile_id"] == profile_id), None)
    if not chat:
        chat = {
            "id": len(data["chats"]) + 1,
            "profile_id": profile_id,
            "profile_name": profile["name"],
            "created_at": datetime.now().isoformat()
        }
        data["chats"].append(chat)

    try:
        # Получаем форму с файлами и текстом
        form = await request.form()
        text = form.get("text", "").strip()
        files = form.getlist("files")

        logger.info(f"📝 Text: '{text}'")
        logger.info(f"📎 Files count: {len(files)}")

        has_files = False
        has_text = bool(text)

        # Обрабатываем файлы
        if files and any(hasattr(f, 'filename') and f.filename for f in files):
            for file in files:
                if hasattr(file, 'filename') and file.filename:
                    file_url = save_uploaded_file(file)
                    if file_url:
                        file_type = get_file_type(file.filename)

                        message_data = {
                            "id": len(data["messages"]) + 1,
                            "chat_id": chat["id"],
                            "file_url": file_url,
                            "file_type": file_type,
                            "file_name": file.filename,
                            "text": text or "",  # Убираем автоматический текст
                            "is_from_user": False,
                            "created_at": datetime.now().isoformat()
                        }
                        data["messages"].append(message_data)
                        has_files = True
                        logger.info(f"✅ File message added: {file.filename}")

        # Если только текст (без файлов)
        if not has_files and has_text:
            message_data = {
                "id": len(data["messages"]) + 1,
                "chat_id": chat["id"],
                "text": text,
                "is_from_user": False,
                "created_at": datetime.now().isoformat()
            }
            data["messages"].append(message_data)
            logger.info("✅ Text message added")

        # Если ничего не отправлено
        if not has_files and not has_text:
            raise HTTPException(status_code=400, detail="Text or files is required")

        save_data(data)
        logger.info("💾 Data saved successfully")
        return {"status": "sent"}

    except Exception as e:
        logger.error(f"❌ Error sending reply: {e}")
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")


@app.post("/api/admin/chats/{profile_id}/system-message")
async def send_system_message(profile_id: int, message_data: dict):
    """Отправка системного сообщения"""
    data = load_data()

    # Находим профиль для имени
    profile = next((p for p in data["profiles"] if p["id"] == profile_id), None)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    chat = next((c for c in data["chats"] if c["profile_id"] == profile_id), None)
    if not chat:
        chat = {
            "id": len(data["chats"]) + 1,
            "profile_id": profile_id,
            "profile_name": profile["name"],
            "created_at": datetime.now().isoformat()
        }
        data["chats"].append(chat)

    # Создаем системное сообщение
    system_message = {
        "id": len(data["messages"]) + 1,
        "chat_id": chat["id"],
        "text": message_data["text"],
        "is_system": True,
        "created_at": datetime.now().isoformat()
    }

    data["messages"].append(system_message)
    save_data(data)

    return {"status": "sent", "message_id": system_message["id"]}


# Комментарии API для админки
@app.get("/api/admin/comments")
async def get_admin_comments():
    data = load_data()
    return {"comments": data.get("comments", [])}


# Промокоды API
@app.get("/api/admin/promocodes")
async def get_admin_promocodes():
    data = load_data()
    return {"promocodes": data.get("promocodes", [])}


@app.post("/api/admin/promocodes")
async def create_admin_promocode(promocode: dict):
    data = load_data()

    # Проверяем, существует ли уже такой промокод
    existing = next((p for p in data["promocodes"] if p["code"] == promocode["code"].upper()), None)
    if existing:
        raise HTTPException(status_code=400, detail="Promocode already exists")

    new_promocode = {
        "id": len(data["promocodes"]) + 1,
        "code": promocode["code"].upper(),
        "discount": promocode["discount"],
        "is_active": True,
        "used_by": [],
        "created_at": datetime.now().isoformat()
    }

    data["promocodes"].append(new_promocode)
    save_data(data)
    return {"status": "created", "promocode": new_promocode}


@app.post("/api/admin/promocodes/{promocode_id}/toggle")
async def toggle_admin_promocode(promocode_id: int):
    data = load_data()
    promocode = next((p for p in data["promocodes"] if p["id"] == promocode_id), None)
    if promocode:
        promocode["is_active"] = not promocode["is_active"]
        save_data(data)
    return {"status": "updated"}


@app.delete("/api/admin/promocodes/{promocode_id}")
async def delete_admin_promocode(promocode_id: int):
    data = load_data()
    data["promocodes"] = [p for p in data["promocodes"] if p["id"] != promocode_id]
    save_data(data)
    return {"status": "deleted"}


# Баннер API
@app.get("/api/admin/banner")
async def get_admin_banner():
    data = load_data()
    return data.get("settings", {}).get("banner", {})


@app.post("/api/admin/banner")
async def update_admin_banner(banner: dict):
    data = load_data()
    if "settings" not in data:
        data["settings"] = {}
    data["settings"]["banner"] = banner
    save_data(data)
    return {"status": "updated"}


@app.get("/api/admin/crypto_wallets")
async def get_admin_crypto_wallets():
    data = load_data()
    return data.get("settings", {}).get("crypto_wallets", {})


@app.post("/api/admin/crypto_wallets")
async def update_admin_crypto_wallets(wallets: dict):
    data = load_data()
    if "settings" not in data:
        data["settings"] = {}
    data["settings"]["crypto_wallets"] = wallets
    save_data(data)
    return {"status": "updated"}


if __name__ == "__main__":
    print("🚀 Admin panel Muji запущена: http://localhost:8002")
    print("🎨 Исправления: VIP анкеты, переименование, улучшенные кнопки!")
    uvicorn.run(app, host="0.0.0.0", port=8002, access_log=False)
