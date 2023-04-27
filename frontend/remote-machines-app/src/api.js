// src/api.js
import axios from 'axios';

const baseURL = 'http://localhost:8000'; // Replace with the actual API base URL if different

const api = axios.create({
  baseURL: baseURL,
});

api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default {
  getMachineByIpAddress: (ipAddress) => api.get(`/remote_machines/${ipAddress}`),
  getMachinesByContactInfo: (contactInfo) =>
    api.get(`/remote_machines/contact_info/${contactInfo}`),
  getAllMachines: () => api.get('/remote_machines'),
};
