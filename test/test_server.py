"""
Elasticsearch MCP 服务器单元测试
"""
import asyncio
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from es_mcp_server.tools import (
    list_indices,
    get_mappings,
    search,
    get_cluster_health,
    get_cluster_stats
)

# 模拟 ES 响应数据
MOCK_INDICES = {"index1": {}, "index2": {}}
MOCK_MAPPINGS = {"index1": {"mappings": {"properties": {"field1": {"type": "text"}}}}}
MOCK_SEARCH_RESULT = {
    "hits": {
        "total": {"value": 10},
        "hits": [{"_id": "1", "_source": {"field1": "value1"}}]
    }
}
MOCK_HEALTH = {"status": "green", "cluster_name": "test_cluster"}
MOCK_STATS = {"cluster_name": "test_cluster", "nodes": {"count": {"total": 1}}}

@pytest.fixture
def mock_es_client():
    """模拟 ES 客户端"""
    client = AsyncMock()
    
    # 模拟索引响应
    indices_response = MagicMock()
    indices_response.body = MOCK_INDICES
    client.indices.get_alias.return_value = indices_response
    
    # 模拟映射响应
    mappings_response = MagicMock()
    mappings_response.body = MOCK_MAPPINGS
    client.indices.get_mapping.return_value = mappings_response
    
    # 模拟搜索响应
    search_response = MagicMock()
    search_response.body = MOCK_SEARCH_RESULT
    client.search.return_value = search_response
    
    # 模拟集群健康响应
    health_response = MagicMock()
    health_response.body = MOCK_HEALTH
    client.cluster.health.return_value = health_response
    
    # 模拟集群统计响应
    stats_response = MagicMock()
    stats_response.body = MOCK_STATS
    client.cluster.stats.return_value = stats_response
    
    return client

@pytest.mark.asyncio
@patch("es_mcp_server.tools.create_es_client")
@patch("es_mcp_server.tools.process_response")
async def test_list_indices(mock_process_response, mock_create_client, mock_es_client):
    """测试列出索引功能"""
    mock_create_client.return_value = mock_es_client
    mock_process_response.return_value = MOCK_INDICES
    
    result = await list_indices()
    
    mock_es_client.indices.get_alias.assert_called_once_with(index="*")
    assert len(result) == 2
    assert "index1" in result
    assert "index2" in result

@pytest.mark.asyncio
@patch("es_mcp_server.tools.create_es_client")
@patch("es_mcp_server.tools.process_response")
async def test_get_mappings(mock_process_response, mock_create_client, mock_es_client):
    """测试获取索引映射功能"""
    mock_create_client.return_value = mock_es_client
    mock_process_response.return_value = MOCK_MAPPINGS
    
    result = await get_mappings("index1")
    
    mock_es_client.indices.get_mapping.assert_called_once_with(index="index1")
    assert result == MOCK_MAPPINGS

@pytest.mark.asyncio
@patch("es_mcp_server.tools.create_es_client")
@patch("es_mcp_server.tools.process_response")
async def test_search(mock_process_response, mock_create_client, mock_es_client):
    """测试搜索功能"""
    mock_create_client.return_value = mock_es_client
    mock_process_response.return_value = MOCK_SEARCH_RESULT
    
    query_body = {"query": {"match_all": {}}}
    result = await search("index1", query_body)
    
    mock_es_client.search.assert_called_once()
    assert result == MOCK_SEARCH_RESULT

@pytest.mark.asyncio
@patch("es_mcp_server.tools.create_es_client")
@patch("es_mcp_server.tools.process_response")
async def test_get_cluster_health(mock_process_response, mock_create_client, mock_es_client):
    """测试获取集群健康状态功能"""
    mock_create_client.return_value = mock_es_client
    mock_process_response.return_value = MOCK_HEALTH
    
    result = await get_cluster_health()
    
    mock_es_client.cluster.health.assert_called_once()
    assert result == MOCK_HEALTH

@pytest.mark.asyncio
@patch("es_mcp_server.tools.create_es_client")
@patch("es_mcp_server.tools.process_response")
async def test_get_cluster_stats(mock_process_response, mock_create_client, mock_es_client):
    """测试获取集群统计信息功能"""
    mock_create_client.return_value = mock_es_client
    mock_process_response.return_value = MOCK_STATS
    
    result = await get_cluster_stats()
    
    mock_es_client.cluster.stats.assert_called_once()
    assert result == MOCK_STATS 