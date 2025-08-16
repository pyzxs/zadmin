import os
from typing import Dict, Any, Optional
from typing import List

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings


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
    host: str = "localhost"
    port: int = 6379
    password: str = ""
    db: int = 0


class LoggingConfig(BaseModel):
    level: str = "INFO"
    log_path: str = "logs/app.log"
    rotation: str = "10 MB"


# 主配置模型
class Settings(BaseSettings):
    app: AppConfig
    database: DatabaseConfig
    redis: RedisConfig
    logging: LoggingConfig


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 全局缓存
_cached_config: Optional[Dict[str, Any]] = None
_cached_mtime: Optional[float] = None


def load_yaml_config_with_cache(file_path: str) -> Dict[str, Any]:
    global _cached_config, _cached_mtime
    current_mtime = os.path.getmtime(file_path)
    if _cached_config is None or current_mtime != _cached_mtime:
        print(f"Reloading YAML file: {file_path}")
        with open(file_path, "r", encoding="UTF-8") as f:
            _cached_config = yaml.safe_load(f)
            _cached_mtime = current_mtime
    return _cached_config


def get_settings() -> Settings:
    file_path = BASE_DIR + "/config/config.yml"
    config_data = load_yaml_config_with_cache(file_path)
    return Settings(**config_data)


# 测试
if __name__ == "__main__":
    print(BASE_DIR)
    settings1 = get_settings()  # 第一次加载
    settings2 = get_settings()  # 从缓存读取
    print(settings1 == settings2)  # True

    # 模拟文件修改（手动更改 application.yaml 后再次运行）
    input("Modify config.yaml and press Enter...")
    settings3 = get_settings()  # 检测到文件变化，重新加载
    print(settings1 == settings3)  # False（如果文件被修改）
