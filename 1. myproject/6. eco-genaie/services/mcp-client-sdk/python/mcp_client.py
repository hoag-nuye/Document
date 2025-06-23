import grpc
import json
from typing import Dict, List, Optional

class MCPClient:
    def __init__(self, host: str = 'localhost', port: int = 9090):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = None  # Will be initialized with generated gRPC stub

    def execute_tool(self, tool_name: str, parameters: Dict) -> Dict:
        """Execute a tool with given parameters."""
        request = {
            'tool_name': tool_name,
            'parameters': json.dumps(parameters)
        }
        response = self.stub.ExecuteTool(request)
        return json.loads(response.result) if response.success else None

    def get_tools(self) -> List[Dict]:
        """Get list of available tools."""
        request = {}
        response = self.stub.GetTools(request)
        return [self._convert_tool(tool) for tool in response.tools]

    def add_tool(self, tool: Dict) -> bool:
        """Add a new tool."""
        request = {'tool': tool}
        response = self.stub.AddTool(request)
        return response.success

    def _convert_tool(self, tool) -> Dict:
        """Convert gRPC tool message to dictionary."""
        return {
            'name': tool.name,
            'description': tool.description,
            'endpoint': tool.endpoint,
            'method': tool.method,
            'parameters': json.loads(tool.parameters)
        }

    def close(self):
        """Close the gRPC channel."""
        self.channel.close() 