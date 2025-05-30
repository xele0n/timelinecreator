# Timeline Creator Web Service

A beautiful web application that generates visual timeline images from user-provided events and dates with advanced features including CSV import, custom colors, and duration events.

## Features

- 🎨 **Beautiful UI**: Modern, responsive design with gradient backgrounds and smooth animations
- 📅 **Easy Event Input**: Simple form to add events with dates and descriptions
- 🔄 **Dynamic Timeline Generation**: Real-time timeline image creation using Python PIL
- ✅ **Event Management**: Add, remove, edit, and view events before generating the timeline
- 📁 **CSV Import**: Bulk import events from CSV files with drag-and-drop support
- 🎯 **Custom Colors**: Assign custom colors to each event for better visualization
- ⏱️ **Duration Events**: Support for events with start and end dates displayed as parallel lines
- 📱 **Mobile Friendly**: Responsive design that works on all devices
- 🖼️ **High-Quality Output**: Generated timeline images with proper spacing and visual hierarchy

## How It Works

### Manual Entry
1. **Add Events**: Enter start date, optional end date, event description, and choose a color
2. **Manage Events**: View all added events with color indicators, edit or remove any event
3. **Generate Timeline**: Click the generate button to create a visual timeline image
4. **View Result**: The timeline image displays events chronologically with custom colors

### CSV Import
1. **Prepare CSV**: Create a CSV file with required columns (date, event) and optional columns (end_date, color)
2. **Upload File**: Drag and drop or click to upload your CSV file
3. **Auto Import**: Events are automatically validated and added to your timeline
4. **Generate**: Create your timeline with all imported events

## Event Types

### Point Events
- Single date events displayed as circles on the timeline
- Event descriptions alternate above and below for clarity
- Custom colors for each event

### Duration Events
- Events with start and end dates
- Displayed as parallel lines that branch from the main timeline
- Perfect for showing project phases, periods, or ongoing activities
- Custom colors and clear date range indicators

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Setup

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

### Adding Events Manually

1. **Select Input Method**: Choose "Manual Entry" tab
2. **Fill Event Details**:
   - Start Date (required)
   - End Date (optional, for duration events)
   - Event Description (required)
   - Color (click color picker to choose)
3. **Add Event**: Click "Add Event" or press Enter
4. **Repeat** for all events you want to include

### Importing from CSV

1. **Select Import Method**: Choose "CSV Import" tab
2. **Prepare CSV File** with the following format:
   ```csv
   date,event,end_date,color
   2024-01-15,Project Start,,#28a745
   2024-02-01,Development Phase,2024-04-30,#007bff
   2024-05-01,Project Launch,,#dc3545
   ```
3. **Upload File**: Drag and drop or click to select your CSV file
4. **Automatic Import**: Events are validated and added to your timeline

### CSV Format Requirements

**Required Columns:**
- `date`: Start date in YYYY-MM-DD format
- `event`: Event description

**Optional Columns:**
- `end_date`: End date in YYYY-MM-DD format (for duration events)
- `color`: Hex color code (e.g., #28a745 or 28a745)

### Managing Events

- **Edit Events**: Click the "Edit" button on any event to modify its details
- **Remove Events**: Click the "Remove" button to delete individual events
- **Clear All**: Use the "Clear All" button to remove all events at once
- **Visual Indicators**: Color dots show each event's assigned color
- **Duration Indicators**: Green border indicates duration events

### Generating Timeline

1. After adding events, the "Generate Timeline" button becomes active
2. Click the button to create your timeline image
3. The timeline shows:
   - **Point events**: As circles with connecting lines to descriptions
   - **Duration events**: As parallel lines showing the time span
   - **Custom colors**: Each event uses its assigned color
   - **Chronological order**: Events are automatically sorted by date
4. **Professional output**: Clean styling suitable for presentations

## Timeline Features

### Visual Elements
- **Main Timeline**: Horizontal black line as the time axis
- **Point Events**: Colored circles with vertical markers
- **Duration Events**: Branching parallel lines with start/end markers
- **Event Text**: Alternating placement above/below for readability
- **Date Labels**: Clear date formatting for reference
- **Color Coding**: Custom colors for event categorization

### Layout Intelligence
- **Smart Positioning**: Events are positioned proportionally by date
- **Overlap Prevention**: Duration events automatically adjust vertical positioning
- **Text Backgrounds**: White backgrounds ensure text readability
- **Professional Typography**: Clean fonts and proper spacing

## API Endpoints

### GET `/`
Returns the main timeline creator interface.

### POST `/upload_csv`
Handles CSV file upload and validation.

**Request**: Multipart form data with CSV file
**Response**:
```json
{
  "success": true,
  "events": [...],
  "message": "Successfully imported 5 events"
}
```

### POST `/generate_timeline`
Generates a timeline image from provided events.

**Request Body**:
```json
{
  "events": [
    {
      "date": "2024-01-15",
      "event": "Project Started",
      "color": "#28a745"
    },
    {
      "date": "2024-02-01",
      "end_date": "2024-04-30",
      "event": "Development Phase",
      "color": "#007bff"
    }
  ]
}
```

**Response**:
```json
{
  "success": true,
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```

## Technical Details

### Backend (Python/Flask)
- **Flask**: Web framework for handling HTTP requests
- **PIL (Pillow)**: Advanced image generation and manipulation
- **CSV Processing**: Built-in CSV parsing with validation
- **Base64 encoding**: Efficient image transfer to frontend
- **Color Management**: Hex to RGB conversion for image rendering

### Frontend (HTML/CSS/JavaScript)
- **Vanilla JavaScript**: No external dependencies
- **Tabbed Interface**: Clean separation of manual entry and CSV import
- **Drag & Drop**: Modern file upload experience
- **Modal Dialogs**: Intuitive event editing interface
- **Responsive Design**: CSS Grid/Flexbox for all screen sizes
- **Color Pickers**: Native HTML5 color input support

### Image Generation Process
1. **Data Parsing**: Validate and parse event data with dates and colors
2. **Temporal Analysis**: Calculate date ranges and optimal positioning
3. **Layout Calculation**: Determine event placement and avoid overlaps
4. **Rendering**: Draw timeline, events, markers, and text with custom colors
5. **Export**: Convert to PNG and encode as base64

## File Structure

```
timeline-creator/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Frontend interface
├── requirements.txt      # Python dependencies
├── sample_timeline.csv   # Example CSV file
├── README.md            # This file
└── LICENSE              # MIT License
```

## Customization

### Timeline Styling
Modify the `create_timeline_image()` function in `app.py` to customize:
- **Image dimensions**: Width, height, margins
- **Colors and fonts**: Timeline colors, text styling
- **Marker styles**: Circle sizes, line widths
- **Text positioning**: Spacing, backgrounds
- **Duration event appearance**: Branch heights, line styles

### UI Appearance
Edit `templates/index.html` to modify:
- **Color schemes**: CSS variables and gradients
- **Layout and spacing**: Container sizes, margins
- **Typography**: Font families and sizes
- **Animations and effects**: Transitions and hover states
- **Form styling**: Input appearance and validation

## Sample Data

Use the included `sample_timeline.csv` file to test the CSV import feature:
- Contains a mix of point and duration events
- Demonstrates different colors and date ranges
- Perfect for testing the timeline generation

## Browser Compatibility

- ✅ Chrome (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ❌ Internet Explorer (not supported)

## Troubleshooting

### Common Issues

1. **CSV Upload Errors**:
   - Ensure your CSV has required columns: `date`, `event`
   - Use YYYY-MM-DD date format
   - Check for special characters in event descriptions
   - Verify color codes are valid hex values

2. **Font Warnings**: The application falls back to default fonts if system fonts aren't available

3. **Port Conflicts**: Change the port in `app.py` from 5000 to another number

4. **File Size Limits**: CSV files are limited to 16MB maximum

5. **Date Validation**: End dates must be after start dates for duration events

### Development Mode

To run with auto-reload and debug information:
```bash
export FLASK_ENV=development  # Linux/Mac
set FLASK_ENV=development     # Windows
python app.py
```

## Advanced Features

### Color Management
- **Color Picker**: Native HTML5 color input for precise color selection
- **Default Colors**: Smart defaults for quick event creation
- **Visual Indicators**: Color dots in event list for easy identification
- **Timeline Integration**: Colors carry through to generated timeline

### Duration Events
- **Parallel Lines**: Visual representation of time spans
- **Smart Positioning**: Automatic vertical offset to prevent overlaps
- **Date Range Display**: Clear start and end date labeling
- **Color Consistency**: Custom colors applied to entire duration representation

### CSV Import Features
- **Drag & Drop**: Modern file upload interface
- **Real-time Validation**: Immediate feedback on data quality
- **Bulk Import**: Process hundreds of events at once
- **Format Flexibility**: Optional columns for maximum compatibility
- **Error Reporting**: Detailed validation messages with row numbers

## Future Enhancements

- [ ] Export timelines as PNG, PDF, or SVG files
- [ ] Timeline templates for common use cases
- [ ] Event categories with automatic color coding
- [ ] Collaborative timeline editing and sharing
- [ ] Integration with calendar applications
- [ ] Multiple timeline views (horizontal/vertical)
- [ ] Advanced styling options and themes
- [ ] Interactive timeline exploration
- [ ] Data export to various formats
- [ ] Real-time collaboration features

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes with tests
4. Update documentation as needed
5. Submit a pull request with detailed description

## Support

For issues, questions, or feature requests:
- Create an issue in this repository
- Provide detailed information about your problem
- Include sample data or screenshots if applicable
- Specify your browser and operating system 