import axios, { AxiosError, type AxiosInstance, type AxiosRequestConfig } from 'axios';
import { ENV } from '../../shared/env';
import { API_ENDPOINTS } from '../../shared/endpoints';
import { tokenStorage } from '../../infrastructure/storage/tokenStorage';

/**
 * Axios instance configurée :
 * - Attache le Bearer access token si présent
 * - Intercepte les 401 -> tente un refresh (file d’attente pour éviter multi-refresh)
 */

export const apiClient: AxiosInstance = axios.create({
  baseURL: ENV.apiBaseUrl,
  withCredentials: false, // true si tu utilises des cookies côté back
});

// --- Gestion de la queue de refresh pour éviter les courses multiples ---
let isRefreshing = false;
let pendingQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
  originalRequest: AxiosRequestConfig;
}> = [];

function processQueue(error: unknown, token: string | null) {
  pendingQueue.forEach(({ resolve, reject, originalRequest }) => {
    if (error) {
      reject(error);
    } else {
      if (token && originalRequest.headers) {
        (originalRequest.headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
      }
      resolve(apiClient.request(originalRequest));
    }
  });
  pendingQueue = [];
}

// --- Request: inject Authorization ---
apiClient.interceptors.request.use((config) => {
  const access = tokenStorage.getAccess();
  if (access && config.headers) {
    (config.headers as Record<string, string>)['Authorization'] = `Bearer ${access}`;
  }
  return config;
});

// --- Response: handle 401 -> refresh ---
apiClient.interceptors.response.use(
  (res) => res,
  async (error: AxiosError<any>) => {
    const originalRequest = error.config;

    // Si pas de config ou pas de 401 -> on propage
    if (!originalRequest || error.response?.status !== 401) {
      return Promise.reject(error);
    }

    // Éviter boucle infinie: si on tente déjà un refresh pour cette requête
    if ((originalRequest as any)._retry) {
      return Promise.reject(error);
    }
    (originalRequest as any)._retry = true;

    // Si le 401 vient de /refresh lui-même -> on échoue (logout)
    const url = originalRequest.url || '';
    if (url.includes(API_ENDPOINTS.refresh)) {
      return Promise.reject(error);
    }

    const refreshToken = tokenStorage.getRefresh();
    if (!refreshToken) {
      // Pas de refresh -> on échoue
      return Promise.reject(error);
    }

    // Si déjà en refresh -> enqueue
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        pendingQueue.push({ resolve, reject, originalRequest });
      });
    }

    // Lancer un refresh
    isRefreshing = true;
    try {
      const { data } = await axios.post(
        ENV.apiBaseUrl + API_ENDPOINTS.refresh,
        { refresh: refreshToken },
        { withCredentials: false }
      );

      const newAccess: string | undefined = data?.access;
      const newRefresh: string | undefined = data?.refresh;

      if (!newAccess) {
        throw new Error('Refresh OK mais access manquant');
      }

      // Met à jour les tokens en storage
      tokenStorage.setAccess(newAccess);
      if (newRefresh) tokenStorage.setRefresh(newRefresh);

      // Relance la queue avec le nouveau token
      processQueue(null, newAccess);
      return apiClient(originalRequest);
    } catch (err) {
      // Refresh échoué -> purge tokens
      tokenStorage.clearAll();
      processQueue(err, null);
      return Promise.reject(err);
    } finally {
      isRefreshing = false;
    }
  }
);
