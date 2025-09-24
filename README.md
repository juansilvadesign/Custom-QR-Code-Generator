# 🎨 Custom QR Code Generator

<div align="center">
  <img src="images/logo-v1.png" alt="Custom QR Code Generator Logo" width="128" height="128">
  
  [![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://python.org)
  [![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
  [![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
  
  *A powerful, interactive QR code generator with custom colors and multiple content types*
</div>

## ✨ Features

- 🎨 **Custom Colors**: Choose any background and foreground colors (hex, RGB, or color names)
- 📱 **Multiple Content Types**: Support for text, URLs, emails, phone numbers, WiFi credentials, and SMS
- 🛡️ **Error Correction**: Four levels of error correction (Low, Medium, Quartile, High)
- 🖥️ **Terminal Preview**: See your QR code directly in the terminal with color support
- 💾 **Smart File Management**: Automatic unique filename generation to prevent overwrites
- 🎯 **Interactive Interface**: User-friendly prompts guide you through the creation process
- 🔧 **Customizable Borders**: Adjustable border size around QR codes
- 📁 **Organized Output**: All generated QR codes are saved in the `saved/` directory

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Windows, macOS, or Linux

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/juansilvadesign/Custom-QR-Code-Generator.git
   cd Custom-QR-Code-Generator
   ```

2. **Set up a virtual environment** (recommended)
   ```bash
   python -m venv .env
   ```

3. **Activate the virtual environment**
   - **Windows**: `.env\Scripts\activate`
   - **macOS/Linux**: `source .env/bin/activate`

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

#### Option 1: Using the Batch File (Windows)
1. Copy `run.bat.template` to `run.bat`
2. Edit `run.bat` and replace `[YOUR_PROJECT_PATH]` with your actual project path
3. Double-click `run.bat` or run it from command prompt

#### Option 2: Direct Python Execution
```bash
python main.py
```

## 📖 Usage Guide

### Content Types Supported

| Type | Description | Example Output |
|------|-------------|----------------|
| **Plain Text** | Any text content | Direct text encoding |
| **URL/Website** | Web links with auto-protocol detection | `https://example.com` |
| **Email** | Email addresses with optional subject/body | `mailto:user@example.com?subject=Hello` |
| **Phone Number** | Phone numbers for direct dialing | `tel:+1234567890` |
| **WiFi Credentials** | Network connection info | `WIFI:T:WPA;S:NetworkName;P:password;;` |
| **SMS Message** | Pre-filled text messages | `sms:+1234567890?body=Hello` |

### Color Format Options

The generator accepts colors in multiple formats:

- **Hex Colors**: `#FF0000`, `#ff0000`, or `ff0000`
- **RGB Values**: `rgb(255,0,0)` or `RGB(255, 0, 0)`
- **Color Names**: `red`, `blue`, `green`, `white`, `black`, `orange`, `purple`, etc.

### Error Correction Levels

| Level | Correction Capacity | Use Case |
|-------|-------------------|----------|
| **Low** | ~7% | Clean environments, larger QR codes |
| **Medium** | ~15% | General use (recommended) |
| **Quartile** | ~25% | Moderately damaged environments |
| **High** | ~30% | High-damage risk environments |

## 🎯 Examples

### Creating a Website QR Code
```
Content Type: URL/Website link
URL: github.com/juansilvadesign
Background: white
Foreground: #2196F3
Border: 4 modules
```

### Creating a WiFi QR Code
```
Content Type: WiFi network credentials
Network Name: MyWiFi
Password: mypassword123
Security: WPA
Hidden: No
```

### Creating a Custom Styled QR Code
```
Content Type: Plain text
Text: Hello, World!
Background: #1a1a1a
Foreground: #00ff41
Border: 2 modules
```

## 📁 Project Structure

```
Custom-QR-Code-Generator/
├── main.py                 # Main application with interactive interface
├── qrcodegen.py           # QR code generation library (Project Nayuki)
├── requirements.txt       # Python dependencies
├── run.bat.template      # Template for Windows batch file
├── LICENSE               # MIT License
├── README.md            # This file
├── images/              # Logo and assets
│   ├── logo-v1.png
│   ├── logo-v1.ico
│   ├── logo-v2.png
│   └── logo-v2.ico
└── saved/               # Generated QR codes (auto-created)
    └── (your QR codes will be saved here)
```

## 🛠️ Technical Details

### Dependencies

The project uses minimal dependencies for maximum compatibility:
- **setuptools**: For package management and distribution tools
- **Built-in modules**: `re`, `sys`, `os` for core functionality

### QR Code Library

This project uses the high-quality QR code generator library by [Project Nayuki](https://www.nayuki.io/page/qr-code-generator-library), which provides:
- Full QR Code Model 2 specification support
- All versions (sizes) from 1 to 40
- All 4 error correction levels
- 4 character encoding modes
- Clean, well-documented code

### Output Format

- **File Format**: SVG (Scalable Vector Graphics)
- **Benefits**: 
  - Infinite scalability without quality loss
  - Small file sizes
  - Wide compatibility
  - Easy to convert to other formats

## 🎨 Customization

### Adding New Color Names

You can extend the color name dictionary in `main.py` by modifying the `color_names` dictionary in the `get_color_input()` function:

```python
color_names = {
    'black': '#000000',
    'white': '#FFFFFF',
    # Add your custom colors here
    'myblue': '#1E88E5',
    'mygreen': '#43A047',
}
```

### Modifying Default Settings

Default values can be changed in the respective functions:
- Error correction level: `get_error_correction_level()`
- Border size: Line with `border = int(border_input) if border_input else 4`
- Default colors: `get_color_input()` function calls

## 🤝 Contributing

We welcome contributions from developers of all skill levels! Whether you want to fix bugs, add features, improve documentation, or suggest new ideas, your help is appreciated.

👉 **See our [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:**
- Setting up your development environment
- Code style guidelines
- Pull request process
- Feature ideas and roadmap
- Bug reporting guidelines

Quick start for contributors:
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/AmazingFeature`
3. Make your changes and test thoroughly
4. Commit: `git commit -m 'Add some AmazingFeature'`
5. Push: `git push origin feature/AmazingFeature` 
6. Open a Pull Request

## 📋 FAQ

**Q: Why SVG format instead of PNG?**
A: SVG provides infinite scalability, smaller file sizes for simple graphics, and easy conversion to other formats when needed.

**Q: Can I use this for commercial projects?**
A: Yes! This project is licensed under MIT License, which allows commercial use.

**Q: The QR code won't scan properly. What should I do?**
A: Try increasing the error correction level or ensuring sufficient contrast between background and foreground colors.

**Q: How do I convert SVG to PNG?**
A: You can use online converters, or tools like Inkscape, or even browsers (open SVG, right-click, save as image).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The QR code generation library is also under MIT License by Project Nayuki.

## 🙏 Acknowledgments

- **[Project Nayuki](https://www.nayuki.io/)** for the excellent QR code generation library
- **[Denso Wave](https://www.denso-wave.com/)** for inventing QR codes
- The Python community for excellent documentation and tools

## 📞 Support

If you encounter any issues or have questions:

1. Check the [FAQ section](#-faq) above
2. Search existing [GitHub Issues](../../issues)
3. Create a new issue with detailed information about your problem

---

<div align="center">
  Made with ❤️ by <a href="https://github.com/juansilvadesign">Juan Silva</a>
  <br>
  <sub>⭐ Star this repository if you found it useful!</sub>
</div>