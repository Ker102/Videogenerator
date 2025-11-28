import { useState, useEffect } from 'react';
import { generateVideo, getStatus, getVideoUrl } from './api';
import './App.css'; // We'll use App.css or index.css

function App() {
  const [prompt, setPrompt] = useState('');
  const [negativePrompt, setNegativePrompt] = useState('');
  const [aspectRatio, setAspectRatio] = useState('16:9');
  const [resolution, setResolution] = useState('720p');
  const [duration, setDuration] = useState('8');
  const [imageFile, setImageFile] = useState(null);
  const [referenceImages, setReferenceImages] = useState([]);
  const [videoFile, setVideoFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');
  const [generatedVideo, setGeneratedVideo] = useState(null);
  const [error, setError] = useState(null);

  // Enforce Constraints
  useEffect(() => {
    // 1. 1080p requires 8s
    if (resolution === '1080p' && duration !== '8') {
      setDuration('8');
    }

    // 2. Extension requires 720p and 8s
    if (videoFile) {
      if (resolution !== '720p') setResolution('720p');
      if (duration !== '8') setDuration('8');
    }

    // 3. Reference Images require 8s and 16:9
    if (referenceImages.length > 0) {
      if (duration !== '8') setDuration('8');
      if (aspectRatio !== '16:9') setAspectRatio('16:9');
    }

    // 4. Interpolation (Last Frame - not yet implemented in UI but good to know)
    // We haven't added lastFrame input yet, but if we do, it needs 8s.

  }, [resolution, duration, videoFile, referenceImages, aspectRatio]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus('Starting generation...');
    setError(null);
    setGeneratedVideo(null);

    const formData = new FormData();
    formData.append('prompt', prompt);
    formData.append('aspect_ratio', aspectRatio);
    formData.append('resolution', resolution);
    formData.append('duration_seconds', duration);
    if (negativePrompt) formData.append('negative_prompt', negativePrompt);
    if (imageFile) formData.append('image', imageFile);
    if (referenceImages.length > 0) {
      referenceImages.forEach((file) => {
        formData.append('reference_images', file);
      });
    }
    if (videoFile) formData.append('video', videoFile);

    try {
      const { operation_name } = await generateVideo(formData);
      setStatus('Processing...');
      pollStatus(operation_name);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to start generation');
      setLoading(false);
    }
  };

  const pollStatus = async (operationName) => {
    const interval = setInterval(async () => {
      try {
        const res = await getStatus(operationName);
        if (res.status === 'done') {
          clearInterval(interval);
          setLoading(false);
          setStatus('Done!');
          if (res.video_url) {
            setGeneratedVideo(getVideoUrl(res.video_url));
          } else {
            setError('Generation done but no video URL returned.');
          }
        } else if (res.status === 'error') {
          clearInterval(interval);
          setLoading(false);
          setError(res.detail || 'Unknown error during processing');
        } else {
          setStatus('Generating... this may take a minute.');
        }
      } catch (err) {
        console.error(err);
        // Don't stop polling immediately on network error, maybe retry?
        // For now, we stop to avoid infinite loops if server dies.
        clearInterval(interval);
        setLoading(false);
        setError('Error polling status');
      }
    }, 5000);
  };

  return (
    <div className="container">
      <header>
        <h1>Veo Video Generator</h1>
        <p>Create stunning videos with Google's Veo 3.1 model</p>
      </header>

      <main>
        <div className="panel input-panel">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Prompt</label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe your video..."
                required
                rows={4}
              />
            </div>

            <div className="form-group">
              <label>Negative Prompt (Optional)</label>
              <input
                type="text"
                value={negativePrompt}
                onChange={(e) => setNegativePrompt(e.target.value)}
                placeholder="What to avoid..."
              />
            </div>

            <div className="settings-grid">
              <div className="form-group">
                <label>Aspect Ratio</label>
                <select
                  value={aspectRatio}
                  onChange={(e) => setAspectRatio(e.target.value)}
                  disabled={referenceImages.length > 0}
                >
                  <option value="16:9">16:9 (Landscape)</option>
                  <option value="9:16">9:16 (Portrait)</option>
                </select>
                {referenceImages.length > 0 && <small className="constraint-text">Reference images require 16:9</small>}
              </div>

              <div className="form-group">
                <label>Resolution</label>
                <select
                  value={resolution}
                  onChange={(e) => setResolution(e.target.value)}
                  disabled={!!videoFile}
                >
                  <option value="720p">720p</option>
                  <option value="1080p">1080p</option>
                </select>
                {videoFile && <small className="constraint-text">Extensions must be 720p</small>}
              </div>

              <div className="form-group">
                <label>Duration</label>
                <select
                  value={duration}
                  onChange={(e) => setDuration(e.target.value)}
                  disabled={resolution === '1080p' || !!videoFile || referenceImages.length > 0}
                >
                  <option value="4">4 seconds</option>
                  <option value="6">6 seconds</option>
                  <option value="8">8 seconds</option>
                </select>
                {(resolution === '1080p' || !!videoFile || referenceImages.length > 0) && <small className="constraint-text">This configuration requires 8s</small>}
              </div>
            </div>

            <div className="file-inputs">
              <div className="form-group">
                <label>Initial Image (Optional)</label>
                <input type="file" accept="image/*" onChange={(e) => setImageFile(e.target.files[0])} />
                <small>For Image-to-Video generation</small>
              </div>

              <div className="form-group">
                <label>Reference Images (Optional, max 3)</label>
                <input
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={(e) => {
                    const files = Array.from(e.target.files);
                    if (files.length > 3) {
                      alert("You can only select up to 3 reference images.");
                      e.target.value = ""; // Clear input
                      setReferenceImages([]);
                    } else {
                      setReferenceImages(files);
                    }
                  }}
                />
                <small>Style/Character reference (Veo 3.1 only)</small>
              </div>

              <div className="form-group">
                <label>Input Video (Optional)</label>
                <input type="file" accept="video/*" onChange={(e) => setVideoFile(e.target.files[0])} />
                <small>For Video Extension</small>
              </div>
            </div>

            <button type="submit" disabled={loading} className="generate-btn">
              {loading ? 'Generating...' : 'Generate Video'}
            </button>
          </form>

          {status && <div className="status-message">{status}</div>}
          {error && <div className="error-message">{error}</div>}
        </div>

        <div className="panel preview-panel">
          {generatedVideo ? (
            <div className="video-wrapper">
              <video src={generatedVideo} controls autoPlay loop />
              <a href={generatedVideo} download className="download-link">Download Video</a>
            </div>
          ) : (
            <div className="placeholder">
              <div className="placeholder-icon">🎬</div>
              <p>Your generated video will appear here</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
