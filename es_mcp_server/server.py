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
import time
import signal
import atexit
from typing import Any, Dict, List, Optional, Union

from mcp.server.fastmcp import FastMCP
from es_mcp_server.tools import (
    list_indices,
    get_mappings,
    search,
    get_cluster_health,
    get_cluster_stats,
    scroll as es_scroll,
    clear_scroll
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
# 初始化时不设置端口，后面会根据命令行参数设置
fastmcp = FastMCP()

# 全局连接状态
es_connected = False

# 注册 MCP 工具
@fastmcp.tool(name="list_indices")
async def mcp_list_indices() -> Dict[str, Any]:
    """
    列出所有可用的 Elasticsearch 索引
    """
    if not es_connected:
        return {"error": "Elasticsearch 连接不可用，请检查连接配置或稍后重试"}
    try:
        indices = await list_indices()
        return {"indices": indices}
    except Exception as e:
        logger.error(f"列出索引失败: {str(e)}")
        return {"error": str(e)}

@fastmcp.tool(name="get_mappings")
async def mcp_get_mappings(index: str) -> Dict[str, Any]:
    """
    获取指定 Elasticsearch 索引的字段映射
    
    参数:
        index: 要查询的索引名称
    """
    if not es_connected:
        return {"error": "Elasticsearch 连接不可用，请检查连接配置或稍后重试"}
    try:
        mappings = await get_mappings(index)
        return mappings
    except Exception as e:
        logger.error(f"获取索引映射失败: {str(e)}")
        return {"error": str(e)}

@fastmcp.tool(name="search")
async def mcp_search(index: str, queryBody: Dict[str, Any], scroll: str = None, size: int = 1000) -> Dict[str, Any]:
    """
    执行 Elasticsearch 搜索查询，支持scroll分页获取大量结果
    
    参数:
        index: 要查询的索引名称
        queryBody: 搜索查询条件
        scroll: scroll保持活动的时间 (如 "1m" 表示1分钟)
        size: 每页返回的文档数量，默认1000，只在scroll不为空的情况下有效
    
    返回:
        dict: 搜索结果，
            如果scroll为空，返回本次的搜索结果，
            如果scroll不为空，返回搜索结果的_scroll_id属性为后续scroll的scrollId参数的值
    """
    if not es_connected:
        return {"error": "Elasticsearch 连接不可用，请检查连接配置或稍后重试"}
    try:
        # 直接调用合并后的search函数，它会根据scroll参数决定使用哪种模式
        results = await search(index, queryBody, scroll, size)
        return results
    except Exception as e:
        logger.error(f"执行{'scroll' if scroll else ''}搜索查询失败: {str(e)}")
        return {"error": str(e)}

@fastmcp.tool(name="scroll")
async def mcp_scroll(scrollId: str, scroll: str = "1m") -> Dict[str, Any]:
    """
    获取 scroll API 查询的下一批结果
    
    参数:
        scrollId: 前一次请求返回的结果的_scroll_id属性
        scroll: scroll保持活动的时间 (如 "1m" 表示1分钟)
    """
    if not es_connected:
        return {"error": "Elasticsearch 连接不可用，请检查连接配置或稍后重试"}
    try:
        results = await es_scroll(scrollId, scroll)
        return results
    except Exception as e:
        logger.error(f"获取scroll下一页失败: {str(e)}")
        return {"error": str(e)}

@fastmcp.tool(name="clear_scroll")
async def mcp_clear_scroll(scrollId: str) -> Dict[str, Any]:
    """
    清除 scroll 查询上下文，释放资源
    
    参数:
        scrollId: 要清除的scroll_id
    """
    if not es_connected:
        return {"error": "Elasticsearch 连接不可用，请检查连接配置或稍后重试"}
    try:
        results = await clear_scroll(scrollId)
        return results
    except Exception as e:
        logger.error(f"清除scroll上下文失败: {str(e)}")
        return {"error": str(e)}

@fastmcp.tool(name="get_cluster_health")
async def mcp_get_cluster_health() -> Dict[str, Any]:
    """
    获取 Elasticsearch 集群健康状态信息
    """
    if not es_connected:
        return {"error": "Elasticsearch 连接不可用，请检查连接配置或稍后重试"}
    try:
        health = await get_cluster_health()
        return health
    except Exception as e:
        logger.error(f"获取集群健康状态失败: {str(e)}")
        return {"error": str(e)}

@fastmcp.tool(name="get_cluster_stats")
async def mcp_get_cluster_stats() -> Dict[str, Any]:
    """
    获取 Elasticsearch 集群运行状态统计信息
    """
    if not es_connected:
        return {"error": "Elasticsearch 连接不可用，请检查连接配置或稍后重试"}
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
    parser.add_argument(
        "--no-connection-check",
        action="store_true",
        help="跳过 Elasticsearch 连接检查，即使连接失败也启动服务器"
    )
    parser.add_argument(
        "--retry-count",
        type=int,
        default=3,
        help="Elasticsearch 连接失败时的重试次数，默认为 3"
    )
    parser.add_argument(
        "--retry-interval",
        type=int,
        default=2,
        help="Elasticsearch 连接失败后的重试间隔（秒），默认为 2"
    )
    parser.add_argument(
        "--quick-shutdown",
        action="store_true",
        help="使用快速关闭模式，按Ctrl+C时立即退出，不等待连接关闭"
    )
    parser.add_argument(
        "--force-exit",
        action="store_true",
        help="使用强制退出模式，完全绕过优雅关闭流程，立即终止进程"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="指定日志文件路径，将日志信息写入该文件"
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

async def prepare_server(args):
    """准备服务器启动前的工作"""
    global es_connected
    
    # 测试与 Elasticsearch 的连接
    es_connected = await test_es_connection(args.retry_count, args.retry_interval, args.no_connection_check)
    
    if not es_connected and not args.no_connection_check:
        raise Exception("无法连接到 Elasticsearch，启动失败。如果要在无法连接的情况下启动服务器，请使用 --no-connection-check 选项。")
    
    # 列出所有可用的工具
    await list_available_tools()
    
    if not es_connected:
        logger.warning("服务器将在降级模式下运行，所有 Elasticsearch 工具将返回错误状态")

def main():
    """主程序入口"""
    args = parse_args()
    
    # 处理强制退出
    if args.force_exit:
        def force_exit():
            print("\n强制终止进程", file=sys.stderr)
            os._exit(0)
        
        # 注册强制退出函数
        atexit.register(force_exit)
        
        # 完全绕过uvicorn的信号处理
        os.environ["UVICORN_NO_SIGNAL_HANDLERS"] = "1"
        
        # 自定义信号处理
        def force_exit_handler(sig, frame):
            print("\n收到信号，强制终止进程", file=sys.stderr)
            os._exit(0)
            
        signal.signal(signal.SIGINT, force_exit_handler)
        signal.signal(signal.SIGTERM, force_exit_handler)
        
        logger.info("已启用强制退出模式，按Ctrl+C将立即终止进程")
    
    # 设置日志级别
    if args.debug:
        logger.setLevel(logging.DEBUG)
        # 设置其他库的日志级别
        logging.getLogger("mcp").setLevel(logging.DEBUG)
        logging.getLogger("elasticsearch").setLevel(logging.DEBUG)
        logging.getLogger("elasticsearch7").setLevel(logging.DEBUG)
    
    # 如果指定了日志文件，则添加文件处理器
    if args.log_file:
        file_handler = logging.FileHandler(args.log_file)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        # 确保文件处理器使用与根日志记录器相同的级别
        file_handler.setLevel(logger.level)
        # 将文件处理器添加到根日志记录器，这样所有模块的日志都会写入文件
        logging.getLogger().addHandler(file_handler)
        logger.info(f"日志将写入文件: {args.log_file}")
    
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
        # 设置信号处理
        setup_signal_handlers(args.quick_shutdown)
        
        # SSE模式时设置更合理的超时时间
        if args.transport == "sse":
            # 设置非常短的超时，让uvicorn更快关闭
            os.environ["UVICORN_TIMEOUT_KEEP_ALIVE"] = "1"
            os.environ["UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN"] = "1"
            
            # 配置更多Uvicorn关闭参数
            os.environ["UVICORN_RELOAD"] = "false"  # 禁用热重载以避免进程问题
            os.environ["UVICORN_TIMEOUT_NOTIFY"] = "1"  # 通知连接关闭的时间
            os.environ["UVICORN_WORKERS"] = "1"  # 只使用一个工作进程更容易关闭
            os.environ["UVICORN_LOG_LEVEL"] = "warning"  # 减少日志噪音
        
        # 运行准备工作
        asyncio.run(prepare_server(args))
        
        # 如果是 SSE 模式，设置 uvicorn 参数
        if args.transport == "sse":
            logger.info(f"SSE 服务器监听: {args.sse_host}:{args.sse_port}")
            # 直接设置 FastMCP 的端口
            fastmcp.settings.port = args.sse_port
            fastmcp.settings.host = args.sse_host
        
        # 启动 MCP 服务器
        logger.info("MCP 服务器启动中，按 Ctrl+C 可以退出程序...")
        # 使用命令行参数中的传输模式
        fastmcp.run(transport=args.transport)
    except KeyboardInterrupt:
        # 如果启用了快速关闭，直接退出
        if args.quick_shutdown:
            logger.info("接收到中断信号，直接退出...")
            os._exit(0)
        else:
            # 否则尝试优雅关闭
            logger.info("接收到中断信号 (Ctrl+C)，正在关闭服务器...")
            shutdown_resources()
            logger.info("MCP 服务器已关闭")
            os._exit(0)  # 使用os._exit()强制退出
    except Exception as e:
        error_str = f"MCP 服务器启动失败: {str(e)}"
        logger.error(error_str)
        if args.debug:
            logger.error(traceback.format_exc())
        shutdown_resources()
        os._exit(1)  # 使用os._exit()强制退出

def setup_signal_handlers(quick_shutdown=False):
    """设置信号处理函数"""
    if quick_shutdown:
        # 快速关闭模式，直接退出
        def quick_exit_handler(sig, frame):
            import sys
            sys.stderr.write(f"接收到信号 {sig}，正在强制退出...\n")
            sys.stderr.flush()
            os._exit(0)  # 立即退出进程
            
        # 注册强制退出信号处理
        signal.signal(signal.SIGINT, quick_exit_handler)
        signal.signal(signal.SIGTERM, quick_exit_handler)
        logger.info("启用快速退出模式，按 Ctrl+C 将立即终止程序")
    else:
        # 正常关闭模式，先清理资源再退出
        def graceful_exit_handler(sig, frame):
            logger.info(f"接收到信号 {sig}，正在关闭服务器...")
            shutdown_resources()
            logger.info("服务器已关闭，正在退出...")
            os._exit(0)
            
        # 注册正常退出信号处理
        signal.signal(signal.SIGINT, graceful_exit_handler)
        signal.signal(signal.SIGTERM, graceful_exit_handler)

def shutdown_resources():
    """关闭所有资源和后台任务（当前无后台任务）"""
    logger.info("所有资源已关闭")

async def test_es_connection(retry_count=3, retry_interval=2, skip_check=False):
    """
    测试与 Elasticsearch 的连接，支持重试机制
    
    参数:
        retry_count: 连接失败时的重试次数
        retry_interval: 重试间隔（秒）
        skip_check: 是否跳过连接检查
        
    返回:
        bool: 连接是否成功
    """
    # 如果设置了跳过连接检查，直接返回
    if skip_check:
        logger.warning("跳过 Elasticsearch 连接检查，服务器将以降级模式启动")
        return False
    
    from es_mcp_server.client import create_es_client
    
    logger.info("正在测试与 Elasticsearch 的连接...")
    
    for attempt in range(retry_count + 1):
        try:
            async with create_es_client() as client:
                info = await client.info()
                logger.info(f"Elasticsearch 连接成功! 版本: {info['version']['number']}")
                return True
        except Exception as e:
            if attempt < retry_count:
                logger.warning(f"Elasticsearch 连接失败 (尝试 {attempt+1}/{retry_count+1}): {str(e)}")
                logger.info(f"将在 {retry_interval} 秒后重试...")
                
                # 提供连接建议
                await _provide_connection_suggestions(e)
                
                # 延迟重试
                await asyncio.sleep(retry_interval)
            else:
                logger.error(f"Elasticsearch 连接失败，已达到最大重试次数: {str(e)}")
                await _provide_connection_suggestions(e)
                return False

async def _provide_connection_suggestions(error):
    """根据错误类型提供连接建议"""
    error_str = str(error).lower()
    
    if "connectionrefused" in error_str:
        logger.info(f"建议: 确认 Elasticsearch 是否已在 {es_config.host}:{es_config.port} 启动")
        logger.info("您可以使用 curl 命令测试 Elasticsearch 连接: " +
                  f"curl -X GET http://{es_config.host}:{es_config.port}")
        
    elif "unauthorized" in error_str or "authentication" in error_str:
        logger.info("建议: 检查提供的用户名和密码是否正确")
        
    elif "timeouterror" in error_str:
        logger.info(f"建议: 检查防火墙规则是否允许连接 {es_config.host}:{es_config.port}")
        
    elif "ssl" in error_str or "certificate" in error_str:
        logger.info("建议: 检查 SSL/TLS 配置，可以尝试设置 ES_VERIFY_CERTS=false")
        
    else:
        logger.info("建议: 检查 Elasticsearch 连接配置和网络状态")
        logger.info(f"连接参数: host={es_config.host}, port={es_config.port}, version={es_config.es_version}")

if __name__ == "__main__":
    main() 