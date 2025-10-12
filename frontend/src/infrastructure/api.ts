import axios from 'axios';
import { ENV } from '../shared/env';

export const api = axios.create({
  baseURL: ENV.apiBaseUrl || 'http://localhost:8000/api', // fallback dev sensé
});
