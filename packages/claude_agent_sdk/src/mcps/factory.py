from .tools.calculate import calculate

def define_mcp_servers():
    return [
        {
            "name": "utils",
            "version": "1.0.0",
            "tools": [calculate]
        }
    ]
