// src/infrastructure/http/apiClient.ts
import axios, {
  AxiosError,
  type AxiosInstance,
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
  type AxiosRequestHeaders,
} from 'axios';
import { ENV } from '../../shared/env';
import { API_ENDPOINTS } from '../../shared/endpoints';
import { tokenStorage } from '../../infrastructure/storage/tokenStorage';

/**
 * Refresh response attendu depuis le backend (SimpleJWT rotation)
 */
type RefreshResponse = {
  access?: string;
  refresh?: string;
};

/**
 * Extends AxiosRequestConfig pour stocker un flag interne _retry
 * (utile pour éviter boucle infinie de refresh)
 */
type OriginalRequest = AxiosRequestConfig & { _retry?: boolean };

/**
 * Axios instance configurée :
 * - Attache le Bearer access token si présent
 * - Intercepte les 401 -> tente un refresh (file d’attente pour éviter multi-refresh)
 */
export const apiClient: AxiosInstance = axios.create({
  baseURL: ENV.apiBaseUrl,
  withCredentials: false,
});

// --- Gestion de la queue de refresh pour éviter les courses multiples ---
let isRefreshing = false;
let pendingQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
  originalRequest: OriginalRequest;
}> = [];

/**
 * Normalise et injecte l'Authorization header sur la requête en file d'attente.
 * On évite `any` en utilisant AxiosRequestHeaders / Record<string,string>.
 */
function processQueue(error: unknown, token: string | null) {
  pendingQueue.forEach(({ resolve, reject, originalRequest }) => {
    if (error) {
      reject(error);
      return;
    }

    if (token) {
      // originalRequest.headers peut être de différents shapes -> normalise en plain object
      const existingHeaders =
        (originalRequest.headers as AxiosRequestHeaders | undefined) ?? {};
      // construire un objet de headers simple de type Record<string,string>
      const normalized: Record<string, string> = {
        // spread existing headers (transform values to string where possible)
        ...Object.fromEntries(
          Object.entries(existingHeaders).map(([k, v]) => [
            k,
            String((v as unknown) ?? ''),
          ]),
        ),
        Authorization: `Bearer ${token}`,
      };
      originalRequest.headers = normalized as unknown as AxiosRequestHeaders;
    }

    // relancer la requête originale
    resolve(apiClient.request(originalRequest));
  });
  pendingQueue = [];
}

// --- Request: inject Authorization ---
// utilise InternalAxiosRequestConfig (type attendu par axios interceptors)
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const access = tokenStorage.getAccess();

  // assure que headers est un objet plain (Record<string,string>) pour éviter les problèmes de type
  const existing = (config.headers as AxiosRequestHeaders | undefined) ?? {};
  const normalizedHeaders: Record<string, string> = Object.fromEntries(
    Object.entries(existing).map(([k, v]) => [k, String((v as unknown) ?? '')]),
  );

  if (access) {
    normalizedHeaders['Authorization'] = `Bearer ${access}`;
  }

  // Réaffecte en type attendu par axios
  config.headers = normalizedHeaders as unknown as AxiosRequestHeaders;

  return config;
});

// --- Response: handle 401 -> refresh ---
apiClient.interceptors.response.use(
  (res) => res,
  async (error: AxiosError<unknown>) => {
    const originalRequest = error.config as OriginalRequest | undefined;

    // Si pas de config ou pas de 401 -> on propage
    if (!originalRequest || error.response?.status !== 401) {
      return Promise.reject(error);
    }

    // Éviter boucle infinie: si on tente déjà un refresh pour cette requête
    if (originalRequest._retry) {
      return Promise.reject(error);
    }
    originalRequest._retry = true;

    // Si le 401 vient de /refresh lui-même -> on échoue (logout)
    const url = originalRequest.url ?? '';
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
        pendingQueue.push({
          resolve,
          reject,
          originalRequest,
        });
      });
    }

    // Lancer un refresh
    isRefreshing = true;
    try {
      const resp = await axios.post<RefreshResponse>(
        ENV.apiBaseUrl + API_ENDPOINTS.refresh,
        { refresh: refreshToken },
        { withCredentials: false },
      );

      const newAccess: string | undefined = resp.data?.access;
      const newRefresh: string | undefined = resp.data?.refresh;

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
  },
);
