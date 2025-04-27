"""
Elasticsearch MCP 工具实现
包含所有需求的 Elasticsearch 操作工具
"""
import logging
from typing import Any, Dict, List, Optional, Union

from es_mcp_server.client import create_es_client, process_response

logger = logging.getLogger(__name__)

async def list_indices() -> List[str]:
    """
    列出所有 Elasticsearch 索引
    
    返回:
        list: 索引名称列表
    """
    client = await create_es_client()
    try:
        response = await client.indices.get_alias(index="*")
        result = await process_response(response)
        indices = list(result.keys())
        await client.close()
        return indices
    except Exception as e:
        logger.error(f"列出索引失败: {str(e)}")
        await client.close()
        raise

async def get_mappings(index: str) -> Dict[str, Any]:
    """
    获取指定索引的映射
    
    参数:
        index: 索引名称
        
    返回:
        dict: 索引映射信息
    """
    client = await create_es_client()
    try:
        response = await client.indices.get_mapping(index=index)
        result = await process_response(response)
        await client.close()
        return result
    except Exception as e:
        logger.error(f"获取索引 {index} 的映射失败: {str(e)}")
        await client.close()
        raise

async def search(
    index: str,
    query_body: Dict[str, Any]
) -> Dict[str, Any]:
    """
    执行搜索查询
    
    参数:
        index: 索引名称
        query_body: 查询DSL对象

    返回:
        dict: 搜索结果，包含匹配文档和聚合信息
    """
    client = await create_es_client()
    try:
        # 默认启用高亮
        if "highlight" not in query_body and "query" in query_body:
            query_body["highlight"] = {
                "fields": {"*": {}}
            }

        response = await client.search(index=index, body=query_body)
        result = await process_response(response)
        await client.close()
        return result
    except Exception as e:
        logger.error(f"搜索索引 {index} 失败: {str(e)}")
        await client.close()
        raise

async def get_cluster_health() -> Dict[str, Any]:
    """
    获取 Elasticsearch 集群健康状态
    
    返回:
        dict: 集群健康信息
    """
    client = await create_es_client()
    try:
        response = await client.cluster.health()
        result = await process_response(response)
        await client.close()
        return result
    except Exception as e:
        logger.error(f"获取集群健康状态失败: {str(e)}")
        await client.close()
        raise

async def get_cluster_stats() -> Dict[str, Any]:
    """
    获取 Elasticsearch 集群统计信息
    
    返回:
        dict: 集群统计信息
    """
    client = await create_es_client()
    try:
        response = await client.cluster.stats()
        result = await process_response(response)
        await client.close()
        return result
    except Exception as e:
        logger.error(f"获取集群统计信息失败: {str(e)}")
        await client.close()
        raise 