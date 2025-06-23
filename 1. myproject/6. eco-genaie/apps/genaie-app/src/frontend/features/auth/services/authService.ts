import axios from 'axios';

const API_URL = 'http://localhost:3005/' ;

export const authService = {
  async login(email: string, password: string) {
    return axios.post(`${API_URL}/auth/login`, { email, password });
  },

  async register(email: string, password: string, name: string) {
    return axios.post(`${API_URL}/auth/register`, { email, password, name });
  },

  async getProfile() {
    const token = localStorage.getItem('token');
    return axios.get(`${API_URL}/auth/profile`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  },
}; 