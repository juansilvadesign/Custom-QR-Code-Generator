#!/usr/bin/env python3
"""
Custom QR Code Generator with Interactive Configuration

This script allows users to create QR codes with custom colors and content
through an interactive terminal interface.
"""

from qrcodegen import QrCode, QrSegment
import re
import sys
import os


def get_color_input(prompt: str, default_color: str) -> str:
    """Get color input from user with validation."""
    print(f"\n{prompt}")
    print("You can enter colors in the following formats:")
    print("  - Hex: #FF0000, #ff0000, or ff0000")
    print("  - RGB: rgb(255,0,0) or RGB(255, 0, 0)")
    print("  - Color names: red, blue, green, white, black, etc.")
    print(f"  - Press Enter for default: {default_color}")
    
    while True:
        color = input("Enter color: ").strip()
        
        # Use default if empty
        if not color:
            return default_color
            
        # Validate hex colors
        if color.startswith('#'):
            if re.match(r'^#[0-9A-Fa-f]{6}$', color):
                return color
            else:
                print("Invalid hex format. Use #RRGGBB (e.g., #FF0000)")
                continue
        
        # Add # to hex colors without it
        if re.match(r'^[0-9A-Fa-f]{6}$', color):
            return f"#{color}"
            
        # Validate RGB format
        if color.lower().startswith('rgb'):
            rgb_match = re.match(r'rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', color.lower())
            if rgb_match:
                r, g, b = map(int, rgb_match.groups())
                if all(0 <= val <= 255 for val in [r, g, b]):
                    return f"#{r:02X}{g:02X}{b:02X}"
                else:
                    print("RGB values must be between 0 and 255")
                    continue
            else:
                print("Invalid RGB format. Use rgb(255,0,0)")
                continue
        
        # Common color names
        color_names = {
            'black': '#000000',
            'white': '#FFFFFF',
            'red': '#FF0000',
            'green': '#00FF00',
            'blue': '#0000FF',
            'yellow': '#FFFF00',
            'cyan': '#00FFFF',
            'magenta': '#FF00FF',
            'orange': '#FFA500',
            'purple': '#800080',
            'pink': '#FFC0CB',
            'brown': '#A52A2A',
            'gray': '#808080',
            'grey': '#808080',
            'navy': '#000080',
            'darkblue': '#00008B',
            'darkgreen': '#006400',
            'darkred': '#8B0000'
        }
        
        if color.lower() in color_names:
            return color_names[color.lower()]
        
        print(f"Unknown color '{color}'. Please try again.")


def get_error_correction_level() -> QrCode.Ecc:
    """Get error correction level from user."""
    print("\nChoose error correction level:")
    print("1. Low (~7% correction)")
    print("2. Medium (~15% correction) [Recommended]")
    print("3. Quartile (~25% correction)")
    print("4. High (~30% correction)")
    
    while True:
        choice = input("Enter choice (1-4) or press Enter for Medium: ").strip()
        
        if not choice or choice == '2':
            return QrCode.Ecc.MEDIUM
        elif choice == '1':
            return QrCode.Ecc.LOW
        elif choice == '3':
            return QrCode.Ecc.QUARTILE
        elif choice == '4':
            return QrCode.Ecc.HIGH
        else:
            print("Invalid choice. Please enter 1-4.")


def get_unique_filename(base_filename: str, directory: str = "saved") -> str:
    """Generate a unique filename, adding (1), (2), etc. if duplicates exist."""
    # Create the saved directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")
    
    # Remove extension if present and add .svg
    name_without_ext = base_filename.split('.')[0]
    filename = f"{name_without_ext}.svg"
    full_path = os.path.join(directory, filename)
    
    # Check if file exists and add counter if needed
    counter = 1
    original_path = full_path
    
    while os.path.exists(full_path):
        filename = f"{name_without_ext} ({counter}).svg"
        full_path = os.path.join(directory, filename)
        counter += 1
    
    return full_path


def get_content_type():
    """Get the type of content from user."""
    print("\nWhat type of content do you want to encode?")
    print("1. Plain text")
    print("2. URL/Website link")
    print("3. Email address")
    print("4. Phone number")
    print("5. WiFi network credentials")
    print("6. SMS message")
    
    while True:
        choice = input("Enter choice (1-6): ").strip()
        if choice in ['1', '2', '3', '4', '5', '6']:
            return choice
        print("Invalid choice. Please enter 1-6.")


def get_content(content_type: str) -> str:
    """Get the actual content based on the type."""
    if content_type == '1':  # Plain text
        return input("Enter the text to encode: ")
    
    elif content_type == '2':  # URL
        url = input("Enter the URL (with or without http://): ").strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    elif content_type == '3':  # Email
        email = input("Enter email address: ").strip()
        subject = input("Enter email subject (optional): ").strip()
        body = input("Enter email body (optional): ").strip()
        
        mailto = f"mailto:{email}"
        params = []
        if subject:
            params.append(f"subject={subject}")
        if body:
            params.append(f"body={body}")
        if params:
            mailto += "?" + "&".join(params)
        return mailto
    
    elif content_type == '4':  # Phone
        phone = input("Enter phone number: ").strip()
        return f"tel:{phone}"
    
    elif content_type == '5':  # WiFi
        ssid = input("Enter WiFi network name (SSID): ").strip()
        password = input("Enter WiFi password: ").strip()
        security = input("Enter security type (WPA/WEP/nopass) [WPA]: ").strip() or "WPA"
        hidden = input("Is network hidden? (y/n) [n]: ").strip().lower() == 'y'
        
        return f"WIFI:T:{security};S:{ssid};P:{password};H:{'true' if hidden else 'false'};;"
    
    elif content_type == '6':  # SMS
        phone = input("Enter phone number: ").strip()
        message = input("Enter SMS message: ").strip()
        return f"sms:{phone}?body={message}"


def to_svg_str_custom(qr: QrCode, border: int, bg_color: str, fg_color: str) -> str:
    """Returns SVG code for QR Code with custom colors."""
    if border < 0:
        raise ValueError("Border must be non-negative")
    
    parts: list[str] = []
    parts.append('<?xml version="1.0" encoding="UTF-8"?>\n')
    parts.append('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n')
    dimension = qr.get_size() + border * 2
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 {dimension} {dimension}" stroke="none">\n')
    parts.append(f'\t<rect width="100%" height="100%" fill="{bg_color}"/>\n')
    parts.append('\t<path d="')
    
    for y in range(qr.get_size()):
        for x in range(qr.get_size()):
            if qr.get_module(x, y):
                parts.append(f'M{x+border},{y+border}h1v1h-1z ')
    
    parts.append(f'" fill="{fg_color}"/>\n')
    parts.append('</svg>\n')
    return "".join(parts)


def print_qr_terminal(qr: QrCode, use_colors: bool = False, bg_dark: bool = False):
    """Print QR code to terminal with optional color support."""
    border = 2
    
    # ANSI color codes
    if use_colors:
        if bg_dark:
            # Dark background, light foreground
            bg_char = "\033[40m  \033[0m"  # Black background
            fg_char = "\033[47m  \033[0m"  # White background
        else:
            # Light background, dark foreground  
            bg_char = "\033[47m  \033[0m"  # White background
            fg_char = "\033[40m  \033[0m"  # Black background
    else:
        # No colors, use Unicode blocks
        bg_char = "  "
        fg_char = "██"
    
    print("\nQR Code preview:")
    for y in range(-border, qr.get_size() + border):
        line = ""
        for x in range(-border, qr.get_size() + border):
            if qr.get_module(x, y):
                line += fg_char
            else:
                line += bg_char
        print(line)
    print()


def main():
    """Main interactive function."""
    print("=" * 60)
    print("        Custom QR Code Generator")
    print("=" * 60)
    print("Create QR codes with custom colors and content!")
    
    try:
        # Get content
        content_type = get_content_type()
        content = get_content(content_type)
        
        if not content.strip():
            print("Error: Content cannot be empty!")
            return
        
        # Get error correction level
        ecc_level = get_error_correction_level()
        
        # Get colors
        bg_color = get_color_input("Choose background color:", "#FFFFFF")
        fg_color = get_color_input("Choose foreground color (QR modules):", "#000000")
        
        # Get border size
        print(f"\nBorder size (modules around QR code):")
        border_input = input("Enter border size (0-10) [4]: ").strip()
        try:
            border = int(border_input) if border_input else 4
            border = max(0, min(10, border))  # Clamp between 0 and 10
        except ValueError:
            border = 4
        
        # Get filename
        print(f"\nOutput filename:")
        base_filename = input("Enter filename (without extension) [custom_qr]: ").strip()
        if not base_filename:
            base_filename = "custom_qr"
        
        # Get unique filename with full path
        filename = get_unique_filename(base_filename)
        
        print(f"\nGenerating QR code...")
        print(f"Content: {content}")
        print(f"Error correction: {ecc_level}")
        print(f"Background: {bg_color}")
        print(f"Foreground: {fg_color}")
        print(f"Border: {border} modules")
        print(f"Output file: {filename}")
        
        # Generate QR code
        qr = QrCode.encode_text(content, ecc_level)
        
        # Generate SVG
        svg = to_svg_str_custom(qr, border, bg_color, fg_color)
        
        # Save to file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(svg)
        
        print(f"\n✅ QR code saved as '{filename}'")
        
        # Show terminal preview
        show_preview = input("\nShow terminal preview? (y/n) [y]: ").strip().lower()
        if show_preview != 'n':
            try:
                # Try to determine if background is dark
                bg_is_dark = bg_color.lower() in ['#000000', '#0c0e12', 'black'] or \
                           (bg_color.startswith('#') and 
                            sum(int(bg_color[i:i+2], 16) for i in (1, 3, 5)) < 384)
                print_qr_terminal(qr, use_colors=True, bg_dark=bg_is_dark)
            except:
                # Fallback to simple preview
                print_qr_terminal(qr, use_colors=False)
        
        # Ask if user wants to create another
        another = input("Create another QR code? (y/n) [n]: ").strip().lower()
        if another == 'y':
            print("\n" + "=" * 60)
            main()  # Recursive call for another QR code
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nError: {e}")
        print("Please try again.")


if __name__ == "__main__":
    main()