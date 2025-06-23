# MCP Client SDK

This SDK provides client libraries for interacting with the Model Context Protocol (MCP) Server in both Python and Java.

## Python SDK

### Installation

```bash
pip install -r python/requirements.txt
```

### Usage

```python
from mcp_client import MCPClient

# Initialize client
client = MCPClient(host='localhost', port=9090)

# Execute a tool
result = client.execute_tool('tool_name', {
    'param1': 'value1',
    'param2': 'value2'
})

# Get available tools
tools = client.get_tools()

# Add a new tool
success = client.add_tool({
    'name': 'new_tool',
    'description': 'Tool description',
    'endpoint': 'http://example.com/api',
    'method': 'POST',
    'parameters': {
        'param1': 'string',
        'param2': 'number'
    }
})

# Close the client
client.close()
```

## Java SDK

### Installation

Add the following dependency to your `pom.xml`:

```xml
<dependency>
    <groupId>com.yourorg.mcp</groupId>
    <artifactId>mcp-client-sdk</artifactId>
    <version>1.0.0</version>
</dependency>
```

### Usage

```java
import com.yourorg.mcp.client.MCPClient;
import java.util.Map;
import java.util.List;

// Initialize client
MCPClient client = new MCPClient("localhost", 9090);

// Execute a tool
Map<String, Object> result = client.executeTool("tool_name", Map.of(
    "param1", "value1",
    "param2", "value2"
));

// Get available tools
List<Map<String, Object>> tools = client.getTools();

// Add a new tool
boolean success = client.addTool(Map.of(
    "name", "new_tool",
    "description", "Tool description",
    "endpoint", "http://example.com/api",
    "method", "POST",
    "parameters", Map.of(
        "param1", "string",
        "param2", "number"
    )
));

// Close the client
client.shutdown();
```

## Features

- Execute tools with parameters
- Get list of available tools
- Add new tools
- Support for both Python and Java
- Type-safe API
- Error handling
- Connection management 