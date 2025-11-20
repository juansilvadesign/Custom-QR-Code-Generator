from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import qrcodegen
import os

app = Flask(__name__)
CORS(app)

# Complete HTML with embedded JavaScript
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Custom QR Code Generator</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
    <div class="max-w-6xl mx-auto py-8 px-4">
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-gray-900 mb-2">Custom QR Code Generator</h1>
            <p class="text-gray-600">Create beautiful, customizable QR codes for any content</p>
        </div>

        <div class="grid md:grid-cols-2 gap-6">
            <!-- Left Panel - Configuration -->
            <div class="bg-white rounded-xl shadow-lg p-6">
                <h2 class="text-xl font-semibold mb-4">Configuration</h2>
                
                <!-- Content Type Selector -->
                <div class="mb-6">
                    <label class="block text-sm font-medium text-gray-700 mb-3">Content Type</label>
                    <div class="grid grid-cols-3 gap-2">
                        <button onclick="setContentType('text')" id="btn-text" class="content-type-btn border-blue-500 bg-blue-50 text-blue-700">
                            <svg class="w-6 h-6 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                            <span class="text-xs mt-1">Text</span>
                        </button>
                        <button onclick="setContentType('url')" id="btn-url" class="content-type-btn">
                            <svg class="w-6 h-6 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path></svg>
                            <span class="text-xs mt-1">URL</span>
                        </button>
                        <button onclick="setContentType('email')" id="btn-email" class="content-type-btn">
                            <svg class="w-6 h-6 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
                            <span class="text-xs mt-1">Email</span>
                        </button>
                        <button onclick="setContentType('phone')" id="btn-phone" class="content-type-btn">
                            <svg class="w-6 h-6 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path></svg>
                            <span class="text-xs mt-1">Phone</span>
                        </button>
                        <button onclick="setContentType('sms')" id="btn-sms" class="content-type-btn">
                            <svg class="w-6 h-6 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>
                            <span class="text-xs mt-1">SMS</span>
                        </button>
                        <button onclick="setContentType('wifi')" id="btn-wifi" class="content-type-btn">
                            <svg class="w-6 h-6 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0"></path></svg>
                            <span class="text-xs mt-1">WiFi</span>
                        </button>
                    </div>
                </div>

                <!-- Content Fields -->
                <div id="content-fields" class="mb-6"></div>

                <!-- Color Options -->
                <div class="grid grid-cols-2 gap-4 mb-6">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Background</label>
                        <div class="flex gap-2">
                            <input type="color" id="bgColor" value="#FFFFFF" class="w-12 h-10 rounded cursor-pointer">
                            <input type="text" id="bgColorText" value="#FFFFFF" class="flex-1 px-3 py-2 border border-gray-300 rounded-lg">
                        </div>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Foreground</label>
                        <div class="flex gap-2">
                            <input type="color" id="fgColor" value="#000000" class="w-12 h-10 rounded cursor-pointer">
                            <input type="text" id="fgColorText" value="#000000" class="flex-1 px-3 py-2 border border-gray-300 rounded-lg">
                        </div>
                    </div>
                </div>

                <!-- Error Correction Level -->
                <div class="mb-6">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Error Correction</label>
                    <select id="errorLevel" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                        <option value="L">Low (~7%)</option>
                        <option value="M" selected>Medium (~15%)</option>
                        <option value="Q">Quartile (~25%)</option>
                        <option value="H">High (~30%)</option>
                    </select>
                </div>

                <!-- Generate Button -->
                <button onclick="generateQR()" id="generateBtn" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition-colors">
                    Generate QR Code
                </button>
            </div>

            <!-- Right Panel - Preview -->
            <div class="bg-white rounded-xl shadow-lg p-6">
                <h2 class="text-xl font-semibold mb-4">Preview</h2>
                <div id="preview" class="flex items-center justify-center min-h-[400px] bg-gray-50 rounded-lg">
                    <p class="text-gray-400">Your QR code will appear here</p>
                </div>
            </div>
        </div>
    </div>

    <style>
        .content-type-btn {
            @apply flex flex-col items-center justify-center p-3 rounded-lg border-2 transition-all border-gray-200 hover:border-gray-300;
        }
        .content-type-btn.active {
            @apply border-blue-500 bg-blue-50 text-blue-700;
        }
    </style>

    <script>
        let currentType = 'text';

        // Sync color inputs
        document.getElementById('bgColor').addEventListener('input', (e) => {
            document.getElementById('bgColorText').value = e.target.value;
        });
        document.getElementById('bgColorText').addEventListener('input', (e) => {
            document.getElementById('bgColor').value = e.target.value;
        });
        document.getElementById('fgColor').addEventListener('input', (e) => {
            document.getElementById('fgColorText').value = e.target.value;
        });
        document.getElementById('fgColorText').addEventListener('input', (e) => {
            document.getElementById('fgColor').value = e.target.value;
        });

        function setContentType(type) {
            currentType = type;
            // Update button styles
            document.querySelectorAll('.content-type-btn').forEach(btn => {
                btn.classList.remove('active', 'border-blue-500', 'bg-blue-50', 'text-blue-700');
                btn.classList.add('border-gray-200');
            });
            document.getElementById('btn-' + type).classList.add('active', 'border-blue-500', 'bg-blue-50', 'text-blue-700');
            
            // Render appropriate fields
            renderFields(type);
        }

        function renderFields(type) {
            const container = document.getElementById('content-fields');
            
            const templates = {
                text: `<label class="block text-sm font-medium text-gray-700 mb-2">Text Content</label>
                       <textarea id="qrContent" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" rows="4" placeholder="Enter your text here..."></textarea>`,
                
                url: `<label class="block text-sm font-medium text-gray-700 mb-2">Website URL</label>
                      <input type="text" id="qrContent" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="example.com or https://example.com">`,
                
                email: `<div class="space-y-3">
                          <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
                            <input type="email" id="emailAddress" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="user@example.com">
                          </div>
                          <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Subject (Optional)</label>
                            <input type="text" id="emailSubject" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="Email subject">
                          </div>
                          <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Body (Optional)</label>
                            <textarea id="emailBody" class="w-full px-3 py-2 border border-gray-300 rounded-lg" rows="3" placeholder="Email body"></textarea>
                          </div>
                        </div>`,
                
                phone: `<label class="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
                        <input type="tel" id="phoneNumber" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="+1234567890">`,
                
                sms: `<div class="space-y-3">
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
                          <input type="tel" id="smsPhone" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="+1234567890">
                        </div>
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-2">Message (Optional)</label>
                          <textarea id="smsBody" class="w-full px-3 py-2 border border-gray-300 rounded-lg" rows="3" placeholder="Pre-filled SMS message"></textarea>
                        </div>
                      </div>`,
                
                wifi: `<div class="space-y-3">
                         <div>
                           <label class="block text-sm font-medium text-gray-700 mb-2">Network Name (SSID)</label>
                           <input type="text" id="wifiSSID" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="MyWiFi">
                         </div>
                         <div>
                           <label class="block text-sm font-medium text-gray-700 mb-2">Password</label>
                           <input type="text" id="wifiPassword" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="password123">
                         </div>
                         <div>
                           <label class="block text-sm font-medium text-gray-700 mb-2">Security Type</label>
                           <select id="wifiSecurity" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                             <option value="WPA">WPA/WPA2</option>
                             <option value="WEP">WEP</option>
                             <option value="nopass">None</option>
                           </select>
                         </div>
                         <div class="flex items-center">
                           <input type="checkbox" id="wifiHidden" class="mr-2">
                           <label class="text-sm text-gray-700">Hidden Network</label>
                         </div>
                       </div>`
            };
            
            container.innerHTML = templates[type];
        }

        function getContent() {
            switch(currentType) {
                case 'text':
                    return document.getElementById('qrContent').value;
                case 'url':
                    const url = document.getElementById('qrContent').value;
                    return url.startsWith('http') ? url : 'https://' + url;
                case 'email':
                    const email = document.getElementById('emailAddress').value;
                    const subject = document.getElementById('emailSubject').value;
                    const body = document.getElementById('emailBody').value;
                    let mailto = 'mailto:' + email;
                    const params = new URLSearchParams();
                    if (subject) params.append('subject', subject);
                    if (body) params.append('body', body);
                    if (params.toString()) mailto += '?' + params.toString();
                    return mailto;
                case 'phone':
                    return 'tel:' + document.getElementById('phoneNumber').value;
                case 'sms':
                    const smsPhone = document.getElementById('smsPhone').value;
                    const smsBody = document.getElementById('smsBody').value;
                    let sms = 'sms:' + smsPhone;
                    if (smsBody) sms += '?body=' + encodeURIComponent(smsBody);
                    return sms;
                case 'wifi':
                    const ssid = document.getElementById('wifiSSID').value;
                    const password = document.getElementById('wifiPassword').value;
                    const security = document.getElementById('wifiSecurity').value;
                    const hidden = document.getElementById('wifiHidden').checked;
                    return `WIFI:T:${security};S:${ssid};P:${password};H:${hidden};`;
                default:
                    return '';
            }
        }

        async function generateQR() {
            const btn = document.getElementById('generateBtn');
            btn.disabled = true;
            btn.textContent = 'Generating...';
            
            const content = getContent();
            if (!content) {
                alert('Please enter content for the QR code');
                btn.disabled = false;
                btn.textContent = 'Generate QR Code';
                return;
            }
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        content: content,
                        backgroundColor: document.getElementById('bgColor').value,
                        foregroundColor: document.getElementById('fgColor').value,
                        errorLevel: document.getElementById('errorLevel').value
                    })
                });
                
                const data = await response.json();
                
                if (data.svg) {
                    document.getElementById('preview').innerHTML = `
                        <div class="text-center">
                            ${data.svg}
                            <button onclick="downloadSVG()" class="mt-4 inline-flex items-center gap-2 px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                                Download SVG
                            </button>
                        </div>
                    `;
                    window.currentSVG = data.svg;
                } else {
                    alert('Error: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                alert('Failed to generate QR code: ' + error);
            } finally {
                btn.disabled = false;
                btn.textContent = 'Generate QR Code';
            }
        }

        function downloadSVG() {
            const blob = new Blob([window.currentSVG], { type: 'image/svg+xml' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'qrcode-' + Date.now() + '.svg';
            a.click();
            URL.revokeObjectURL(url);
        }

        // Initialize with text type
        renderFields('text');
    </script>
</body>
</html>
'''

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def to_svg_string(qr, border, background_color, foreground_color):
    """Convert QR code to SVG string with custom colors"""
    if border < 0:
        raise ValueError("Border must be non-negative")
    if qr.get_size() + border * 2 > 10000:
        raise ValueError("Image too large")
    
    bg_r, bg_g, bg_b = hex_to_rgb(background_color)
    fg_r, fg_g, fg_b = hex_to_rgb(foreground_color)
    
    parts = []
    parts.append('<?xml version="1.0" encoding="UTF-8"?>')
    parts.append('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">')
    
    dimension = qr.get_size() + border * 2
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 {dimension} {dimension}" stroke="none">')
    parts.append(f'<rect width="100%" height="100%" fill="rgb({bg_r},{bg_g},{bg_b})"/>')
    parts.append(f'<path d="')
    
    for y in range(qr.get_size()):
        for x in range(qr.get_size()):
            if qr.get_module(x, y):
                if x != 0 or y != 0:
                    parts.append(" ")
                parts.append(f"M{x + border},{y + border}h1v1h-1z")
    
    parts.append(f'" fill="rgb({fg_r},{fg_g},{fg_b})"/>')
    parts.append('</svg>')
    
    return "".join(parts)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/generate', methods=['POST'])
def generate_qr():
    try:
        data = request.json
        content = data.get('content', '')
        background_color = data.get('backgroundColor', '#FFFFFF')
        foreground_color = data.get('foregroundColor', '#000000')
        error_level = data.get('errorLevel', 'M')
        
        # Map error correction levels
        ecc_map = {
            'L': qrcodegen.QrCode.Ecc.LOW,
            'M': qrcodegen.QrCode.Ecc.MEDIUM,
            'Q': qrcodegen.QrCode.Ecc.QUARTILE,
            'H': qrcodegen.QrCode.Ecc.HIGH
        }
        
        ecc = ecc_map.get(error_level, qrcodegen.QrCode.Ecc.MEDIUM)
        
        # Generate QR code
        qr = qrcodegen.QrCode.encode_text(content, ecc)
        
        # Convert to SVG
        svg = to_svg_string(qr, 4, background_color, foreground_color)
        
        return jsonify({'svg': svg})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)