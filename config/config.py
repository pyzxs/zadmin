import os
from typing import Dict, Any, Optional
from typing import List

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings

# 根目录地址
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# 子模型定义
class AppConfig(BaseModel):
    name: str
    version: str = "1.0"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    secret_key: str
    allowed_origins: List[str] = []


class DatabaseConfig(BaseModel):
    url: str
    async_url: str
    pool_size: int = 10
    echo_sql: bool = False


class RedisConfig(BaseModel):
    url: str = "redis://:123456@127.0.0.1:6379/0"


class CorsConfig(BaseModel):
    allow_origins: list
    allow_credentials: bool = False
    allow_headers: list
    allow_methods: list

class JwtConfig(BaseModel):
    secret_key: str
    algorithm: str = "HS256"
    expires_in: int = 7200

class LoggingConfig(BaseModel):
    level: str = "INFO"
    log_path: str = "logs/app.log"
    error_path: str = "logs/error.log"
    rotate_size: int = 10
    back_files: int = 5


# 主配置模型
class Settings(BaseSettings):
    app: AppConfig
    database: DatabaseConfig
    redis: RedisConfig
    logging: LoggingConfig
    cors: CorsConfig
    jwt: JwtConfig


# 全局缓存
_cached_config: Optional[Dict[str, Any]] = None
_cached_mtime: Optional[float] = None


def load_yaml_config_with_cache(file_path: str) -> Dict[str, Any]:
    global _cached_config, _cached_mtime
    current_mtime = os.path.getmtime(file_path)
    if _cached_config is None or current_mtime != _cached_mtime:
        print("读取配置文件")
        with open(file_path, "r", encoding="UTF-8") as f:
            _cached_config = yaml.safe_load(f)
            _cached_mtime = current_mtime
    return _cached_config


def get_settings() -> Settings:
    file_path = os.path.join(BASE_DIR, "config/config.yml")
    config_data = load_yaml_config_with_cache(file_path)
    return Settings(**config_data)


# 测试
if __name__ == "__main__":
    print(BASE_DIR)
    settings1 = get_settings()  # 第一次加载
    settings2 = get_settings()  # 从缓存读取
    print(settings1 == settings2)  # True
