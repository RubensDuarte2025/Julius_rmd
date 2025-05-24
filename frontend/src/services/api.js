import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api', // URL base do backend Django
  // timeout: 10000, // Exemplo de timeout
  // headers: { 'Content-Type': 'application/json' }
});

// Opcional: Interceptor para adicionar token de autenticação (Pós-MVP)
// apiClient.interceptors.request.use(config => {
//   const token = localStorage.getItem('authToken');
//   if (token) {
//     config.headers.Authorization = `Bearer ${token}`;
//   }
//   return config;
// }, error => {
//   return Promise.reject(error);
// });

export default apiClient;
