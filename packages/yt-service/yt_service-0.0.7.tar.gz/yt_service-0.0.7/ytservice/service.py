import sys
import urllib.parse
from pathlib import Path

import click
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse

from ytservice import (model, ytclient, common, exception_handlers)
from ytservice.model import (Settings, YtModel)
from ytservice.version import VERSION

APP_NAME = "yt-service"

# Initialize settings and FastAPI app
settings = Settings()
app = FastAPI(redoc_url=None)

app.add_exception_handler(RequestValidationError, exception_handlers.validation_exception_handler)
app.add_exception_handler(HTTPException, exception_handlers.http_exception_handler)
app.add_exception_handler(Exception, exception_handlers.global_exception_handler)


@app.get("/")
def read_root():
    return dict(app=APP_NAME, version=VERSION,
                Lan="http://{0}:{1}".format(common.get_local_ip(), settings.port))


# Endpoint to extract audio information
@app.post("/yt/audio/info")
async def audio_info(post_model: YtModel):
    try:
        content = ytclient.extract_audio_info(url=post_model.url, settings=settings)
        if content:
            return common.build_response(data=content)
        else:
            raise HTTPException(status_code=500, detail="Failed to extract video info")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to extract audio information
@app.post("/yt/audio/bestInfo")
async def audio_best_info(post_model: YtModel):
    try:
        content = ytclient.optimize_audio_info(url=post_model.url, settings=settings)
        if content:
            return common.build_response(data=content)
        else:
            raise HTTPException(status_code=500, detail="Failed to extract video bestInfo")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to download video
@app.post("/yt/video/download")
async def video_download(post_model: YtModel):
    try:
        download_info = ytclient.download_video(url=post_model.url, settings=settings)
        if download_info:
            download_url = download_info["url"]
            file_name = Path(download_url).name
            encoded_file_name = urllib.parse.quote(file_name)
            # Include timestamp directory in the download URL
            timestamp = Path(download_url).parent.name
            file_url = f"http://{common.get_local_ip()}:{settings.port}/yt/download-file/{timestamp}/{encoded_file_name}"
            download_info["url"] = file_url
            return common.build_response(data=download_info)
        else:
            raise HTTPException(status_code=500, detail="Failed to download video")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to extract video information
@app.post("/yt/video/info")
async def video_info(post_model: YtModel):
    try:
        content = ytclient.extract_video_info(url=post_model.url, settings=settings)
        if content:
            return common.build_response(data=content)
        else:
            raise HTTPException(status_code=500, detail="Failed to extract video info")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to extract video information
@app.post("/yt/video/bestInfo")
async def video_best_info(post_model: YtModel):
    try:
        content = ytclient.optimize_video_info(url=post_model.url, settings=settings)
        if content:
            return common.build_response(data=content)
        else:
            raise HTTPException(status_code=500, detail="Failed to extract video bestInfo")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to serve downloaded files
@app.get("/yt/download-file/{timestamp}/{encoded_file_name}")
async def download_file(timestamp: str, encoded_file_name: str):
    file_name = urllib.parse.unquote(encoded_file_name)
    file_location = settings.download_dir / timestamp / file_name
    if not file_location.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_location, filename=file_location.name)


# CLI command to start the server with optional settings
@click.command()
@click.option('--host', type=str, show_default=True, default=model.SETTING_HOST, help='Service IP address')
@click.option('--port', type=int, show_default=True, default=model.SETTING_PORT, help='Service port')
@click.option('--proxy', type=str, show_default=True, default=model.SETTING_PROXY, help='Proxy server address')
@click.option('--download-dir', type=click.Path(), help='Download directory [~/YTDownload]')
@click.option('-s', '--signal', help='send signal to service',
              type=click.Choice(['install', 'start', 'stop', 'status', 'rm'], case_sensitive=False))
@click.option('--version', is_flag=True)
def start_server(host, port, proxy, download_dir, signal, version):
    if version:
        click.echo(VERSION)
        return
    if signal:
        common.run_service(app_name=APP_NAME, signal=signal)
        return
    if host:
        settings.host = host
    if port:
        settings.port = port
    if proxy:
        settings.proxy = proxy
    if download_dir:
        settings.download_dir = Path(download_dir)
    uvicorn.run(app, host=settings.host, port=settings.port)


# Main entry point to start the server
if __name__ == "__main__":
    sys.argv.append("--version")
    start_server()
