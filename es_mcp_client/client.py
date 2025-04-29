"""
Elasticsearch MCP 客户端
用于验证 MCP 服务器的有效性
"""

import ast
import argparse
import asyncio
import json
import logging
import traceback
from typing import Any, Dict, List, Optional
import sys

from mcp import ClientSession
from mcp.client.sse import sse_client


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class ESMCPClient:
    """MCP 客户端包装类"""
    
    def __init__(self, session: ClientSession):
        """初始化 MCP 客户端"""
        self.session = session
    
    async def invoke(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """调用 MCP 方法"""
        # 使用MCP会话调用工具
        result = await self.session.call_tool(method, params)
        return result

async def test_list_indices(client):
    """测试列出索引工具"""
    logger.info("测试: 列出所有索引")
    try:
        response = await client.invoke("list_indices", {})
        logger.info(f"返回结果: {response.content[0].text}")
        rco = json.loads(response.content[0].text)
        return rco['indices']
    except Exception as e:
        logger.error(f"列出索引失败: {str(e)}\n{traceback.format_exc()}")
        raise

async def test_get_mappings(client, index):
    """测试获取索引映射工具"""
    logger.info(f"测试: 获取索引 {index} 的映射")
    try:
        response = await client.invoke("get_mappings", {"index": index})
        logger.info(f"返回结果: {response.content[0].text}")
        return response
    except Exception as e:
        logger.error(f"获取索引映射失败: {str(e)}\n{traceback.format_exc()}")
        raise

async def test_search(client, index):
    """测试搜索工具"""
    logger.info(f"测试: 在索引 {index} 中搜索")
    try:
        query_body = {
            "query": {
                "match_all": {}
            },
            "size": 5
        }
        response = await client.invoke("search", {
            "index": index,
            "queryBody": query_body
        })
        logger.info(f"返回结果中的文档数: {response.content[0].text}")
        return response
    except Exception as e:
        logger.error(f"搜索失败: {str(e)}\n{traceback.format_exc()}")
        raise

async def test_cluster_health(client):
    """测试获取集群健康状态工具"""
    logger.info("测试: 获取集群健康状态")
    try:
        response = await client.invoke("get_cluster_health", {})
        logger.info(f"返回结果: {response.content[0].text}")
        return response
    except Exception as e:
        logger.error(f"获取集群健康状态失败: {str(e)}\n{traceback.format_exc()}")
        raise

async def test_cluster_stats(client):
    """测试获取集群统计信息工具"""
    logger.info("测试: 获取集群统计信息")
    try:
        response = await client.invoke("get_cluster_stats", {})
        ro = json.loads(response.content[0].text)
        logger.info(f"集群名称: {ro.get('cluster_name')}")
        logger.info(f"节点数: {ro.get('nodes', {}).get('count', {})}")
        return response
    except Exception as e:
        logger.error(f"获取集群统计信息失败: {str(e)}\n{traceback.format_exc()}")
        raise

async def run_tests(url: str):
    """运行所有测试"""
    logger.info(f"连接到 MCP 服务器: {url}")
    
    try:
        # 使用异步上下文管理器创建 SSE 客户端
        async with sse_client(url) as (read_stream, write_stream):
            logger.info("客户端连接成功")
            
            # 创建 MCP 会话
            async with ClientSession(read_stream, write_stream) as session:
            
                # 等待会话初始化
                await session.initialize()
                
                # 创建Elasticsearch MCP客户端
                client = ESMCPClient(session)

                try:
                    # 运行测试
                    indices = await test_list_indices(client)
                    
                    if indices:
                        # 选择第一个索引进行测试
                        test_index = indices[0]
                        logger.info(f"选择索引 {test_index} 进行后续测试")
                        
                        await test_get_mappings(client, test_index)
                        await test_search(client, test_index)
                    else:
                        logger.warning("未找到索引，跳过相关测试")
                    
                    await test_cluster_health(client)
                    await test_cluster_stats(client)
                    
                    logger.info("所有测试完成")
                except Exception as e:
                    logger.error(f"测试执行过程中出错: {str(e)}\n{traceback.format_exc()}")
                    return False
    except Exception as e:
        logger.error(f"连接到服务器失败: {str(e)}\n{traceback.format_exc()}")
        return False
    
    return True

def parse_args():
    """命令行参数解析"""
    parser = argparse.ArgumentParser(description="Elasticsearch MCP 客户端测试程序")
    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:8000/sse",
        help="MCP 服务器 SSE 终端点 URL，默认为 http://localhost:8000/sse"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式，显示详细日志"
    )
    return parser.parse_args()

def main():
    """主程序入口"""
    args = parse_args()
    
    # 设置日志级别
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logging.getLogger("mcp").setLevel(logging.DEBUG)
        logging.getLogger("httpx").setLevel(logging.DEBUG)
    
    # 运行测试
    success = asyncio.run(run_tests(args.url))
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 