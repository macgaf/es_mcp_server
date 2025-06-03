"""
Elasticsearch MCP 工具实现
包含所有需求的 Elasticsearch 操作工具
"""
import logging
from typing import Any, Dict, List, Optional, Union
from contextlib import asynccontextmanager

from es_mcp_server.client import create_es_client, process_response

logger = logging.getLogger(__name__)

async def list_indices() -> List[str]:
    """
    列出所有 Elasticsearch 索引
    
    返回:
        list: 索引名称列表
    """
    async with create_es_client() as client:
        try:
            response = await client.indices.get_alias(index="*")
            result = await process_response(response)
            indices = list(result.keys())
            return indices
        except Exception as e:
            logger.error(f"列出索引失败: {str(e)}")
            raise

async def get_mappings(index: str) -> Dict[str, Any]:
    """
    获取指定索引的映射
    
    参数:
        index: 索引名称
        
    返回:
        dict: 索引映射信息
    """
    async with create_es_client() as client:
        try:
            response = await client.indices.get_mapping(index=index)
            result = await process_response(response)
            return result
        except Exception as e:
            logger.error(f"获取索引 {index} 的映射失败: {str(e)}")
            raise

async def search(
    index: str,
    query_body: Dict[str, Any],
    scroll: str = None,
    size: int = 100
) -> Dict[str, Any]:
    """
    执行搜索查询
    
    参数:
        index: 索引名称
        query_body: 查询DSL对象
        scroll: 可选，scroll保持活动的时间 (如 "1m" 表示1分钟)，设置后启用scroll模式
        size: 每批返回的文档数量，默认100，仅在scroll模式时有效

    返回:
        dict: 搜索结果，包含匹配文档和聚合信息，启用scroll时还会包含scroll_id
    """
    async with create_es_client() as client:
        try:
            # 设置size参数(scroll模式时)
            if scroll and "size" not in query_body:
                query_body["size"] = size
                
            # 默认启用高亮
            if "highlight" not in query_body and "query" in query_body:
                query_body["highlight"] = {
                    "fields": {"*": {}}
                }

            # 根据是否提供scroll参数决定使用普通搜索还是scroll搜索
            if scroll:
                # 使用scroll模式
                response = await client.search(
                    index=index, 
                    body=query_body,
                    scroll=scroll
                )
            else:
                # 使用普通搜索
                response = await client.search(index=index, body=query_body)
            result = await process_response(response)
            
            # 如果是scroll模式，确保返回scroll_id
            if scroll and "_scroll_id" in response:
                result["_scroll_id"] = response["_scroll_id"]
                
            return result
        except Exception as e:
            logger.error(f"{'Scroll ' if scroll else ''}搜索索引 {index} 失败: {str(e)}")
            raise

async def scroll(
    scroll_id: str,
    scroll: str = "1m"
) -> Dict[str, Any]:
    """
    使用scroll_id获取下一批结果
    
    参数:
        scroll_id: 前一次请求返回的scroll_id
        scroll: scroll保持活动的时间 (如 "1m" 表示1分钟)
        
    返回:
        dict: 下一批搜索结果和更新的scroll_id
    """
    async with create_es_client() as client:
        try:
            # ES 7.x用法
            if hasattr(client, "scroll"):
                response = await client.scroll(
                    scroll_id=scroll_id,
                    scroll=scroll
                )
            # ES 8.x用法
            else:
                response = await client.scroll(
                    body={"scroll_id": scroll_id, "scroll": scroll}
                )
                
            result = await process_response(response)
            
            # 确保返回scroll_id (如果不是最后一页)
            if "_scroll_id" in response and len(response.get("hits", {}).get("hits", [])) > 0:
                result["_scroll_id"] = response["_scroll_id"]
                
            return result
        except Exception as e:
            logger.error(f"执行scroll获取下一页失败: {str(e)}")
            raise

async def clear_scroll(
    scroll_id: str
) -> Dict[str, Any]:
    """
    清除scroll上下文，释放资源
    
    参数:
        scroll_id: 要清除的scroll_id
        
    返回:
        dict: 清除操作的结果
    """
    async with create_es_client() as client:
        try:
            # ES 7.x用法
            if hasattr(client, "clear_scroll"):
                response = await client.clear_scroll(
                    scroll_id=scroll_id
                )
            # ES 8.x用法
            else:
                response = await client.clear_scroll(
                    body={"scroll_id": [scroll_id]}
                )
                
            result = await process_response(response)
            return result
        except Exception as e:
            logger.error(f"清除scroll上下文失败: {str(e)}")
            raise

async def get_cluster_health() -> Dict[str, Any]:
    """
    获取 Elasticsearch 集群健康状态
    
    返回:
        dict: 集群健康信息
    """
    async with create_es_client() as client:
        try:
            response = await client.cluster.health()
            result = await process_response(response)
            return result
        except Exception as e:
            logger.error(f"获取集群健康状态失败: {str(e)}")
            raise

async def get_cluster_stats() -> Dict[str, Any]:
    """
    获取 Elasticsearch 集群统计信息
    
    返回:
        dict: 集群统计信息
    """
    async with create_es_client() as client:
        try:
            response = await client.cluster.stats()
            result = await process_response(response)
            return result
        except Exception as e:
            logger.error(f"获取集群统计信息失败: {str(e)}")
            raise 