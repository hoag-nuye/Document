package com.yourorg.mcp.mysql_server.service;

import com.yourorg.mcp.mysql_server.model.ToolModel;
import com.yourorg.mcp.mysql_server.repository.ToolRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.List;
import java.util.Map;

@Service
public class MCPServerService {

    @Autowired
    private ToolRepository toolRepository;

    private final RestTemplate restTemplate = new RestTemplate();

    public String executeTool(String toolName, String parameters) {
        ToolModel tool = toolRepository.findByName(toolName)
                .orElseThrow(() -> new RuntimeException("Tool not found"));

        HttpHeaders headers = new HttpHeaders();
        HttpEntity<String> request = new HttpEntity<>(parameters, headers);

        return restTemplate.exchange(
            tool.getEndpoint(),
            HttpMethod.valueOf(tool.getMethod()),
            request,
            String.class
        ).getBody();
    }

    public List<ToolModel> getTools() {
        return toolRepository.findAll();
    }

    public void addTool(Map<String, Object> toolData) {
        ToolModel tool = new ToolModel();
        tool.setName((String) toolData.get("name"));
        tool.setDescription((String) toolData.get("description"));
        tool.setEndpoint((String) toolData.get("endpoint"));
        tool.setMethod((String) toolData.get("method"));
        tool.setParameters((String) toolData.get("parameters"));

        toolRepository.save(tool);
    }
} 