from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import qrcodegen
import os

app = Flask(__name__)
CORS(app)

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

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)