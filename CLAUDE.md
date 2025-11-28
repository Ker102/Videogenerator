# Veo 3.1 Video Generator - AI Agent Context

## Project Overview
This is a full-stack web application for generating videos using Google's Veo 3.1 model via the Gemini API.

**Tech Stack:**
- **Backend:** Python FastAPI with `google-genai` SDK
- **Frontend:** React (Vite)
- **Video Model:** Google Veo 3.1 (veo-3.1-generate-preview)

## Project Structure
```
/backend
  - main.py              # FastAPI server with Gemini integration
  - requirements.txt     # Python dependencies
  - .env                 # API key (GEMINI_API_KEY) - GITIGNORED
  - .env.example         # Template for .env
  - uploads/             # Temporary uploaded files - GITIGNORED
  - generated/           # Generated video outputs - GITIGNORED

/frontend
  - src/
    - App.jsx            # Main React component with UI
    - api.js             # API service layer
    - index.css          # Styling with dark theme
  - node_modules/        # GITIGNORED
```

## Features Implemented

### Video Generation Modes
1. **Text-to-Video**: Generate video from text prompt only
2. **Image-to-Video**: Animate a single image
3. **Reference Images**: Use up to 3 images to guide style/character (Veo 3.1 only)
4. **Video Extension**: Extend a Veo-generated video by 7 seconds (up to 20 times)

### API Constraints (Auto-enforced in UI)
- **Resolution Options:** 720p, 1080p
  - 1080p requires 8-second duration
  - Video extension only supports 720p
- **Aspect Ratios:** 16:9, 9:16
  - Reference images require 16:9
- **Duration Options:** 4s, 6s, 8s
  - 1080p, video extension, and reference images all require 8s
- **Person Generation:**
  - Text-to-video & Extension: "allow_all"
  - Image-to-video, Interpolation, Reference images: "allow_adult"

## Running the Application

### Backend
```bash
cd backend
pip install -r requirements.txt
# Add GEMINI_API_KEY to .env file
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# Opens on http://localhost:5173
```

## Key Implementation Details

### Backend (main.py)
- **File Upload:** Uses `client.files.upload(file=bytes, mime_type="video/mp4")` for video extension
- **Async Operations:** Video generation returns an operation name; status is polled via `/status/{operation_name}`
- **Image Processing:** Uses PIL to convert uploaded images to the format expected by the SDK
- **Reference Images:** Wrapped in `types.VideoGenerationReferenceImage(image=pil_img, reference_type="asset")`

### Frontend (App.jsx)
- **Constraint Enforcement:** `useEffect` hook automatically adjusts settings based on API requirements
- **File Handling:** Multiple file inputs with validation (e.g., max 3 reference images)
- **Status Polling:** Polls backend every 5 seconds until video generation completes
- **UI Feedback:** Displays constraint messages in orange when options are auto-locked

## Common Issues & Solutions

### 1. "Files.upload() got unexpected keyword argument 'path'"
**Fix:** Use `file=bytes` instead of `path=filepath`
```python
# ❌ Wrong
uploaded_file = client.files.upload(path=video_path)

# ✅ Correct
with open(video_path, 'rb') as f:
    video_bytes = f.read()
uploaded_file = client.files.upload(file=video_bytes, mime_type="video/mp4")
```

### 2. API Key Not Found
Ensure `.env` file exists in `/backend` with:
```
GEMINI_API_KEY=your_actual_key_here
```

### 3. Video Extension Fails
- Only works with Veo-generated videos
- Requires 720p resolution and 8s duration
- Input video must be ≤141 seconds

## API Endpoints

### POST /generate
Starts video generation. Returns operation_name.
**Form Fields:**
- `prompt` (required)
- `model` (default: "veo-3.1-generate-preview")
- `aspect_ratio` (16:9 or 9:16)
- `resolution` (720p or 1080p)
- `duration_seconds` (4, 6, or 8)
- `negative_prompt` (optional)
- `image` (file, optional)
- `reference_images` (files, optional, max 3)
- `video` (file, optional - for extension)

### GET /status/{operation_name}
Polls generation status. Returns:
- `{"status": "processing"}` - Still generating
- `{"status": "done", "video_url": "/videos/{filename}"}` - Complete
- `{"status": "error", "detail": "..."}` - Failed

### GET /videos/{filename}
Serves generated video file.

## Git Repository
- **Remote:** https://github.com/Ker102/Videogenerator.git
- **Branch:** main
- **Important:** `.env` and sensitive files are gitignored

## Recent Changes
1. Added reference images support (up to 3)
2. Implemented UI constraint enforcement
3. Fixed video upload API (file= instead of path=)
4. Added comprehensive .gitignore
5. Created .env.example template

## Next Steps / Future Enhancements
- Add "Last Frame" input for interpolation videos
- Implement operation history/database instead of in-memory storage
- Add progress indicators beyond polling
- Support for multiple video formats
- Batch video generation
