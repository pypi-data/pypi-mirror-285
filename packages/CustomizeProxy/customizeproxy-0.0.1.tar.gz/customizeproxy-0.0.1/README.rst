==============
CustomizeProxy
==============

CustomizeProxy 是一个基于  mitmproxy 10.3.1 版本的二次封装版本。

概述
----

CustomizeProxy 是一个允许开发者拦截和修改本地计算机所有网络请求库，在windows平台可自动安装证书。


安装
----

使用 pip 安装 CustomizeProxy ：

.. code-block:: bash

    pip install CustomizeProxy

请注意，由于本项目是 mitmproxy 的封装版本，可能需要从源代码安装或使用特定的安装步骤。

使用示例
--------

以下是一个简单的使用示例，展示如何使用：

.. code-block:: python

    from CustomizeProxy import exec_listening,addons,Optional,mitmproxy
    class HTTPInterceptor:

            def load(self, loader):
                loader.add_option(
                    name="validate_inbound_headers",
                    typespec=Optional[bool],
                    default=False,
                    help="Validate inbound HTTP headers. (default: False)",
                ) # 不检查请求头格式

            def request(self, flow: mitmproxy.http.HTTPFlow):
                print("拦截:",flow.server_conn.address)
   
    if __name__ == '__main__':
        addons.append(HTTPInterceptor())
        exec_listening()

贡献
----

我们欢迎任何形式的贡献，包括但不限于：

- 报告问题或错误。
- 提供功能请求或改进建议。

许可证
------

本项目采用 MIT 许可证。有关更多信息，请查看 `LICENSE` 文件。
