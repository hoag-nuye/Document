package com.yourorg.mcp.mysql_server.controller;

import com.yourorg.mcp.mysql_server.service.MCPServerService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/mcp")
@CrossOrigin(origins = "*")
public class MCPServerController {

    @Autowired
    private MCPServerService mcpServerService;

    @PostMapping("/execute")
    public ResponseEntity<?> executeTool(@RequestBody Map<String, String> request) {
        try {
            String result = mcpServerService.executeTool(
                request.get("tool_name"),
                request.get("parameters")
            );
            return ResponseEntity.ok(Map.of("result", result));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }

    @GetMapping("/tools")
    public ResponseEntity<?> getTools() {
        try {
            return ResponseEntity.ok(mcpServerService.getTools());
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }

    @PostMapping("/tools")
    public ResponseEntity<?> addTool(@RequestBody Map<String, Object> tool) {
        try {
            mcpServerService.addTool(tool);
            return ResponseEntity.ok().build();
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }
} 