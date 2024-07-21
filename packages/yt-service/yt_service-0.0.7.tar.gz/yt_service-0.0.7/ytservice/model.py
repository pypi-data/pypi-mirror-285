from pathlib import Path

from fastapi import HTTPException
from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings

SETTING_HOST = "0.0.0.0"
SETTING_PORT = 8000
SETTING_PROXY = "socks5://127.0.0.1:1086"


# Configuration settings for the application
class Settings(BaseSettings):
    host: str = SETTING_HOST
    port: int = SETTING_PORT
    proxy: str = SETTING_PROXY
    download_dir: Path = Path.home() / "YTDownload"
    home_dir: Path = Path.home() / ".yt-home"


# Model for YouTube URL input
class YtModel(BaseModel):
    url: str

    # Validator to ensure the URL starts with http:// or https://
    @field_validator('url')
    def url_valid(cls, v):
        if not (v.startswith("http://") or v.startswith("https://")):
            raise HTTPException(status_code=500, detail='URL must start with http:// or https://')
        return v
