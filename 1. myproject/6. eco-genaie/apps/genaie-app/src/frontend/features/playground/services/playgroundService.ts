import axios from 'axios';
const API_URL = 'http://localhost:3005/';
const AI_AGENT_URL = 'http://localhost:3005/';

const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return { Authorization: `Bearer ${token}` };
};

export const playgroundService = {
  async sendMessage(message: string) {
    return axios.post(
      `${AI_AGENT_URL}/chat`,
      { message },
      { headers: getAuthHeader() }
    );
  },

  async addTool(toolData: any) {
    return axios.post(
      `${API_URL}/playground/tools`,
      toolData,
      { headers: getAuthHeader() }
    );
  },

  async getTools() {
    return axios.get(
      `${API_URL}/playground/tools`,
      { headers: getAuthHeader() }
    );
  },

  async deleteTool(toolId: string) {
    return axios.delete(
      `${API_URL}/playground/tools/${toolId}`,
      { headers: getAuthHeader() }
    );
  },
}; 