"""
Script to check available fonts on the system.
"""

import os
import platform
from PIL import ImageFont

def get_available_fonts():
    """Get a list of available fonts on the system."""
    
    print("Checking available fonts on your system...\n")
    
    # Common font directories based on OS
    if platform.system() == "Windows":
        font_dirs = [
            r"C:\Windows\Fonts",
            os.path.expanduser(r"~\AppData\Local\Microsoft\Windows\Fonts")
        ]
    elif platform.system() == "Darwin":  # macOS
        font_dirs = [
            "/Library/Fonts",
            "/System/Library/Fonts",
            os.path.expanduser("~/Library/Fonts")
        ]
    else:  # Linux
        font_dirs = [
            "/usr/share/fonts",
            "/usr/local/share/fonts",
            os.path.expanduser("~/.fonts")
        ]
    
    fonts = []
    for font_dir in font_dirs:
        if os.path.exists(font_dir):
            for root, dirs, files in os.walk(font_dir):
                for file in files:
                    if file.lower().endswith(('.ttf', '.otf')):
                        fonts.append(os.path.join(root, file))
    
    # Print fonts by category
    print("=" * 70)
    print("AVAILABLE FONTS ON YOUR SYSTEM")
    print("=" * 70)
    
    # Categorize fonts
    bold_fonts = []
    mono_fonts = []
    regular_fonts = []
    
    for font in sorted(fonts):
        font_name = os.path.basename(font)
        font_lower = font_name.lower()
        
        if 'bold' in font_lower:
            bold_fonts.append((font_name, font))
        elif 'mono' in font_lower or 'consola' in font_lower or 'courier' in font_lower:
            mono_fonts.append((font_name, font))
        else:
            regular_fonts.append((font_name, font))
    
    print("\n📌 BEST FOR RPG GAMES (Bold/Heavy fonts):")
    print("-" * 70)
    for name, path in bold_fonts[:15]:  # Show top 15
        print(f"  {name}")
        print(f"    Path: {path}")
    
    print("\n📌 MONOSPACE FONTS (Good for pixelated/retro look):")
    print("-" * 70)
    for name, path in mono_fonts[:10]:  # Show top 10
        print(f"  {name}")
        print(f"    Path: {path}")
    
    print("\n📌 REGULAR FONTS (General use):")
    print("-" * 70)
    for name, path in regular_fonts[:10]:  # Show top 10
        print(f"  {name}")
        print(f"    Path: {path}")
    
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS FOR RPG-STYLE GAMES:")
    print("=" * 70)
    
    recommendations = [
        ("Arial Black / Arial Bold", "Bold, readable, good for titles"),
        ("Impact", "Very bold, great for dramatic titles"),
        ("Consolas Bold", "Monospace, good for retro/pixel look"),
        ("Courier New Bold", "Classic monospace, pixelated feel"),
        ("Georgia Bold", "Serif font, medieval/fantasy feel"),
        ("Times New Roman Bold", "Classic serif, traditional RPG feel"),
        ("Trebuchet MS Bold", "Modern, clean, readable"),
    ]
    
    for font_name, description in recommendations:
        print(f"\n  {font_name}")
        print(f"    → {description}")
    
    print("\n" + "=" * 70)
    print(f"\nTotal fonts found: {len(fonts)}")
    
    # Try to find specific good fonts
    print("\n" + "=" * 70)
    print("TESTING SPECIFIC FONTS FOR RPG USE:")
    print("=" * 70)
    
    test_fonts = [
        "arialbd.ttf",  # Arial Bold
        "impact.ttf",   # Impact
        "consolab.ttf", # Consolas Bold
        "courbd.ttf",   # Courier New Bold
        "timesbd.ttf",  # Times New Roman Bold
        "georgiab.ttf", # Georgia Bold
    ]
    
    for test_font in test_fonts:
        found = False
        for font_path in fonts:
            if test_font.lower() in font_path.lower():
                print(f"\n  ✅ {test_font} FOUND")
                print(f"     Path: {font_path}")
                found = True
                break
        if not found:
            print(f"\n  ❌ {test_font} NOT FOUND")

if __name__ == "__main__":
    get_available_fonts()
