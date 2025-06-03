"""
Elasticsearch MCP 客户端
用于验证 MCP 服务器的有效性
"""

import ast
import argparse
import asyncio
import json
import logging
import os
import traceback
import time
from typing import Any, Dict, List, Optional, Tuple
import sys

from mcp import ClientSession
from mcp.client.sse import sse_client
import anyio


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
        try:
            result = await self.session.call_tool(method, params)
            return result
        except anyio.EndOfStream as e:
            logger.error(f"调用工具时连接中断: {str(e)}")
            raise RuntimeError(f"SSE连接已断开，无法调用工具 {method}: {str(e)}") from e
        except Exception as e:
            logger.error(f"调用工具 {method} 时出错: {str(e)}")
            raise

async def test_list_indices(client):
    """测试列出索引工具"""
    logger.info("测试: 列出所有索引")
    try:
        response = await client.invoke("list_indices", {})
        if not response or not response.content:
            logger.error("服务器返回空响应")
            return []
            
        logger.info(f"返回结果: {response.content[0].text}")
        rco = json.loads(response.content[0].text)
        return rco.get('indices', [])
    except Exception as e:
        logger.error(f"列出索引失败: {str(e)}\n{traceback.format_exc()}")
        return []

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
    
    # 重试连接的次数
    max_retries = 3
    retry_interval = 2
    
    for attempt in range(max_retries):
        try:
            # 使用异步上下文管理器创建 SSE 客户端
            async with sse_client(url) as (read_stream, write_stream):
                logger.info("客户端连接成功")
                
                # 创建 MCP 会话，设置超时
                session_params = {}
                async with ClientSession(read_stream, write_stream, **session_params) as session:
                
                    # 等待会话初始化
                    with anyio.fail_after(10):  # 10秒超时
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
                        return True
                    except (anyio.EndOfStream, asyncio.CancelledError) as e:
                        logger.error(f"SSE连接中断: {str(e)}")
                        # 如果不是最后一次尝试，则重试
                        if attempt < max_retries - 1:
                            logger.info(f"将在 {retry_interval} 秒后重试连接...")
                            await asyncio.sleep(retry_interval)
                        else:
                            return False
                    except Exception as e:
                        logger.error(f"测试执行过程中出错: {str(e)}\n{traceback.format_exc()}")
                        return False
                        
        except (anyio.EndOfStream, ConnectionError, OSError) as e:
            logger.error(f"连接到服务器失败 (尝试 {attempt+1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"将在 {retry_interval} 秒后重试连接...")
                await asyncio.sleep(retry_interval)
            else:
                logger.error("达到最大重试次数，放弃连接")
                return False
        except Exception as e:
            logger.error(f"发生意外错误: {str(e)}\n{traceback.format_exc()}")
            return False
    
    return False

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
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="指定日志文件路径，将日志信息写入该文件"
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
    
    # 如果指定了日志文件，则添加文件处理器
    if args.log_file:
        file_handler = logging.FileHandler(args.log_file)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        # 确保文件处理器使用与根日志记录器相同的级别
        file_handler.setLevel(logger.level)
        # 将文件处理器添加到根日志记录器，这样所有模块的日志都会写入文件
        logging.getLogger().addHandler(file_handler)
        logger.info(f"日志将写入文件: {args.log_file}")
    
    try:
        # 运行测试
        success = asyncio.run(run_tests(args.url))
        
        if not success:
            os._exit(1)
    except KeyboardInterrupt:
        logger.info("接收到中断信号 (Ctrl+C)，终止客户端...")
        os._exit(0)
    except Exception as e:
        logger.error(f"客户端运行出错: {str(e)}\n{traceback.format_exc()}")
        os._exit(1)

if __name__ == "__main__":
    main() 