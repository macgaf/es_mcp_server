"""
Elasticsearch 客户端工厂模块
支持 ES7 和 ES8 版本的客户端创建
"""
import logging
from typing import Any, Dict, Union, Optional

from es_mcp_server.config import es_config

logger = logging.getLogger(__name__)

# 全局客户端实例
_es_client = None

async def create_es_client() -> Any:
    """
    创建 Elasticsearch 客户端
    根据配置的 ES 版本创建对应的异步客户端
    
    返回:
        Elasticsearch 异步客户端实例
    """
    global _es_client
    
    # 如果已有客户端实例且没有关闭，则复用
    if _es_client is not None:
        return _es_client
    
    connection_params = _get_connection_params()
    
    if es_config.es_version == 7:
        # ES7 客户端
        from elasticsearch7 import AsyncElasticsearch
        _es_client = AsyncElasticsearch(**connection_params)
    else:
        # ES8 客户端
        from elasticsearch import AsyncElasticsearch
        _es_client = AsyncElasticsearch(**connection_params)
    
    return _es_client

async def close_es_client() -> None:
    """
    关闭 Elasticsearch 客户端连接
    在服务器关闭时调用以释放资源
    """
    global _es_client
    
    if _es_client is not None:
        logger.info("正在关闭 Elasticsearch 客户端连接...")
        try:
            await _es_client.close()
            logger.info("Elasticsearch 客户端连接已关闭")
        except Exception as e:
            logger.error(f"关闭 Elasticsearch 客户端时出错: {str(e)}")
        finally:
            _es_client = None

def _get_connection_params() -> Dict[str, Any]:
    """
    构建 Elasticsearch 连接参数
    
    返回:
        dict: ES 连接参数字典
    """
    # 确定协议
    scheme = "https" if es_config.use_ssl else "http"
    
    # 构建完整 URL 列表
    hosts = [f"{scheme}://{es_config.host}:{es_config.port}"]
    
    logger.debug(f"创建 ES 客户端，连接到: {hosts}")
    
    params = {
        "hosts": hosts,
    }
    
    # 添加 SSL/TLS 配置
    if es_config.use_ssl:
        params["verify_certs"] = es_config.verify_certs
    
    # 添加认证信息
    if es_config.username and es_config.password:
        if es_config.es_version == 7:
            params["http_auth"] = (es_config.username, es_config.password)
        else:
            params["basic_auth"] = (es_config.username, es_config.password)
    elif es_config.api_key:
        params["api_key"] = es_config.api_key
    
    return params

async def process_response(response: Any) -> Any:
    """
    处理 ES 响应，兼容 ES7 和 ES8
    
    参数:
        response: ES 响应对象
        
    返回:
        处理后的响应数据
    """
    if es_config.es_version == 7:
        # ES7 从 response 获取数据
        return response
    else:
        # ES8 response.body 获取数据
        return response.body