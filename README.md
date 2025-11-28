# Veo 3.1 Video Generator

A full-stack web application for generating high-quality videos using Google's Veo 3.1 model via the Gemini API.

![Frontend Interface](https://github.com/Ker102/Videogenerator/raw/main/.github/screenshot.png)

## Features

- **Text-to-Video**: Generate videos from text prompts with audio
- **Image-to-Video**: Animate static images
- **Reference Images**: Use up to 3 images to guide style and character appearance (Veo 3.1 only)
- **Video Extension**: Extend Veo-generated videos by 7 seconds (up to 20 times)
- **Smart Constraints**: UI automatically enforces API limitations with visual feedback
- **Real-time Status**: Live progress updates during generation

## Tech Stack

- **Backend**: Python FastAPI with `google-genai` SDK
- **Frontend**: React (Vite) with modern dark theme UI
- **Model**: Google Veo 3.1 (`veo-3.1-generate-preview`)

## Prerequisites

- Python 3.8+
- Node.js 16+
- Google Gemini API Key ([Get one here](https://aistudio.google.com/apikey))

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Ker102/Videogenerator.git
cd Videogenerator
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Create .env file and add your API key
cp .env.example .env
# Edit .env and add: GEMINI_API_KEY=your_api_key_here

# Start the backend server
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install

# Start the development server
npm run dev
```

### 4. Open the Application
Navigate to `http://localhost:5173` in your browser.

## Configuration Options

### Resolution
- **720p** (default) - Supports all aspect ratios and durations
- **1080p** - Requires 8-second duration

### Aspect Ratio
- **16:9** (Landscape)
- **9:16** (Portrait)

### Duration
- **4 seconds**
- **6 seconds**
- **8 seconds** (required for 1080p and reference images)

### Person Generation
Automatically configured based on generation mode:
- Text-to-video & Extension: `allow_all`
- Image-to-video & Reference images: `allow_adult`

## API Constraints

The UI automatically enforces these constraints:
- 1080p videos must be 8 seconds
- Reference images require 16:9 aspect ratio and 8 seconds
- Video extensions require 720p and 8 seconds

## Project Structure

```
Videogenerator/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Environment template
│   ├── uploads/             # Temporary uploads (gitignored)
│   └── generated/           # Generated videos (gitignored)
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   ├── api.js           # API service
│   │   └── index.css        # Styles
│   ├── package.json
│   └── node_modules/        # (gitignored)
├── CLAUDE.md                # AI agent context
└── README.md
```

## API Endpoints

### `POST /generate`
Start video generation
- **Form Data**: `prompt`, `model`, `aspect_ratio`, `resolution`, `duration_seconds`, `negative_prompt` (optional), `image` (optional), `reference_images` (optional), `video` (optional)
- **Returns**: `{"operation_name": "...", "status": "processing"}`

### `GET /status/{operation_name}`
Check generation status
- **Returns**: `{"status": "processing|done|error", "video_url": "..."}`

### `GET /videos/{filename}`
Download generated video

## Common Issues

### Video Upload Error
If you see `Files.upload() got an unexpected keyword argument 'path'`, ensure you're using the latest version from the repository. This was fixed by changing from `path=` to `file=bytes` parameter.

### API Key Not Found
Make sure `.env` file exists in `/backend` with your actual API key:
```
GEMINI_API_KEY=your_actual_key_here
```

### Video Extension Fails
- Only works with Veo-generated videos (not arbitrary videos)
- Requires 720p resolution and 8s duration
- Input video must be ≤141 seconds

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

## Credits

- Built with [Google Gemini API](https://ai.google.dev/)
- Powered by [Veo 3.1](https://deepmind.google/models/veo/)

## Support

For issues and questions, please open an issue on GitHub.

---

**Note**: This is an educational project. Generated videos are subject to Google's usage policies and quotas.
