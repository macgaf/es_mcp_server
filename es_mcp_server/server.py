"""
Elasticsearch MCP 服务器主程序
支持通过 uvx 启动，支持 stdio 和 sse 两种传输模式
"""
import argparse
import asyncio
import logging
import os
import sys
import traceback
from typing import Any, Dict, List, Optional, Union

from mcp.server.fastmcp import FastMCP
from es_mcp_server.tools import (
    list_indices,
    get_mappings,
    search,
    get_cluster_health,
    get_cluster_stats
)
from es_mcp_server.config import es_config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 创建 FastMCP 实例
fastmcp = FastMCP()

# 注册 MCP 工具
@fastmcp.tool(name="list_indices", description="列出所有可用的 Elasticsearch 索引")
async def mcp_list_indices() -> Dict[str, Any]:
    try:
        indices = await list_indices()
        return {"indices": indices}
    except Exception as e:
        logger.error(f"列出索引失败: {str(e)}")
        return {"error": str(e)}

@fastmcp.tool(name="get_mappings", description="获取指定 Elasticsearch 索引的字段映射")
async def mcp_get_mappings(index: str) -> Dict[str, Any]:
    try:
        mappings = await get_mappings(index)
        return mappings
    except Exception as e:
        logger.error(f"获取索引映射失败: {str(e)}")
        return {"error": str(e)}

@fastmcp.tool(name="search", description="执行 Elasticsearch 搜索查询，支持高亮显示")
async def mcp_search(index: str, queryBody: Dict[str, Any]) -> Dict[str, Any]:
    try:
        results = await search(index, queryBody)
        return results
    except Exception as e:
        logger.error(f"执行搜索查询失败: {str(e)}")
        return {"error": str(e)}

@fastmcp.tool(name="get_cluster_health", description="获取 Elasticsearch 集群健康状态信息")
async def mcp_get_cluster_health() -> Dict[str, Any]:
    try:
        health = await get_cluster_health()
        return health
    except Exception as e:
        logger.error(f"获取集群健康状态失败: {str(e)}")
        return {"error": str(e)}

@fastmcp.tool(name="get_cluster_stats", description="获取 Elasticsearch 集群运行状态统计信息")
async def mcp_get_cluster_stats() -> Dict[str, Any]:
    try:
        stats = await get_cluster_stats()
        return stats
    except Exception as e:
        logger.error(f"获取集群统计信息失败: {str(e)}")
        return {"error": str(e)}

def parse_args():
    """命令行参数解析"""
    parser = argparse.ArgumentParser(description="Elasticsearch MCP 服务器")
    parser.add_argument(
        "--transport",
        type=str,
        default="stdio",
        choices=["stdio", "sse"],
        help="传输模式: stdio 或 sse，默认为 stdio"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help="Elasticsearch 主机地址，默认使用环境变量 ES_HOST 或 localhost"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Elasticsearch 端口，默认使用环境变量 ES_PORT 或 9200"
    )
    parser.add_argument(
        "--es-version",
        type=int,
        default=None,
        choices=[7, 8],
        help="Elasticsearch 版本，支持 7 或 8，默认使用环境变量 ES_VERSION 或 8"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式，显示详细日志"
    )
    parser.add_argument(
        "--sse-host",
        type=str,
        default="0.0.0.0",
        help="SSE 服务器监听地址，默认为 0.0.0.0"
    )
    parser.add_argument(
        "--sse-port",
        type=int,
        default=8000,
        help="SSE 服务器监听端口，默认为 8000"
    )
    return parser.parse_args()

async def list_available_tools():
    """列出所有可用的工具"""
    tools = await fastmcp.list_tools()
    logger.info(f"服务器提供 {len(tools)} 个工具:")
    for tool in tools:
        params_str = ""
        if hasattr(tool, 'params') and tool.params:
            params_list = []
            for name, param in tool.params.items():
                required = "必须" if hasattr(tool, 'required') and name in tool.required else "可选"
                type_str = str(param.type).replace("<class '", "").replace("'>", "") if hasattr(param, 'type') else "unknown"
                params_list.append(f"{name}: {type_str} ({required})")
            params_str = ", ".join(params_list)
        
        logger.info(f"- {tool.name}: {tool.description}")
        if params_str:
            logger.info(f"  参数: {params_str}")

async def prepare_server():
    """准备服务器启动前的工作"""
    # 测试与 Elasticsearch 的连接
    await test_es_connection()
    
    # 列出所有可用的工具
    await list_available_tools()

def main():
    """主程序入口"""
    args = parse_args()
    
    # 设置日志级别
    if args.debug:
        logger.setLevel(logging.DEBUG)
        # 设置其他库的日志级别
        logging.getLogger("mcp").setLevel(logging.DEBUG)
        logging.getLogger("elasticsearch").setLevel(logging.DEBUG)
        logging.getLogger("elasticsearch7").setLevel(logging.DEBUG)
    
    # 更新配置（命令行参数优先）
    if args.host:
        os.environ["ES_HOST"] = args.host
    if args.port:
        os.environ["ES_PORT"] = str(args.port)
    if args.es_version:
        os.environ["ES_VERSION"] = str(args.es_version)
    
    # 连接信息日志
    logger.info(f"Elasticsearch 连接: {es_config.host}:{es_config.port}")
    logger.info(f"Elasticsearch 版本: {es_config.es_version}")
    logger.info(f"传输模式: {args.transport}")
    
    try:
        # 运行准备工作
        asyncio.run(prepare_server())
        
        # 如果是 SSE 模式，设置 uvicorn 参数
        if args.transport == "sse":
            logger.info(f"SSE 服务器监听: {args.sse_host}:{args.sse_port}")
            # 设置 uvicorn 启动参数的环境变量
            os.environ["UVICORN_HOST"] = args.sse_host
            os.environ["UVICORN_PORT"] = str(args.sse_port)
        
        # 启动 MCP 服务器
        fastmcp.run(transport=args.transport)
    except Exception as e:
        error_str = f"MCP 服务器启动失败: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_str)
        sys.exit(1)

async def test_es_connection():
    """测试与 Elasticsearch 的连接"""
    from es_mcp_server.client import create_es_client
    try:
        logger.info("正在测试与 Elasticsearch 的连接...")
        client = await create_es_client()
        # 简单的 ping 测试
        async with client:
            info = await client.info()
            logger.info(f"Elasticsearch 连接成功! 版本: {info['version']['number']}")
    except Exception as e:
        logger.error(f"Elasticsearch 连接失败: {str(e)}")
        raise

if __name__ == "__main__":
    main() 