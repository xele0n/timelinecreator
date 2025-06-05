from flask import Flask, render_template, request, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import base64
from datetime import datetime, timedelta
import os
import csv
from werkzeug.utils import secure_filename
import math
import logging

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Set up logging for font debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def draw_ultra_smooth_curve(draw, start_point, end_point, color, width=2, curve_factor=0.5):
    """Draw an ultra-smooth curved line using high-resolution Bezier curves."""
    x1, y1 = float(start_point[0]), float(start_point[1])
    x2, y2 = float(end_point[0]), float(end_point[1])
    
    # Convert color to RGB tuple if it's a string
    if isinstance(color, str):
        if color.lower() == 'gray' or color.lower() == 'grey':
            color = (128, 128, 128)
        elif color.lower() == 'black':
            color = (0, 0, 0)
        elif color.lower() == 'white':
            color = (255, 255, 255)
        elif color.startswith('#'):
            color = hex_to_rgb(color)
        else:
            color = (128, 128, 128)  # Default to gray
    
    # Calculate distance and direction
    dx = x2 - x1
    dy = y2 - y1
    distance = math.sqrt(dx*dx + dy*dy)
    
    # Adaptive curve control based on distance and direction
    if abs(dx) > abs(dy):  # More horizontal
        control_distance = min(abs(dx) * curve_factor, distance * 0.4)
        cx1 = x1 + (control_distance if dx > 0 else -control_distance)
        cy1 = y1 + dy * 0.1
        cx2 = x2 - (control_distance if dx > 0 else -control_distance)
        cy2 = y2 + dy * 0.1
    else:  # More vertical
        control_distance = min(abs(dy) * curve_factor, distance * 0.4)
        cx1 = x1 + dx * 0.1
        cy1 = y1 + (control_distance if dy > 0 else -control_distance)
        cx2 = x2 + dx * 0.1
        cy2 = y2 - (control_distance if dy > 0 else -control_distance)
    
    # Generate smooth curve with many points for ultra-smooth appearance
    segments = max(50, int(distance / 3))  # Adaptive segment count
    points = []
    
    for i in range(segments + 1):
        t = i / segments
        # Smooth cubic Bezier curve
        mt = 1 - t
        x = (mt**3 * x1 + 
             3 * mt**2 * t * cx1 + 
             3 * mt * t**2 * cx2 + 
             t**3 * x2)
        y = (mt**3 * y1 + 
             3 * mt**2 * t * cy1 + 
             3 * mt * t**2 * cy2 + 
             t**3 * y2)
        points.append((int(x), int(y)))
    
    # Draw the ultra-smooth curve
    for i in range(len(points) - 1):
        draw.line([points[i], points[i + 1]], fill=color, width=int(width))
    
    # Add anti-aliasing effect by drawing slightly thinner lines around the main line
    if width > 2:
        try:
            lighter_color = tuple(min(255, int(c + (255-c)*0.3)) for c in color)
            for i in range(len(points) - 1):
                draw.line([points[i], points[i + 1]], fill=lighter_color, width=max(1, int(width)-1))
        except (TypeError, ValueError):
            # Skip anti-aliasing if color processing fails
            pass

def draw_flowing_branch(draw, start_x, timeline_y, branch_y, end_x, color, width=4):
    """Draw a beautifully flowing branching line for duration events."""
    # Convert to float for calculations
    start_x = float(start_x)
    timeline_y = float(timeline_y)
    branch_y = float(branch_y)
    end_x = float(end_x)
    width = int(width)
    
    # Calculate curve parameters for natural flow
    branch_distance = abs(branch_y - timeline_y)
    horizontal_distance = abs(end_x - start_x)
    
    # Create graceful S-curve for the branch
    if horizontal_distance > 20:
        # Multi-point flowing curve
        quarter_x = start_x + (end_x - start_x) * 0.25
        three_quarter_x = start_x + (end_x - start_x) * 0.75
        mid_x = (start_x + end_x) / 2
        
        # Calculate flowing intermediate points
        curve_offset = branch_distance * 0.3
        mid_y1 = timeline_y + (branch_y - timeline_y) * 0.7
        mid_y2 = branch_y + (curve_offset if branch_y > timeline_y else -curve_offset)
        mid_y3 = timeline_y + (branch_y - timeline_y) * 0.7
        
        # Draw flowing segments
        draw_ultra_smooth_curve(draw, (start_x, timeline_y), (quarter_x, mid_y1), color, width, 0.8)
        draw_ultra_smooth_curve(draw, (quarter_x, mid_y1), (mid_x, mid_y2), color, width, 0.6)
        draw_ultra_smooth_curve(draw, (mid_x, mid_y2), (three_quarter_x, mid_y3), color, width, 0.6)
        draw_ultra_smooth_curve(draw, (three_quarter_x, mid_y3), (end_x, timeline_y), color, width, 0.8)
    else:
        # Simple flowing curve for short distances
        mid_x = (start_x + end_x) / 2
        peak_y = branch_y + (branch_distance * 0.3 if branch_y > timeline_y else -branch_distance * 0.3)
        
        draw_ultra_smooth_curve(draw, (start_x, timeline_y), (mid_x, peak_y), color, width, 0.7)
        draw_ultra_smooth_curve(draw, (mid_x, peak_y), (end_x, timeline_y), color, width, 0.7)

def get_optimal_date_position(x_pos, timeline_y, existing_positions, text_width, is_duration=False):
    """Calculate optimal position for date text to avoid overlaps."""
    x_pos = float(x_pos)
    timeline_y = float(timeline_y)
    text_width = float(text_width)
    
    base_y = timeline_y + 25  # Default position below timeline
    alternative_y = timeline_y - 45  # Alternative position above timeline
    
    # Check for overlaps with existing positions
    margin = 15
    
    def check_overlap(x, y, width):
        for existing_x, existing_y, existing_width in existing_positions:
            existing_x = float(existing_x)
            existing_y = float(existing_y)
            existing_width = float(existing_width)
            if (abs(x - existing_x) < (width + existing_width) / 2 + margin and
                abs(y - existing_y) < 25):
                return True
        return False
    
    # Try default position first
    if not check_overlap(x_pos, base_y, text_width):
        return base_y, False
    
    # Try alternative position above timeline
    if not check_overlap(x_pos, alternative_y, text_width):
        return alternative_y, True
    
    # If both positions conflict, find an available offset
    for offset in range(25, 120, 25):
        # Try below with offset
        test_y = base_y + offset
        if not check_overlap(x_pos, test_y, text_width):
            return test_y, False
        
        # Try above with offset
        test_y = alternative_y - offset
        if not check_overlap(x_pos, test_y, text_width):
            return test_y, True
    
    # Fallback: use default position
    return base_y, False

def format_date_readable(date_obj):
    """Format date as DD Month YYYY for better readability."""
    return date_obj.strftime('%d %B %Y')

def get_text_dimensions(draw, text, font):
    """Safely get text dimensions with fallbacks for different font types."""
    text = str(text)  # Ensure string
    try:
        # Try the modern textbbox method first
        bbox = draw.textbbox((0, 0), text, font=font)
        width = float(bbox[2] - bbox[0])
        height = float(bbox[3] - bbox[1])
        return width, height
    except (AttributeError, TypeError):
        try:
            # Fallback to older textsize method
            width, height = draw.textsize(text, font=font)
            return float(width), float(height)
        except (AttributeError, TypeError):
            # Last resort: estimate based on character count and scale factor
            if hasattr(font, 'size'):
                char_width = font.size * 0.6
                char_height = font.size * 1.2
            else:
                # Very basic fallback
                char_width = 12
                char_height = 16
            return float(len(text) * char_width), float(char_height)

def get_font(size):
    """Get a font with the specified size, trying multiple fallback options."""
    
    logger.info(f"Attempting to load font with size: {size}")
    
    # First try local bundled fonts
    try:
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        local_font_paths = [
            os.path.join(script_dir, 'fonts', 'DejaVuSans.ttf'),
            os.path.join(script_dir, 'fonts', 'LiberationSans-Regular.ttf'),
            os.path.join(script_dir, 'fonts', 'OpenSans-Regular.ttf'),
            os.path.join(script_dir, 'fonts', 'arial.ttf'),
        ]
        
        for font_path in local_font_paths:
            if os.path.exists(font_path):
                try:
                    logger.info(f"Successfully loaded local font: {font_path}")
                    return ImageFont.truetype(font_path, size)
                except (OSError, IOError) as e:
                    logger.warning(f"Failed to load local font {font_path}: {e}")
                    continue
    except Exception as e:
        logger.warning(f"Error checking local fonts: {e}")
    
    # Then try system fonts
    font_paths = [
        # Windows fonts
        "arial.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        # Linux/Unix fonts
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/System/Library/Fonts/Arial.ttf",  # macOS
        "/usr/share/fonts/truetype/opensans/OpenSans-Regular.ttf",
        "/usr/share/fonts/google-noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-R.ttf",
        # Generic fallbacks
        "DejaVuSans.ttf",
        "LiberationSans-Regular.ttf",
        "OpenSans-Regular.ttf",
        "Ubuntu-R.ttf"
    ]
    
    for font_path in font_paths:
        try:
            font = ImageFont.truetype(font_path, size)
            logger.info(f"Successfully loaded system font: {font_path}")
            return font
        except (OSError, IOError):
            continue
    
    logger.warning("No TrueType fonts found, falling back to default font")
    
    # Try to create a basic font directory and font if none exist
    try:
        import os
        font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
        if not os.path.exists(font_dir):
            os.makedirs(font_dir, exist_ok=True)
            logger.info(f"Created fonts directory: {font_dir}")
    except Exception as e:
        logger.warning(f"Could not create fonts directory: {e}")
    
    # Enhanced default font that works better with scaling
    try:
        # Create a better default font for server environments
        default_font = ImageFont.load_default()
        logger.info("Using PIL default font")
        
        # Try to create a synthetic font that scales better
        # This is a workaround for servers without proper font support
        class ScaledDefaultFont:
            def __init__(self, base_font, target_size):
                self.base_font = base_font
                self.size = target_size
                
        return ScaledDefaultFont(default_font, size)
    except Exception as e:
        logger.error(f"Error with default font: {e}")
        try:
            return ImageFont.load_default()
        except Exception as e2:
            logger.error(f"Critical font error: {e2}")
            # Last resort - return None and handle in calling code
            return None

def create_timeline_image(events):
    """Generate a high-quality timeline image from a list of events."""
    if not events:
        return None
    
    # High-resolution dimensions for crisp quality
    scale_factor = 2  # For high DPI rendering
    width = 2000 * scale_factor
    height = 1000 * scale_factor
    margin = 150 * scale_factor
    timeline_y = height // 2
    
    # Create high-resolution image with anti-aliasing
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Load high-quality fonts with appropriate scaling
    try:
        font_large = get_font(24 * scale_factor)
        font_medium = get_font(20 * scale_factor)
        font_small = get_font(16 * scale_factor)
        font_title = get_font(28 * scale_factor)
        
        # Ensure we have valid fonts, fallback to default if any are None
        if any(font is None for font in [font_large, font_medium, font_small, font_title]):
            default_font = ImageFont.load_default()
            font_large = font_large or default_font
            font_medium = font_medium or default_font
            font_small = font_small or default_font
            font_title = font_title or default_font
    except Exception as e:
        # Complete fallback to default fonts
        print(f"Font loading error: {e}")
        default_font = ImageFont.load_default()
        font_large = default_font
        font_medium = default_font
        font_small = default_font
        font_title = default_font
    
    # Parse and sort events by start date
    parsed_events = []
    for event in events:
        start_date = datetime.strptime(event['date'], '%Y-%m-%d')
        end_date = None
        if event.get('end_date'):
            end_date = datetime.strptime(event['end_date'], '%Y-%m-%d')
        
        parsed_events.append({
            'start_date': start_date,
            'end_date': end_date,
            'event': event['event'],
            'color': event.get('color', '#dc3545'),
            'original': event
        })
    
    parsed_events.sort(key=lambda x: x['start_date'])
    
    # Draw main timeline with elegant styling
    timeline_start = margin
    timeline_end = width - margin
    timeline_width = 6 * scale_factor
    
    # Draw main timeline with gradient effect
    for i in range(int(timeline_width)):
        alpha = 0.8 - (i * 0.1)
        gray_value = int(50 + i * 10)
        color = (gray_value, gray_value, gray_value)
        draw.line([(timeline_start, timeline_y - i), (timeline_end, timeline_y - i)], fill=color, width=1)
    
    # Add elegant rounded caps to timeline
    cap_radius = int(4 * scale_factor)
    draw.ellipse([timeline_start - cap_radius, timeline_y - cap_radius,
                  timeline_start + cap_radius, timeline_y + cap_radius], fill='black')
    draw.ellipse([timeline_end - cap_radius, timeline_y - cap_radius,
                  timeline_end + cap_radius, timeline_y + cap_radius], fill='black')
    
    # Calculate time range for positioning
    all_dates = [e['start_date'] for e in parsed_events]
    for e in parsed_events:
        if e['end_date']:
            all_dates.append(e['end_date'])
    
    if len(all_dates) == 1:
        date_range = timedelta(days=1)
        min_date = all_dates[0]
    else:
        min_date = min(all_dates)
        max_date = max(all_dates)
        date_range = max_date - min_date
        if date_range.days == 0:
            date_range = timedelta(days=1)
    
    def date_to_x_position(date):
        if date_range.days == 0:
            return float(width // 2)
        progress = (date - min_date).total_seconds() / date_range.total_seconds()
        return float(timeline_start + progress * (timeline_end - timeline_start))
    
    # Track positions to avoid overlaps
    used_positions = []
    date_positions = []
    
    # Draw events with enhanced quality
    for i, event in enumerate(parsed_events):
        color = hex_to_rgb(event['color'])
        start_x = date_to_x_position(event['start_date'])
        
        if event['end_date']:
            # Duration event with flowing curves
            end_x = date_to_x_position(event['end_date'])
            
            # Find available y position
            branch_height = 80 * scale_factor
            y_offset = 0
            while any(abs(pos - y_offset) < 60 * scale_factor for pos in used_positions):
                y_offset += 60 * scale_factor if i % 2 == 0 else -60 * scale_factor
            
            used_positions.append(y_offset)
            
            # Determine if above or below timeline
            is_above = (i % 2 == 0) or y_offset < 0
            direction = -1 if is_above else 1
            
            branch_y = timeline_y + direction * (branch_height + abs(y_offset))
            
            # Draw the beautiful flowing branch
            draw_flowing_branch(draw, start_x, timeline_y, branch_y, end_x, color, 6 * scale_factor)
            
            # Draw elegant start and end markers with soft glow
            circle_radius = int(8 * scale_factor)
            glow_radius = int(12 * scale_factor)
            
            # Soft glow effect
            for r in range(glow_radius, circle_radius, -1):
                alpha = max(0, 60 - (glow_radius - r) * 8)
                glow_color = tuple(min(255, int(c + alpha)) for c in color)
                draw.ellipse([
                    int(start_x - r), int(timeline_y - r),
                    int(start_x + r), int(timeline_y + r)
                ], fill=glow_color)
                draw.ellipse([
                    int(end_x - r), int(timeline_y - r),
                    int(end_x + r), int(timeline_y + r)
                ], fill=glow_color)
            
            # Main circles with elegant borders
            border_width = int(3 * scale_factor)
            inner_border_width = int(1 * scale_factor)
            
            draw.ellipse([
                int(start_x - circle_radius), int(timeline_y - circle_radius),
                int(start_x + circle_radius), int(timeline_y + circle_radius)
            ], fill=color, outline='white', width=border_width)
            draw.ellipse([
                int(start_x - circle_radius + 2), int(timeline_y - circle_radius + 2),
                int(start_x + circle_radius - 2), int(timeline_y + circle_radius - 2)
            ], outline='black', width=inner_border_width)
            
            draw.ellipse([
                int(end_x - circle_radius), int(timeline_y - circle_radius),
                int(end_x + circle_radius), int(timeline_y + circle_radius)
            ], fill=color, outline='white', width=border_width)
            draw.ellipse([
                int(end_x - circle_radius + 2), int(timeline_y - circle_radius + 2),
                int(end_x + circle_radius - 2), int(timeline_y + circle_radius - 2)
            ], outline='black', width=inner_border_width)
            
            # Event text with elegant styling
            event_text = str(event['event'])  # Ensure string type
            try:
                text_bbox = get_text_dimensions(draw, event_text, font_medium)
                text_width = text_bbox[0]
            except:
                text_width = float(len(event_text) * 12 * scale_factor)  # Fallback calculation
            
            text_x = float(start_x + end_x) / 2.0 - text_width / 2.0
            
            if is_above:
                text_y = float(branch_y - 35 * scale_factor)
            else:
                text_y = float(branch_y + 15 * scale_factor)
            
            # Elegant text background with soft shadow
            padding = int(8 * scale_factor)
            shadow_offset = int(3 * scale_factor)
            
            # Drop shadow
            draw.rectangle([
                int(text_x - padding + shadow_offset), int(text_y - 3 * scale_factor + shadow_offset),
                int(text_x + text_width + padding + shadow_offset), int(text_y + 25 * scale_factor + shadow_offset)
            ], fill=(200, 200, 200))
            
            # Main background
            draw.rectangle([
                int(text_x - padding), int(text_y - 3 * scale_factor),
                int(text_x + text_width + padding), int(text_y + 25 * scale_factor)
            ], fill='white', outline=color, width=int(2 * scale_factor))
            
            draw.text((int(text_x), int(text_y)), event_text, fill=color, font=font_medium)
            
            # Smart date positioning with new format
            start_date_text = format_date_readable(event['start_date'])
            end_date_text = format_date_readable(event['end_date'])
            
            try:
                start_bbox = get_text_dimensions(draw, start_date_text, font_small)
                start_width = float(start_bbox[0])
                end_bbox = get_text_dimensions(draw, end_date_text, font_small)
                end_width = float(end_bbox[0])
            except:
                start_width = float(len(start_date_text) * 10 * scale_factor)
                end_width = float(len(end_date_text) * 10 * scale_factor)
            
            # Calculate optimal positions
            start_date_y, start_above = get_optimal_date_position(
                start_x, timeline_y, date_positions, start_width, True)
            date_positions.append((float(start_x), float(start_date_y), float(start_width)))
            
            end_date_y, end_above = get_optimal_date_position(
                end_x, timeline_y, date_positions, end_width, True)
            date_positions.append((float(end_x), float(end_date_y), float(end_width)))
            
            # Draw elegant date labels
            date_padding = int(6 * scale_factor)
            
            # Start date
            draw.rectangle([
                int(start_x - start_width / 2.0 - date_padding), int(start_date_y - 3 * scale_factor),
                int(start_x + start_width / 2.0 + date_padding), int(start_date_y + 18 * scale_factor)
            ], fill='white', outline='gray', width=int(1 * scale_factor))
            draw.text((int(start_x - start_width / 2.0), int(start_date_y)), start_date_text, fill='black', font=font_small)
            
            # End date
            draw.rectangle([
                int(end_x - end_width / 2.0 - date_padding), int(end_date_y - 3 * scale_factor),
                int(end_x + end_width / 2.0 + date_padding), int(end_date_y + 18 * scale_factor)
            ], fill='white', outline='gray', width=int(1 * scale_factor))
            draw.text((int(end_x - end_width / 2.0), int(end_date_y)), end_date_text, fill='black', font=font_small)
            
        else:
            # Point event with flowing lines
            line_height = 70 * scale_factor
            top_point = (start_x, timeline_y - line_height)
            bottom_point = (start_x, timeline_y + line_height)
            
            # Draw elegant flowing vertical lines
            draw_ultra_smooth_curve(draw, top_point, (start_x, timeline_y), color, 4 * scale_factor, 0.3)
            draw_ultra_smooth_curve(draw, (start_x, timeline_y), bottom_point, color, 4 * scale_factor, 0.3)
            
            # Draw elegant circle with soft glow
            circle_radius = int(10 * scale_factor)
            glow_radius = int(15 * scale_factor)
            
            # Soft glow effect
            for r in range(glow_radius, circle_radius, -1):
                alpha = max(0, 40 - (glow_radius - r) * 5)
                glow_color = tuple(min(255, int(c + alpha)) for c in color)
                draw.ellipse([
                    int(start_x - r), int(timeline_y - r),
                    int(start_x + r), int(timeline_y + r)
                ], fill=glow_color)
            
            # Main circle with elegant border
            border_width = int(4 * scale_factor)
            inner_border_width = int(1 * scale_factor)
            
            draw.ellipse([
                int(start_x - circle_radius), int(timeline_y - circle_radius),
                int(start_x + circle_radius), int(timeline_y + circle_radius)
            ], fill=color, outline='white', width=border_width)
            draw.ellipse([
                int(start_x - circle_radius + 3), int(timeline_y - circle_radius + 3),
                int(start_x + circle_radius - 3), int(timeline_y + circle_radius - 3)
            ], outline='black', width=inner_border_width)
            
            # Smart date positioning with new format
            date_text = format_date_readable(event['start_date'])
            try:
                date_bbox = get_text_dimensions(draw, date_text, font_small)
                date_width = float(date_bbox[0])
            except:
                date_width = float(len(date_text) * 10 * scale_factor)
            
            date_y, date_above = get_optimal_date_position(
                start_x, timeline_y, date_positions, date_width, False)
            date_positions.append((float(start_x), float(date_y), float(date_width)))
            
            # Draw elegant date with background
            date_padding = int(6 * scale_factor)
            draw.rectangle([
                int(start_x - date_width / 2.0 - date_padding), int(date_y - 3 * scale_factor),
                int(start_x + date_width / 2.0 + date_padding), int(date_y + 18 * scale_factor)
            ], fill='white', outline='gray', width=int(1 * scale_factor))
            draw.text((int(start_x - date_width / 2.0), int(date_y)), date_text, fill='black', font=font_small)
            
            # Event description with elegant styling
            event_text = str(event['event'])  # Ensure string type
            try:
                event_bbox = get_text_dimensions(draw, event_text, font_large)
                event_width = float(event_bbox[0])
            except:
                event_width = float(len(event_text) * 16 * scale_factor)
            
            # Alternate text positioning
            if i % 2 == 0:
                text_y = float(timeline_y - 130 * scale_factor)
                connection_start = (start_x, timeline_y - circle_radius)
                connection_end = (start_x, text_y + 30 * scale_factor)
            else:
                text_y = float(timeline_y + 130 * scale_factor)
                connection_start = (start_x, timeline_y + circle_radius)
                connection_end = (start_x, text_y)
            
            # Elegant text background with shadow
            text_padding = int(10 * scale_factor)
            shadow_offset = int(3 * scale_factor)
            
            # Drop shadow
            draw.rectangle([
                int(start_x - event_width / 2.0 - text_padding + shadow_offset), int(text_y - 3 * scale_factor + shadow_offset),
                int(start_x + event_width / 2.0 + text_padding + shadow_offset), int(text_y + 28 * scale_factor + shadow_offset)
            ], fill=(200, 200, 200))
            
            # Main background
            draw.rectangle([
                int(start_x - event_width / 2.0 - text_padding), int(text_y - 3 * scale_factor),
                int(start_x + event_width / 2.0 + text_padding), int(text_y + 28 * scale_factor)
            ], fill='white', outline=color, width=int(2 * scale_factor))
            
            draw.text((int(start_x - event_width / 2.0), int(text_y)), event_text, fill=color, font=font_large)
            
            # Draw elegant curved connection line
            draw_ultra_smooth_curve(draw, connection_start, connection_end, 'gray', 2 * scale_factor, 0.4)
    
    # Add elegant title with styling
    point_events = len([e for e in parsed_events if not e['end_date']])
    duration_events = len([e for e in parsed_events if e['end_date']])
    title = f"Timeline: {point_events} Events, {duration_events} Duration Events"
    
    try:
        title_bbox = get_text_dimensions(draw, title, font_title)
        title_width = float(title_bbox[0])
    except:
        title_width = float(len(title) * 20 * scale_factor)
    
    # Title with elegant shadow
    shadow_offset = int(4 * scale_factor)
    draw.text((int(width / 2.0 - title_width / 2.0 + shadow_offset), int(40 * scale_factor + shadow_offset)), 
             title, fill=(180, 180, 180), font=font_title)
    draw.text((int(width / 2.0 - title_width / 2.0), int(40 * scale_factor)), title, fill='black', font=font_title)
    
    # Scale down for final output while maintaining quality
    final_width = width // scale_factor
    final_height = height // scale_factor
    img = img.resize((final_width, final_height), Image.LANCZOS)
    
    # Apply subtle blur for softer appearance
    img = img.filter(ImageFilter.SMOOTH_MORE)
    
    return img

@app.route('/')
def index():
    """Serve the main timeline creator page."""
    return render_template('index.html')

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    """Handle CSV file upload and parse timeline data."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.csv'):
            return jsonify({'error': 'File must be a CSV file'}), 400
        
        # Read CSV data
        csv_data = file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_data))
        
        events = []
        for row_num, row in enumerate(csv_reader, 1):
            try:
                # Required fields
                if 'date' not in row or 'event' not in row:
                    return jsonify({'error': f'Row {row_num}: Missing required columns "date" and "event"'}), 400
                
                event = {
                    'date': row['date'].strip(),
                    'event': row['event'].strip()
                }
                
                # Validate date format
                try:
                    datetime.strptime(event['date'], '%Y-%m-%d')
                except ValueError:
                    return jsonify({'error': f'Row {row_num}: Invalid date format. Use YYYY-MM-DD'}), 400
                
                # Optional fields
                if 'end_date' in row and row['end_date'].strip():
                    end_date = row['end_date'].strip()
                    try:
                        datetime.strptime(end_date, '%Y-%m-%d')
                        event['end_date'] = end_date
                    except ValueError:
                        return jsonify({'error': f'Row {row_num}: Invalid end_date format. Use YYYY-MM-DD'}), 400
                
                if 'color' in row and row['color'].strip():
                    color = row['color'].strip()
                    if not color.startswith('#'):
                        color = '#' + color
                    if len(color) != 7:
                        return jsonify({'error': f'Row {row_num}: Invalid color format. Use #RRGGBB'}), 400
                    event['color'] = color
                else:
                    event['color'] = '#dc3545'  # Default red
                
                events.append(event)
                
            except Exception as e:
                return jsonify({'error': f'Row {row_num}: {str(e)}'}), 400
        
        if not events:
            return jsonify({'error': 'No valid events found in CSV file'}), 400
        
        return jsonify({
            'success': True,
            'events': events,
            'message': f'Successfully imported {len(events)} events'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to process CSV file: {str(e)}'}), 500

@app.route('/generate_timeline', methods=['POST'])
def generate_timeline():
    """Generate and return a timeline image."""
    try:
        data = request.json
        events = data.get('events', [])
        
        if not events:
            return jsonify({'error': 'No events provided'}), 400
        
        # Validate events
        for event in events:
            if 'date' not in event or 'event' not in event:
                return jsonify({'error': 'Each event must have date and event fields'}), 400
            try:
                datetime.strptime(event['date'], '%Y-%m-%d')
                if event.get('end_date'):
                    datetime.strptime(event['end_date'], '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Generate timeline image
        img = create_timeline_image(events)
        if img is None:
            return jsonify({'error': 'Failed to generate timeline'}), 500
        
        # Convert image to base64
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG', quality=95, optimize=True)
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{img_base64}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 