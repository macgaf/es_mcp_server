# 总体需求
本项目的目的是基于[modelcontextprotocol的python sdk](https://github.com/modelcontextprotocol/python-sdk)
（可以通过
pip install mcp
来安装），构建一个elasticsearch（以下简称es）的mcp服务器，实现一系列的tools来对接es的基本操作

# 功能需求
## 提供下列mcp工具
1. 索引查询，列表显示集群的所有索引
2. 输入索引名称，获取索引的mapping
3. 输入索引的名称，query条件以及是否返回所有文档bool值，根据是否返回文档bool值决定是否返回符合条件的所有docments，同时返回聚合的所有的统计信息
4. 获取es集群的运行状态信息
5. 获取es集群的健康状态信息
## 上述所有的工具满足如下要求
1. 通过mcp.server.fastmcp包的FastMCP类来创建实例fastmcp，基于@fastmcp.tool()用annotation函数的方式来定义工具
2. 工具的名称、描述都在@fastmcp.tool()注解的参数中定义，这种方式不需要显式描述工具的参数

# 其他需求
1. 基于包名来创建目录结构，不要重复创建目录
2. 服务器主程序，包名es_mcp_server,所有服务端代码都在该目录下
   1. 入口为es_mcp_server.server
   2. 支持uvx启动
   3. 同时支持支持对接es7 和es8服务器
      1. 针对es服务器的版本，需要使用不同版本的es库支持，也就是说本项目要同时支持v7 和v8的库
      2. 对于es7
         1. 客户端库为elasticsearch7
         2. es api调用时，从response中获取返回数据
         3. 用户名密码使用http_auth
         4. 使用 ssl 而不是 tls 进行 SSL/TLS 配置
      3. 对于es8
         1. 客户端库为elasticsearch
         2. es api调用是，直接从response.body中获取返回数据
         3. 用户名密码使用basic_auth
      4. 异步方式访问es服务器
   4. 支持用户名口令模式、支持api key 模式
      1. 支持环境变量
      2. 支持配置文件中进行配置
   5. 同时支持stdio和sse两种transport模式
      1. 前面定义的fastmcp.run(transport='stdio')来实现stdio
      2. 前面定义的fastmcp.run(transport='sse')来实现sse即可，不要显式去启动其他的web服务
   6. 提供命令行的开关，实现将log写入指定的文件
3. 提供一个客户端的程序，以验证服务的有效性,包名es_mcp_client，所有客户端代码都在该目录下
   1. 基于mcp.client.sse包的sse_client来实现
   2. 主程序入口为es_mcp_client.client
   3. 支持uvx启动
   4. 提供命令行的开关，实现将log写入指定的文件
4. 使用hatchling来打包构建能力，能发布可安装、运行的包
   1. 检查依赖的包是否存在，如果不存在，提前中止
   2. 添加pytest的开发依赖
5. 单元测试支持
   1. 为服务端和客户端程序提供所有单元测试，包名test
   2. 在项目工程描述中，提供dev依赖选项，支持可选的pytest依赖支持
6.  提供一个claude desktop的mcpServers配置demo（json文件，放在/claude_config_examples目录下），以便于说明如何在claude client中如何使用本mcp server，该配置包含如下配置实例
   1.  一个Elasticsearch的stdio方式运行的mcp server实例
       1.  需要按照最新的MCP规范提供配置，使用对象格式（非数组格式），包含command、args、env等参数，其形式语言描述如下
   
   
   ``` bnf
   <config>       ::= { "mcpServers": <servers> }
   <servers>      ::= { <serverName>: <serverConfig> }
   <serverName>   ::=  <string>   // 可扩展为其他服务器名
   <serverConfig> ::= { "command" : "uvx" ,
                        "args" : [ "es-mcp-server" ],
                        "env" : [ <envs> ]
                      }  
   <envs>       ::= <kv> (, <kv>)*
   <kv>         ::= <k> : <v>
   <k>          ::= "ES_HOST" | "ES_PORT" | "ES_USERNAME"| "ES_PASSPORT" ...
   <v>          ::= <string>

   ```

       2.  样例配置细节类似 @https://github.com/ahujasid/blender-mcp?tab=readme-ov-file#claude-for-desktop-integration
   2.  一个Elasticsearch的sse方式运行的mcp server实例
       1.  其形式语言描述如下：
   ``` bnf
   <config>       ::= { "mcpServers": <servers> }
   <servers>      ::= { <serverName>: <serverConfig> }
   <serverName>   ::=  <string>   // 可扩展为其他服务器名
   <serverConfig> ::= { "url" : "http://<hostname>:<port>/sse"       }  
   ```
       2.  样例配置细节类似 @https://github.com/co-browser/browser-use-mcp-server?tab=readme-ov-file#sse-mode-client-configuration
7.  提供markdown格式的readme文件
    1.  内容包括
        1.  本项目的目录结构
        2.  服务器的功能和使用说明
        3.  客户端使用说明
        4.  对接其他工具的使用方法（以对接claude的客户端来说明）
        5.  注明：本项目的大部分代码、文档、配置示例都是用cursor的claude-3.7-sonnet根据[需求文档](/docs/requires.md) 生成出来的（提示词：基于本文件生成项目所有程序）。 
    2.  提供中、英、法、德、日等语言版本的readme文件，缺省为中文，
    3.  在readme文件中加入其他语种readme文件的交叉链接，链接的icon为语种对应的国家的国旗表情符号
8.  添加一个.gitignore 文件，将一般python的中间文件和目标文件以及build生成的中间生成文件和目标文件都ignore掉
9.  添加一个在vscode中进行debug 服务端和客户端的配置文件（sse模式），debug 类型为debugpy
10. 添加MIT授权
   


