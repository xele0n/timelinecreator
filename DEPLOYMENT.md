# Timeline Creator Deployment Guide

## Font Support for Servers

The Timeline Creator application requires TrueType fonts to render text properly. On many Linux servers, fonts may not be installed by default, which can cause text rendering issues.

### For Ubuntu/Debian Servers

```bash
# Install essential fonts
sudo apt-get update
sudo apt-get install -y fonts-dejavu-core fonts-liberation fonts-noto-core

# Optional: Install additional fonts for better appearance
sudo apt-get install -y fonts-ubuntu fonts-opensans
```

### For CentOS/RHEL Servers

```bash
# Install essential fonts
sudo yum install -y dejavu-sans-fonts liberation-fonts google-noto-sans-fonts

# Or for newer versions with dnf
sudo dnf install -y dejavu-sans-fonts liberation-fonts google-noto-sans-fonts
```

### For Alpine Linux (Docker)

If using Alpine Linux in Docker, add this to your Dockerfile:

```dockerfile
RUN apk add --no-cache \
    font-noto \
    fontconfig \
    ttf-dejavu \
    ttf-liberation
```

### For Docker Deployment

Complete Dockerfile example:

```dockerfile
FROM python:3.9-slim

# Install system dependencies including fonts
RUN apt-get update && apt-get install -y \
    fonts-dejavu-core \
    fonts-liberation \
    fonts-noto-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

### Verifying Font Installation

You can verify that fonts are properly installed by running:

```bash
# Check available fonts
fc-list | grep -i "dejavu\|liberation\|noto"

# Or specifically for the fonts our app looks for
ls -la /usr/share/fonts/truetype/dejavu/
ls -la /usr/share/fonts/truetype/liberation/
```

### Alternative: Bundling Fonts

If you cannot install system fonts, you can bundle fonts with your application:

1. Create a `fonts/` directory in your project
2. Download open-source fonts like DejaVu Sans or Liberation Sans
3. Place the `.ttf` files in the `fonts/` directory
4. The application will automatically detect and use bundled fonts

### Common Issues

- **Text appears as boxes or is missing**: Usually indicates missing fonts. Install the packages above.
- **Text is too small or poorly rendered**: Make sure TrueType fonts are installed, not just bitmap fonts.
- **Application runs but timeline looks blank**: Check the server logs for font loading errors.

### Production Environment Variables

Consider setting these environment variables for better font handling:

```bash
export FONTCONFIG_PATH=/usr/share/fontconfig
export FONTCONFIG_FILE=/etc/fonts/fonts.conf
``` 