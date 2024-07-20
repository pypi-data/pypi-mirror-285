class ToolManager:
    def __init__(self):
        self.tools = {}

    def add_tool(self, tool_name: str, tool):
        self.tools[tool_name] = tool

    def use_tool(self, tool_name: str, *args, **kwargs):
        if tool_name in self.tools:
            return self.tools[tool_name](*args, **kwargs)
        return "Tool not found."