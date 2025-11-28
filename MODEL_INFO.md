## Model Information

The application is configured to use **`veo-3.1-generate-preview`**, which is the **standard Veo 3.1 model** (NOT Veo 3.1 Fast).

### Available Models
- **veo-3.1-generate-preview**: Standard Veo 3.1 - High-quality video generation (what we use)
- **Veo 3.1 Fast**: Faster variant optimized for speed and price (not used)

### Why We Use Standard Veo 3.1
The standard Veo 3.1 model provides:
- Higher quality video output
- Better cinematic control
- Enhanced audio generation
- Better character consistency
- Improved prompt adherence

While Veo 3.1 Fast is available for rapid development and lower costs, this application prioritizes quality over speed.

### Verifying the Model
You can see the model being used in:
1. **Backend**: `backend/main.py` line 59 - `model: str = Form("veo-3.1-generate-preview")`
2. **Frontend**: The UI displays "Using: Veo 3.1 (High-Quality Mode)"
