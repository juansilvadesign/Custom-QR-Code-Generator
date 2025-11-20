import React, { useState } from 'react';
import { Download, Wifi, Mail, Phone, MessageSquare, Link2, Type } from 'lucide-react';

export default function QRCodeGenerator() {
  const [contentType, setContentType] = useState('text');
  const [qrData, setQrData] = useState('');
  const [backgroundColor, setBackgroundColor] = useState('#FFFFFF');
  const [foregroundColor, setForegroundColor] = useState('#000000');
  const [errorLevel, setErrorLevel] = useState('M');
  const [qrCodeSVG, setQrCodeSVG] = useState('');
  const [loading, setLoading] = useState(false);

  // WiFi specific fields
  const [wifiSSID, setWifiSSID] = useState('');
  const [wifiPassword, setWifiPassword] = useState('');
  const [wifiSecurity, setWifiSecurity] = useState('WPA');
  const [wifiHidden, setWifiHidden] = useState(false);

  // Email specific fields
  const [emailAddress, setEmailAddress] = useState('');
  const [emailSubject, setEmailSubject] = useState('');
  const [emailBody, setEmailBody] = useState('');

  // Phone/SMS specific fields
  const [phoneNumber, setPhoneNumber] = useState('');
  const [smsBody, setSmsBody] = useState('');

  const generateQRCode = async () => {
    setLoading(true);
    
    let content = '';
    
    switch(contentType) {
      case 'text':
        content = qrData;
        break;
      case 'url':
        content = qrData.startsWith('http') ? qrData : `https://${qrData}`;
        break;
      case 'email':
        content = `mailto:${emailAddress}`;
        if (emailSubject || emailBody) {
          const params = new URLSearchParams();
          if (emailSubject) params.append('subject', emailSubject);
          if (emailBody) params.append('body', emailBody);
          content += `?${params.toString()}`;
        }
        break;
      case 'phone':
        content = `tel:${phoneNumber}`;
        break;
      case 'sms':
        content = `sms:${phoneNumber}`;
        if (smsBody) content += `?body=${encodeURIComponent(smsBody)}`;
        break;
      case 'wifi':
        content = `WIFI:T:${wifiSecurity};S:${wifiSSID};P:${wifiPassword};H:${wifiHidden};`;
        break;
      default:
        content = qrData;
    }

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content,
          backgroundColor,
          foregroundColor,
          errorLevel
        })
      });

      const data = await response.json();
      if (data.svg) {
        setQrCodeSVG(data.svg);
      }
    } catch (error) {
      console.error('Error generating QR code:', error);
      alert('Failed to generate QR code');
    } finally {
      setLoading(false);
    }
  };

  const downloadQRCode = () => {
    const blob = new Blob([qrCodeSVG], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `qrcode-${Date.now()}.svg`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const renderContentFields = () => {
    switch(contentType) {
      case 'text':
        return (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Text Content</label>
            <textarea
              value={qrData}
              onChange={(e) => setQrData(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows="4"
              placeholder="Enter your text here..."
            />
          </div>
        );
      
      case 'url':
        return (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Website URL</label>
            <input
              type="text"
              value={qrData}
              onChange={(e) => setQrData(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="example.com or https://example.com"
            />
          </div>
        );
      
      case 'email':
        return (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
              <input
                type="email"
                value={emailAddress}
                onChange={(e) => setEmailAddress(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="user@example.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Subject (Optional)</label>
              <input
                type="text"
                value={emailSubject}
                onChange={(e) => setEmailSubject(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Email subject"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Body (Optional)</label>
              <textarea
                value={emailBody}
                onChange={(e) => setEmailBody(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows="3"
                placeholder="Email body"
              />
            </div>
          </div>
        );
      
      case 'phone':
        return (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
            <input
              type="tel"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="+1234567890"
            />
          </div>
        );
      
      case 'sms':
        return (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
              <input
                type="tel"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="+1234567890"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Message (Optional)</label>
              <textarea
                value={smsBody}
                onChange={(e) => setSmsBody(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows="3"
                placeholder="Pre-filled SMS message"
              />
            </div>
          </div>
        );
      
      case 'wifi':
        return (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Network Name (SSID)</label>
              <input
                type="text"
                value={wifiSSID}
                onChange={(e) => setWifiSSID(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="MyWiFi"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
              <input
                type="text"
                value={wifiPassword}
                onChange={(e) => setWifiPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="password123"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Security Type</label>
              <select
                value={wifiSecurity}
                onChange={(e) => setWifiSecurity(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="WPA">WPA/WPA2</option>
                <option value="WEP">WEP</option>
                <option value="nopass">None</option>
              </select>
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="hidden"
                checked={wifiHidden}
                onChange={(e) => setWifiHidden(e.target.checked)}
                className="mr-2"
              />
              <label htmlFor="hidden" className="text-sm text-gray-700">Hidden Network</label>
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Custom QR Code Generator</h1>
          <p className="text-gray-600">Create beautiful, customizable QR codes for any content</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Left Panel - Configuration */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Configuration</h2>
            
            {/* Content Type Selector */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">Content Type</label>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { type: 'text', icon: Type, label: 'Text' },
                  { type: 'url', icon: Link2, label: 'URL' },
                  { type: 'email', icon: Mail, label: 'Email' },
                  { type: 'phone', icon: Phone, label: 'Phone' },
                  { type: 'sms', icon: MessageSquare, label: 'SMS' },
                  { type: 'wifi', icon: Wifi, label: 'WiFi' }
                ].map(({ type, icon: Icon, label }) => (
                  <button
                    key={type}
                    onClick={() => setContentType(type)}
                    className={`flex flex-col items-center justify-center p-3 rounded-lg border-2 transition-all ${
                      contentType === type
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <Icon size={24} />
                    <span className="text-xs mt-1">{label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Content Fields */}
            <div className="mb-6">
              {renderContentFields()}
            </div>

            {/* Color Options */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Background</label>
                <div className="flex gap-2">
                  <input
                    type="color"
                    value={backgroundColor}
                    onChange={(e) => setBackgroundColor(e.target.value)}
                    className="w-12 h-10 rounded cursor-pointer"
                  />
                  <input
                    type="text"
                    value={backgroundColor}
                    onChange={(e) => setBackgroundColor(e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Foreground</label>
                <div className="flex gap-2">
                  <input
                    type="color"
                    value={foregroundColor}
                    onChange={(e) => setForegroundColor(e.target.value)}
                    className="w-12 h-10 rounded cursor-pointer"
                  />
                  <input
                    type="text"
                    value={foregroundColor}
                    onChange={(e) => setForegroundColor(e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
            </div>

            {/* Error Correction Level */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Error Correction</label>
              <select
                value={errorLevel}
                onChange={(e) => setErrorLevel(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="L">Low (~7%)</option>
                <option value="M">Medium (~15%)</option>
                <option value="Q">Quartile (~25%)</option>
                <option value="H">High (~30%)</option>
              </select>
            </div>

            {/* Generate Button */}
            <button
              onClick={generateQRCode}
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition-colors disabled:bg-gray-400"
            >
              {loading ? 'Generating...' : 'Generate QR Code'}
            </button>
          </div>

          {/* Right Panel - Preview */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Preview</h2>
            
            <div className="flex items-center justify-center min-h-[400px] bg-gray-50 rounded-lg">
              {qrCodeSVG ? (
                <div className="text-center">
                  <div 
                    dangerouslySetInnerHTML={{ __html: qrCodeSVG }}
                    className="inline-block"
                  />
                  <button
                    onClick={downloadQRCode}
                    className="mt-4 flex items-center gap-2 mx-auto px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
                  >
                    <Download size={20} />
                    Download SVG
                  </button>
                </div>
              ) : (
                <p className="text-gray-400">Your QR code will appear here</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}