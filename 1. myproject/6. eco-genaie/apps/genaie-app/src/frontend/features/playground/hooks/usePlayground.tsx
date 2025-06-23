import { useState, useCallback } from 'react';
import { playgroundService } from '../services/playgroundService';

interface Tool {
  id: string;
  name: string;
  description: string;
  endpoint: string;
  method: string;
  parameters: any;
}

export const usePlayground = () => {
  const [tools, setTools] = useState<Tool[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (message: string) => {
    try {
      setLoading(true);
      const response = await playgroundService.sendMessage(message);
      return response;
    } catch (err) {
      setError('Failed to send message');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const addTool = useCallback(async (toolData: Omit<Tool, 'id'>) => {
    try {
      setLoading(true);
      const response = await playgroundService.addTool(toolData);
      setTools((prev) => [...prev, response.data]);
      return response;
    } catch (err) {
      setError('Failed to add tool');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getTools = useCallback(async () => {
    try {
      setLoading(true);
      const response = await playgroundService.getTools();
      setTools(response.data);
      return response;
    } catch (err) {
      setError('Failed to fetch tools');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    tools,
    loading,
    error,
    sendMessage,
    addTool,
    getTools,
  };
}; 