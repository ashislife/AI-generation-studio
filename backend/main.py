import os
import uuid
import gc
import subprocess
from pathlib import Path
from threading import Lock
from math import ceil

import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from diffusers import (
    StableDiffusionPipeline,
    AutoencoderKLWan,
    WanPipeline,
)
from diffusers.schedulers.scheduling_unipc_multistep import (
    UniPCMultistepScheduler,
)
from diffusers.utils import export_to_video


# =========================================================
# CONFIG
# =========================================================

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

IMAGE_ID = os.getenv(
    "IMAGE_MODEL_ID",
    "runwayml/stable-diffusion-v1-5",
)

VIDEO_MODEL_ID = os.getenv(
    "VIDEO_MODEL_ID",
    "Wan-AI/Wan2.1-T2V-1.3B-Diffusers",
)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE = torch.float16 if DEVICE == "cuda" else torch.float32

image_pipe = None
video_pipe = None
lock = Lock()

app = FastAPI(title="AI Generation Studio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv(
        "FRONTEND_ORIGINS", "*"
    ).split(","),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# REQUEST MODELS
# =========================================================

class ImageRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=1500)

    negative_prompt: str = (
        "blurry, low quality, distorted, deformed, watermark, text"
    )

    steps: int = Field(default=20, ge=1, le=50)
    guidance: float = Field(default=7.5, ge=1, le=15)
    seed: int = Field(default=42, ge=0, le=4294967295)

    width: int = Field(default=512, ge=256, le=768)
    height: int = Field(default=512, ge=256, le=768)


class VideoRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=1500)

    negative_prompt: str = (
        "blurry, distorted, low quality, flicker, watermark, text"
    )

    steps: int = Field(default=20, ge=4, le=40)
    guidance: float = Field(default=5.0, ge=1, le=10)
    seed: int = Field(default=42, ge=0, le=4294967295)

    # Wan requires (frames - 1) to be divisible by 4.
    frames: int = Field(default=49, ge=9, le=81)

    # Requested final video duration.
    duration_seconds: int = Field(default=10, ge=5, le=10)

    # Resolution.
    width: int = Field(default=480, ge=256, le=832)
    height: int = Field(default=480, ge=256, le=832)


# =========================================================
# HELPERS
# =========================================================

def need_gpu():
    if not torch.cuda.is_available():
        raise HTTPException(
            status_code=503,
            detail=(
                "CUDA GPU unavailable. "
                "Use the GPU server for inference."
            ),
        )


def clear_gpu():
    gc.collect()

    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def get_image_pipe():
    global image_pipe

    need_gpu()

    if image_pipe is None:
        image_pipe = StableDiffusionPipeline.from_pretrained(
            IMAGE_ID,
            torch_dtype=DTYPE,
            use_safetensors=True,
        )

        image_pipe.enable_attention_slicing()
        image_pipe.to("cuda")

    return image_pipe


def get_video_pipe():
    global video_pipe

    need_gpu()

    if video_pipe is None:
        vae = AutoencoderKLWan.from_pretrained(
            VIDEO_MODEL_ID,
            subfolder="vae",
            torch_dtype=torch.float32,
        )

        pipe = WanPipeline.from_pretrained(
            VIDEO_MODEL_ID,
            vae=vae,
            torch_dtype=torch.float16,
        )

        pipe.scheduler = UniPCMultistepScheduler.from_config(
            pipe.scheduler.config,
            prediction_type="flow_prediction",
            use_flow_sigmas=True,
            num_train_timesteps=1000,
            flow_shift=3.0,
        )

        pipe.enable_model_cpu_offload()
        pipe.vae.enable_tiling()
        pipe.set_progress_bar_config(disable=False)

        video_pipe = pipe

    return video_pipe


def stitch_videos(
    video_paths,
    output_path,
    duration_seconds=None,
):
    """Concatenate MP4 clips and trim to the requested duration."""

    if not video_paths:
        raise RuntimeError("No video clips were generated.")

    concat_file = None

    try:
        if len(video_paths) == 1:
            input_args = [
                "-i",
                str(video_paths[0]),
            ]

        else:
            concat_file = OUT / (
                f"concat_{uuid.uuid4().hex}.txt"
            )

            with open(
                concat_file,
                "w",
                encoding="utf-8",
            ) as file:
                for video_path in video_paths:
                    safe_path = (
                        str(Path(video_path).resolve())
                        .replace("\\", "/")
                        .replace("'", "'\\''")
                    )

                    file.write(f"file '{safe_path}'\n")

            input_args = [
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_file),
            ]

        command = [
            "ffmpeg",
            "-y",
            *input_args,
        ]

        if duration_seconds is not None:
            command.extend([
                "-t",
                str(duration_seconds),
            ])

        command.extend([
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(output_path),
        ])

        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=3600,
        )

    finally:
        if concat_file is not None and concat_file.exists():
            concat_file.unlink()


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "cuda_available": torch.cuda.is_available(),
        "device": DEVICE,
        "gpu_name": (
            torch.cuda.get_device_name(0)
            if torch.cuda.is_available()
            else None
        ),
        "image_model": IMAGE_ID,
        "video_model": VIDEO_MODEL_ID,
    }


# =========================================================
# IMAGE GENERATION
# =========================================================

@app.post("/api/generate/image")
def generate_image(req: ImageRequest):
    need_gpu()

    name = f"image_{uuid.uuid4().hex}.png"
    path = OUT / name

    with lock:
        try:
            pipe = get_image_pipe()

            generator = torch.Generator(
                device="cuda"
            ).manual_seed(req.seed)

            image = pipe(
                prompt=req.prompt,
                negative_prompt=req.negative_prompt,
                num_inference_steps=req.steps,
                guidance_scale=req.guidance,
                width=req.width,
                height=req.height,
                generator=generator,
            ).images[0]

            image.save(path)

        except HTTPException:
            raise

        except Exception as exc:
            clear_gpu()

            raise HTTPException(
                status_code=500,
                detail=f"Image generation failed: {exc}",
            ) from exc

    return {
        "status": "success",
        "filename": name,
        "url": f"/outputs/{name}",
    }


# =========================================================
# VIDEO GENERATION
# =========================================================

@app.post("/api/generate/video")
def generate_video(req: VideoRequest):
    need_gpu()

    if (req.frames - 1) % 4 != 0:
        raise HTTPException(
            status_code=422,
            detail=(
                "Wan frames must satisfy "
                "(frames - 1) % 4 == 0."
            ),
        )

    name = f"video_{uuid.uuid4().hex}.mp4"
    final_path = OUT / name
    clip_paths = []

    fps = 16
    frames_per_clip = req.frames
    clip_seconds = (frames_per_clip - 1) / fps

    # Calculate how many clips are needed to cover the duration.
    clip_count = max(
        1,
        ceil(req.duration_seconds / clip_seconds),
    )

    with lock:
        try:
            pipe = get_video_pipe()

            for index in range(clip_count):
                clip_path = OUT / (
                    f"clip_{uuid.uuid4().hex}.mp4"
                )

                generator = torch.Generator(
                    device="cpu"
                ).manual_seed(req.seed + index)

                segment_prompt = (
                    f"{req.prompt}. "
                    "Cinematic scene, natural movement, "
                    "consistent subject and environment."
                )

                with torch.inference_mode():
                    result = pipe(
                        prompt=segment_prompt,
                        negative_prompt=req.negative_prompt,
                        num_frames=frames_per_clip,
                        num_inference_steps=req.steps,
                        guidance_scale=req.guidance,
                        width=req.width,
                        height=req.height,
                        generator=generator,
                    )

                export_to_video(
                    result.frames[0],
                    str(clip_path),
                    fps=fps,
                )

                clip_paths.append(str(clip_path))

                del result
                clear_gpu()

            # Combine clips and trim the final MP4.
            stitch_videos(
                clip_paths,
                final_path,
                req.duration_seconds,
            )

        except HTTPException:
            raise

        except subprocess.TimeoutExpired as exc:
            clear_gpu()

            raise HTTPException(
                status_code=500,
                detail="FFmpeg stitching timed out.",
            ) from exc

        except Exception as exc:
            clear_gpu()

            raise HTTPException(
                status_code=500,
                detail=f"Video generation failed: {exc}",
            ) from exc

        finally:
            for clip in clip_paths:
                try:
                    if os.path.exists(clip):
                        os.remove(clip)

                except OSError:
                    pass

    return {
        "status": "success",
        "filename": name,
        "url": f"/outputs/{name}",
        "requested_duration_seconds": req.duration_seconds,
        "segments_generated": clip_count,
        "note": (
            "Output is trimmed to the requested duration. "
            "Independently generated clips may not be "
            "visually continuous."
        ),
    }


# =========================================================
# STATIC OUTPUTS
# =========================================================

app.mount(
    "/outputs",
    StaticFiles(directory=str(OUT)),
    name="outputs",
)