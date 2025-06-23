package com.yourorg.mcp.client;

import com.google.gson.Gson;
import com.yourorg.mcp.proto.*;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class MCPClient {
    private final ManagedChannel channel;
    private final MCPServiceGrpc.MCPServiceBlockingStub blockingStub;
    private final Gson gson = new Gson();

    public MCPClient(String host, int port) {
        this.channel = ManagedChannelBuilder.forAddress(host, port)
                .usePlaintext()
                .build();
        this.blockingStub = MCPServiceGrpc.newBlockingStub(channel);
    }

    public Map<String, Object> executeTool(String toolName, Map<String, Object> parameters) {
        ToolRequest request = ToolRequest.newBuilder()
                .setToolName(toolName)
                .setParameters(gson.toJson(parameters))
                .build();

        ToolResponse response = blockingStub.executeTool(request);
        if (!response.getSuccess()) {
            throw new RuntimeException(response.getError());
        }

        return gson.fromJson(response.getResult(), Map.class);
    }

    public List<Map<String, Object>> getTools() {
        GetToolsRequest request = GetToolsRequest.getDefaultInstance();
        GetToolsResponse response = blockingStub.getTools(request);

        return response.getToolsList().stream()
                .map(this::convertTool)
                .collect(Collectors.toList());
    }

    public boolean addTool(Map<String, Object> tool) {
        Tool toolProto = Tool.newBuilder()
                .setName((String) tool.get("name"))
                .setDescription((String) tool.get("description"))
                .setEndpoint((String) tool.get("endpoint"))
                .setMethod((String) tool.get("method"))
                .setParameters(gson.toJson(tool.get("parameters")))
                .build();

        AddToolRequest request = AddToolRequest.newBuilder()
                .setTool(toolProto)
                .build();

        AddToolResponse response = blockingStub.addTool(request);
        return response.getSuccess();
    }

    private Map<String, Object> convertTool(Tool tool) {
        return Map.of(
            "name", tool.getName(),
            "description", tool.getDescription(),
            "endpoint", tool.getEndpoint(),
            "method", tool.getMethod(),
            "parameters", gson.fromJson(tool.getParameters(), Map.class)
        );
    }

    public void shutdown() {
        channel.shutdown();
    }
} 