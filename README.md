# AI Generation Studio

An AI-powered image and video generation application that transforms text prompts into visual content using Stable Diffusion and Wan 2.1.

## Overview

AI Generation Studio provides a single interface for generating AI images and short videos. It uses a Streamlit frontend and a FastAPI backend, with model inference designed to run on a CUDA-enabled GPU server.

**Current status:** Local frontend and backend setup completed. GPU-based image and video generation still requires testing on the target GPU server.

## Features

- **Text-to-Image:** Generate images from text prompts using Stable Diffusion 1.5.
- **Text-to-Video:** Generate video clips using Wan 2.1 T2V-1.3B.
- **Prompt Controls:** Configure prompts, negative prompts, inference steps, guidance scale and seed.
- **Video Export:** Export generated clips as MP4.
- **Video Stitching:** Combine generated clips using FFmpeg.
- **Media Preview:** Preview generated images and videos in the frontend.
- **Download Support:** Download generated PNG and MP4 files.
- **GPU Health Check:** Check CUDA availability and the detected GPU.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI |
| Image Model | Stable Diffusion 1.5 |
| Video Model | Wan 2.1 T2V-1.3B |
| Deep Learning | PyTorch |
| Model Inference | Hugging Face Diffusers |
| Validation | Pydantic |
| Video Processing | FFmpeg |
| API Server | Uvicorn |

## Project Structure

```text
AI-Generation-Demo/
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── app.py
│   └── requirements.txt
├── outputs/
├── README.md
└── .gitignore
```

Generated images and videos are saved in the `outputs/` directory.

## Requirements

- Python 3.10 or a compatible Python version
- pip
- CUDA-enabled NVIDIA GPU for generation
- Sufficient GPU VRAM and system RAM for the selected models
- Internet access for the initial model download
- FFmpeg for video stitching

## Local Setup

### 1. Clone or open the project

Open a terminal in the project root directory.

### 2. Install backend dependencies

```bash
cd backend
python -m pip install -r requirements.txt
```

### 3. Start the FastAPI backend

Run from inside the `backend/` directory:

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### 4. Verify the API

Open these URLs in your browser:

- API health: http://127.0.0.1:8000/health
- Interactive API documentation: http://127.0.0.1:8000/docs

The health endpoint reports whether CUDA is available and identifies the configured models.

### 5. Install frontend dependencies

Open a second terminal:

```bash
cd frontend
python -m pip install -r requirements.txt
```

### 6. Start the frontend

```bash
python -m streamlit run app.py
```

Open the local URL printed in the terminal, normally:

http://localhost:8501

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check API and GPU status |
| POST | `/api/generate/image` | Generate an image |
| POST | `/api/generate/video` | Generate a video |
| GET | `/outputs/{filename}` | Access generated media |

## Model Configuration

The backend supports environment-variable configuration:

```text
IMAGE_MODEL_ID=runwayml/stable-diffusion-v1-5
VIDEO_MODEL_ID=Wan-AI/Wan2.1-T2V-1.3B-Diffusers
```

The model weights are not included in the project. They are downloaded from the model repository when the corresponding pipeline is first loaded.

## Video Generation

The video pipeline uses Wan 2.1 T2V-1.3B to generate short clips. FFmpeg can combine generated clips into a single MP4 file.

Important considerations:

- The current implementation defaults to a requested duration of 10 seconds.
- The final duration depends on frame count, FPS and clip stitching.
- Independently generated clips may have visual inconsistencies.
- Generation speed depends on GPU performance, VRAM, resolution and inference steps.
- Actual video generation has not yet been verified on the target GPU server.

## GPU Deployment

The application is designed to run model inference on a CUDA-enabled GPU server.

Before production use:

1. Verify that NVIDIA drivers and CUDA-compatible PyTorch are working.
2. Confirm GPU availability using `nvidia-smi`.
3. Install the backend requirements.
4. Install FFmpeg and verify that the `ffmpeg` command is available.
5. Start FastAPI and verify `/health`.
6. Test image generation and video generation separately.
7. Configure the frontend API URL to point to the deployed backend.
8. Configure HTTPS and restrict public API access appropriately.

Do not expose the backend publicly without suitable access controls and deployment configuration.

## Troubleshooting

**CUDA unavailable**

The local machine may not have a compatible CUDA-enabled PyTorch setup or an accessible NVIDIA GPU. Check the GPU environment before attempting generation.

**Model loading fails**

Check the model repository ID, installed Diffusers compatibility, internet access, disk space and available memory.

**Video generation runs out of memory**

Reduce frame count or resolution, or use a suitable memory optimization configuration.

**Video stitching fails**

Verify FFmpeg installation and confirm that the generated clip files exist.

**Frontend cannot connect to backend**

Check that FastAPI is running and that the configured API URL matches the backend address.

## Limitations

- GPU-based inference is required for the current implementation.
- First-time model loading can take significant time and disk space.
- Long videos require multiple generation and stitching operations.
- Production deployment and GPU inference still need end-to-end testing.

## License

Review the licenses and usage terms of the selected pretrained models before commercial use.

## Author

AI Generation Studio — Image and Video Generation Project
