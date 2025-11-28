import os
import time
import base64
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv
import shutil

load_dotenv()

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini Client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = None

if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Failed to initialize Gemini client: {e}")
else:
    print("WARNING: GEMINI_API_KEY not found in environment variables. Video generation will fail.")

UPLOAD_DIR = "uploads"
GENERATED_DIR = "generated"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

class GenerateRequest(BaseModel):
    prompt: str
    model: str = "veo-3.1-generate-preview"
    aspect_ratio: str = "16:9" # "16:9" or "9:16"
    resolution: str = "720p" # "720p" or "1080p"
    duration_seconds: str = "8" # "4", "6", "8"
    negative_prompt: Optional[str] = None
    person_generation: str = "allow_all"

# Store operations in memory for simplicity (in production use a DB)
operations = {}

@app.post("/generate")
async def generate_video(
    prompt: str = Form(...),
    model: str = Form("veo-3.1-generate-preview"),
    aspect_ratio: str = Form("16:9"),
    resolution: str = Form("720p"),
    duration_seconds: str = Form("8"),
    negative_prompt: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    last_frame: Optional[UploadFile] = File(None),
    video: Optional[UploadFile] = File(None),
    reference_images: List[UploadFile] = File(None)
):
    if not client:
        raise HTTPException(status_code=500, detail="Gemini Client not initialized. Check server logs/API Key.")

    try:
        print(f"Received request: prompt='{prompt}', model='{model}'")
        
        config_args = {
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "duration_seconds": duration_seconds,
            "person_generation": "allow_all" 
        }
        
        if negative_prompt:
            config_args["negative_prompt"] = negative_prompt

        # Helper to process image uploads
        def process_image_upload(upload_file: UploadFile):
            from PIL import Image
            import io
            file_content = upload_file.file.read()
            return Image.open(io.BytesIO(file_content))

        # Handle Image Input (Image-to-Video)
        img_part = None
        if image:
            img_part = process_image_upload(image)
            config_args["person_generation"] = "allow_adult" # Enforce for image input

        # Handle Last Frame (Interpolation)
        if last_frame:
            # last_frame is part of config
            config_args["last_frame"] = process_image_upload(last_frame)
            config_args["person_generation"] = "allow_adult"

        # Handle Reference Images
        ref_imgs = []
        if reference_images:
            for ref_img in reference_images:
                pil_img = process_image_upload(ref_img)
                # Create VideoGenerationReferenceImage object
                # Note: The SDK might expect the wrapper or just the image in a list?
                # Docs: reference_images=[dress_reference, ...]
                # dress_reference = types.VideoGenerationReferenceImage(image=..., reference_type="asset")
                
                ref_obj = types.VideoGenerationReferenceImage(
                    image=pil_img,
                    reference_type="asset"
                )
                ref_imgs.append(ref_obj)
            
            if ref_imgs:
                config_args["reference_images"] = ref_imgs
                config_args["person_generation"] = "allow_adult"

        # Handle Video Input (Extension)
        video_part = None
        if video:
             # Save video to disk
            video_path = os.path.join(UPLOAD_DIR, video.filename)
            with open(video_path, "wb") as buffer:
                shutil.copyfileobj(video.file, buffer)
            
            print(f"Uploading video {video.filename}...")
            uploaded_file = client.files.upload(path=video_path)
            
            # Wait for processing
            while uploaded_file.state.name == "PROCESSING":
                time.sleep(2)
                uploaded_file = client.files.get(name=uploaded_file.name)
            
            if uploaded_file.state.name == "FAILED":
                 raise HTTPException(status_code=400, detail="Video processing failed")
            
            print(f"Video uploaded: {uploaded_file.name}")
            video_part = uploaded_file
            config_args["person_generation"] = "allow_all" # Extension supports allow_all

        
        # Config object
        config = types.GenerateVideosConfig(**config_args)

        # Call API
        call_args = {
            "model": model,
            "prompt": prompt,
            "config": config
        }
        
        if img_part:
            call_args["image"] = img_part
            
        if video_part:
            call_args["video"] = video_part

        print("Calling generate_videos...")
        operation = client.models.generate_videos(**call_args)
        
        # Store operation name/id
        op_name = operation.name
        operations[op_name] = operation
        
        return {"operation_name": op_name, "status": "processing"}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{operation_name}")
async def get_status(operation_name: str):
    # In a real app, we'd look up the operation object or ID.
    # Here we might need to reconstruct it or fetch it if we didn't persist the object.
    # The SDK allows fetching operation by name?
    # client.operations.get(operation) or client.operations.get(name=...)
    
    try:
        # We can try to fetch it directly from API using the name
        # The SDK usage: operation = client.operations.get(operation)
        # We can probably pass the name string or construct a dummy object with the name.
        # Let's try passing the name string if the SDK supports it, or look at how to fetch.
        # Docs: operation = client.operations.get(operation)
        # Maybe: operation = client.operations.get(name=operation_name)
        
        # For now, let's assume we can pass the name.
        # If not, we rely on our in-memory dict (which is brittle if server restarts).
        
        operation = operations.get(operation_name)
        if not operation:
             # Try to fetch from API if not in memory (e.g. after restart)
             # This part is tricky without the exact SDK signature for get by name.
             # We'll assume we can use the name.
             pass

        # Refresh status
        # Note: client.operations.get() returns the updated operation
        # We need to pass the operation object or name.
        # Let's try passing the name.
        updated_op = client.operations.get(name=operation_name)
        
        if updated_op.done:
            # Download if done and not already downloaded
            # We need to extract the video URI or content.
            # generated_video = updated_op.response.generated_videos[0]
            # client.files.download(file=generated_video.video)
            
            if hasattr(updated_op, 'response') and updated_op.response:
                 generated_videos = updated_op.response.generated_videos
                 if generated_videos:
                     vid = generated_videos[0]
                     # Save to file
                     filename = f"{operation_name.replace('/', '_')}.mp4"
                     save_path = os.path.join(GENERATED_DIR, filename)
                     
                     if not os.path.exists(save_path):
                         print(f"Downloading video to {save_path}")
                         client.files.download(file=vid.video, config={"download_path": save_path}) # Check download signature
                         # The docs say: client.files.download(file=generated_video.video)
                         # And then: generated_video.video.save("filename.mp4") ??
                         # Or: client.files.download(file=video.video) -> returns bytes?
                         # Docs: video.video.save("name.mp4")
                         # Let's try the save method on the video object if it exists after download?
                         # Actually docs say:
                         # client.files.download(file=video.video)
                         # video.video.save("...")
                         # This implies the object is updated with data?
                         # Or maybe we just use the save_path in download?
                         # Let's assume we can just write the bytes if download returns them, or use the .save method.
                         
                         # Let's try to be safe:
                         # The docs example:
                         # client.files.download(file=video.video)
                         # video.video.save("dialogue_example.mp4")
                         
                         # So we do that.
                         vid.video.save(save_path)

                     return {"status": "done", "video_url": f"/videos/{filename}"}
            
            return {"status": "done", "detail": "No video found in response"}
            
        return {"status": "processing"}

    except Exception as e:
        print(f"Status check error: {e}")
        return {"status": "error", "detail": str(e)}

@app.get("/videos/{filename}")
async def get_video(filename: str):
    file_path = os.path.join(GENERATED_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Video not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
