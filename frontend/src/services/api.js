import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const searchCorpus = async (query, filters = {}) => {
  const response = await axios.post(`${API_BASE_URL}/search`, {
    query,
    court: filters.court || '',
    year: filters.year || '',
    document_type: filters.document_type || '',
    top_k: 20
  });
  return response.data;
};

export const getCaseDetails = async (caseId) => {
  const response = await axios.get(`${API_BASE_URL}/cases/${caseId}`);
  return response.data;
};

export const getHealthStatus = async () => {
  const response = await axios.get(`${API_BASE_URL}/health`);
  return response.data;
};
