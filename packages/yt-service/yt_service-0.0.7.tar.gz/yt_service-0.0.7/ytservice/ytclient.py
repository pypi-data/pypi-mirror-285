from datetime import datetime

import yt_dlp
from fastapi import HTTPException

from ytservice.model import Settings


# Generate yt-dlp options for video downloading
def generate_video_options(settings: Settings) -> dict:
    ydl_opts = {
        'quiet': True,
        'ignoreerrors': True,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'noplaylist': True,
        'merge_output_format': 'mp4',
        'postprocessors': [{'key': 'FFmpegCopyStream'}],
        'postprocessor_args': {'copystream': ['-c:v', 'libx264', '-c:a', 'aac']},
        'buffer_size': '128M',
        'n_threads': 16,  # 设置线程数
    }

    if settings.proxy:
        ydl_opts['proxy'] = settings.proxy

    settings.download_dir.mkdir(parents=True, exist_ok=True)
    ydl_opts['outtmpl'] = str(settings.download_dir / datetime.now().strftime('%Y%m%d%H%M%S') / '%(title)s.%(ext)s')

    return ydl_opts


# Generate yt-dlp options for audio downloading
def generate_audio_options(settings: Settings) -> dict:
    ydl_opts = {
        'quiet': True,
        'ignoreerrors': True,
        'format': 'bestaudio[ext=m4a]',
        'noplaylist': True
    }

    if settings.proxy:
        ydl_opts['proxy'] = settings.proxy

    settings.download_dir.mkdir(parents=True, exist_ok=True)
    ydl_opts['outtmpl'] = str(settings.download_dir / datetime.now().strftime('%Y%m%d%H%M%S') / '%(title)s.%(ext)s')

    return ydl_opts


def optimize_audio_info(url: str, settings: Settings):
    info = extract_audio_info(url=url, settings=settings)
    best_info = dict(
        title=info.get("title", ""),
        extractor=info.get("extractor", ""),
        url=info.get("url", ""),
        ext=info.get("ext", ""),
        format=info.get("format", ""),
        resolution=info.get("resolution", ""))
    return best_info


def optimize_video_info(url: str, settings: Settings):
    info = extract_video_info(url=url, settings=settings)
    requested_formats = info.get("requested_formats", [])
    if not requested_formats:
        raise HTTPException(status_code=500, detail="No requested formats found")

    best_info = dict(
        title=info.get("title", ""),
        extractor=info.get("extractor", ""),
        requested_formats=[])

    for requested in requested_formats:
        mats = dict(
            url=requested.get("url", ""),
            ext=requested.get("ext", ""),
            format=info.get("format", ""),
            resolution=requested.get("resolution", ""))
        best_info["requested_formats"].append(mats)

    return best_info


def extract_audio_info(url: str, settings: Settings) -> dict:
    ydl_opts = generate_audio_options(settings=settings)
    return _extract_info(url=url, ydl_opts=ydl_opts)


def extract_video_info(url: str, settings: Settings) -> dict:
    ydl_opts = generate_video_options(settings=settings)
    return _extract_info(url=url, ydl_opts=ydl_opts)


# Extract video information without downloading
def _extract_info(url: str, ydl_opts: dict) -> dict:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url=url, download=False)


# Download video and return the file path
def download_video(url: str, settings: Settings) -> dict:
    ydl_opts = generate_video_options(settings=settings)
    download_info = {}

    # Progress hook to capture the file path after download
    def progress_hook(resp):
        if resp['status'] == 'finished':
            download_info["url"] = (resp['info_dict']['filename'])
            download_info["title"] = (resp['info_dict']['title'])
            download_info["description"] = (resp['info_dict']['description'])
            download_info["extractor"] = (resp['info_dict']['extractor'])
            download_info["format"] = (resp['info_dict']['format'])
            download_info["ext"] = (resp['info_dict']['ext'])
            download_info["resolution"] = (resp['info_dict']['resolution'])

    ydl_opts['progress_hooks'] = [progress_hook]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return download_info


if __name__ == '__main__':
    print("test")
