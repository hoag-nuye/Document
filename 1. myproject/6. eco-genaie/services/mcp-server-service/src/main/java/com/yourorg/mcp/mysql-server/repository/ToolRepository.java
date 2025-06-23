package com.yourorg.mcp.mysql_server.repository;

import com.yourorg.mcp.mysql_server.model.ToolModel;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface ToolRepository extends JpaRepository<ToolModel, Long> {
    Optional<ToolModel> findByName(String name);
} 