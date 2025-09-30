// src/infrastructure/http/apiClient.ts
import axios, {
  AxiosError,
  type AxiosInstance,
  type AxiosRequestConfig,
} from 'axios';
import { ENV } from '../../shared/env';
import { API_ENDPOINTS } from '../../shared/endpoints';
import { tokenStorage } from '../../infrastructure/storage/tokenStorage';

type RefreshResponse = { access?: string; refresh?: string };
type OriginalRequest = AxiosRequestConfig & { _retry?: boolean };

export const apiClient: AxiosInstance = axios.create({
  baseURL: ENV.apiBaseUrl,
  withCredentials: false,
  headers: {
    Accept: 'application/json',
  },
});

/**
 * Typage sécurisé pour defaults.headers d'Axios.
 * On cast via unknown -> shape partielle explicitée pour éviter `any`.
 */
type PartialAxiosDefaultsHeaders = {
  common?: Record<string, string>;
  get?: Record<string, string>;
  post?: Record<string, string>;
  put?: Record<string, string>;
  patch?: Record<string, string>;
  delete?: Record<string, string>;
  [key: string]: Record<string, string> | string | undefined;
};

const headersDefaults = apiClient.defaults
  .headers as unknown as PartialAxiosDefaultsHeaders;

// Assure JSON par défaut pour POST (évite le 415)
headersDefaults.post = {
  ...(headersDefaults.post ?? {}),
  'Content-Type': 'application/json',
};

headersDefaults.patch = {
  ...(headersDefaults.patch ?? {}),
  'Content-Type': 'application/json',
};
headersDefaults.put = {
  ...(headersDefaults.put ?? {}),
  'Content-Type': 'application/json',
};

// --- refresh queue ---
let isRefreshing = false;
let pendingQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
  originalRequest: OriginalRequest;
}> = [];

function processQueue(error: unknown, token: string | null) {
  pendingQueue.forEach(({ resolve, reject, originalRequest }) => {
    if (error) return reject(error);
    if (token) {
      originalRequest.headers = {
        ...(originalRequest.headers || {}),
        Authorization: `Bearer ${token}`,
      };
    }
    resolve(apiClient.request(originalRequest));
  });
  pendingQueue = [];
}

// --- Request: ajoute seulement Authorization, NE PAS remplacer headers ---
apiClient.interceptors.request.use((config) => {
  const access = tokenStorage.getAccess();
  if (access) {
    config.headers = config.headers || {};
    (config.headers as Record<string, string>)['Authorization'] =
      `Bearer ${access}`;
  }
  // DEBUG TEMP:

  console.debug('[api] =>', config.method?.toUpperCase(), config.url, {
    hasAuth: Boolean(access),
    authHead: access ? `Bearer ${access.slice(0, 12)}…` : null,
  });
  return config;
});

// --- Response: handle 401 -> refresh ---
apiClient.interceptors.response.use(
  (res) => res,
  async (error: AxiosError<unknown>) => {
    const originalRequest = error.config as OriginalRequest | undefined;
    if (!originalRequest || error.response?.status !== 401) {
      return Promise.reject(error);
    }
    if (originalRequest._retry) return Promise.reject(error);
    originalRequest._retry = true;

    const url = originalRequest.url ?? '';
    if (url.includes(API_ENDPOINTS.refresh)) return Promise.reject(error);

    const refreshToken = tokenStorage.getRefresh();
    if (!refreshToken) return Promise.reject(error);

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        pendingQueue.push({ resolve, reject, originalRequest });
      });
    }

    isRefreshing = true;
    try {
      const resp = await axios.post<RefreshResponse>(
        ENV.apiBaseUrl + API_ENDPOINTS.refresh,
        { refresh: refreshToken },
        {
          withCredentials: false,
          headers: {
            'Content-Type': 'application/json',
            Accept: 'application/json',
          },
        },
      );

      const newAccess = resp.data?.access;
      const newRefresh = resp.data?.refresh;
      if (!newAccess) throw new Error('Refresh OK mais access manquant');

      tokenStorage.setAccess(newAccess);
      if (newRefresh) tokenStorage.setRefresh(newRefresh);

      processQueue(null, newAccess);
      return apiClient(originalRequest);
    } catch (err) {
      tokenStorage.clearAll();
      processQueue(err, null);
      return Promise.reject(err);
    } finally {
      isRefreshing = false;
    }
  },
);
