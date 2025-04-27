"""
配置模块，用于加载 Elasticsearch 连接配置
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

class ESConfig(BaseSettings):
    """Elasticsearch 连接配置"""
    host: str = os.getenv("ES_HOST", "localhost")
    port: int = int(os.getenv("ES_PORT", "9200"))
    username: Optional[str] = os.getenv("ES_USERNAME")
    password: Optional[str] = os.getenv("ES_PASSWORD")
    api_key: Optional[str] = os.getenv("ES_API_KEY")
    use_ssl: bool = os.getenv("ES_USE_SSL", "false").lower() == "true"
    verify_certs: bool = os.getenv("ES_VERIFY_CERTS", "true").lower() == "true"
    
    # ES 版本，支持 7 和 8
    es_version: int = int(os.getenv("ES_VERSION", "8"))
    
    @property
    def has_auth(self) -> bool:
        """检查是否设置了认证信息"""
        return bool((self.username and self.password) or self.api_key)
    
    @property
    def hosts(self) -> list:
        """返回格式化的主机列表"""
        return [f"{self.host}:{self.port}"]

# 创建全局配置实例
es_config = ESConfig() 