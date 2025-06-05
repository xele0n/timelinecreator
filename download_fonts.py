#!/usr/bin/env python3
"""
Script to download free fonts for the Timeline Creator application.
Run this script to download fonts that will be bundled with the app.
"""

import os
import urllib.request
import zipfile
import tempfile

def download_and_extract_font(url, font_filename, extract_path):
    """Download and extract a font file."""
    try:
        print(f"Downloading font from {url}...")
        
        # Create fonts directory if it doesn't exist
        os.makedirs(extract_path, exist_ok=True)
        
        # Download to temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            urllib.request.urlretrieve(url, temp_file.name)
            
            # If it's a zip file, extract it
            if url.endswith('.zip'):
                with zipfile.ZipFile(temp_file.name, 'r') as zip_ref:
                    # Extract only TTF files
                    for file_info in zip_ref.filelist:
                        if file_info.filename.endswith('.ttf'):
                            file_info.filename = os.path.basename(file_info.filename)
                            zip_ref.extract(file_info, extract_path)
                            print(f"Extracted: {file_info.filename}")
            else:
                # Direct TTF file
                font_path = os.path.join(extract_path, font_filename)
                os.rename(temp_file.name, font_path)
                print(f"Downloaded: {font_filename}")
                
        # Clean up temp file
        try:
            os.unlink(temp_file.name)
        except:
            pass
            
    except Exception as e:
        print(f"Error downloading font: {e}")

def main():
    """Download free fonts for the application."""
    
    # Create fonts directory
    fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    
    print("Downloading free fonts for Timeline Creator...")
    print(f"Installing fonts to: {fonts_dir}")
    
    # Download DejaVu Sans (SIL Open Font License)
    # This is a high-quality, widely compatible font
    dejavu_url = "https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-fonts-ttf-2.37.zip"
    download_and_extract_font(dejavu_url, "DejaVuSans.ttf", fonts_dir)
    
    print("\nFont download complete!")
    print("The application will now use these bundled fonts on servers without system fonts.")
    print("\nIf you're deploying to a server, you can also install system fonts using:")
    print("  Ubuntu/Debian: sudo apt-get install fonts-dejavu-core")
    print("  CentOS/RHEL: sudo yum install dejavu-sans-fonts")

if __name__ == "__main__":
    main() 