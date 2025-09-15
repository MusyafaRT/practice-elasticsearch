// src/services/axiosInstance.ts
import axios from "axios";
import { useAuthStore } from "../stores/useAuthStore";

export const BASE_URL = "http://localhost:8000";

const axiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
    "App-Version": 1,
  },
});

axiosInstance.interceptors.request.use((config) => {
  const { token } = useAuthStore.getState();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const { refreshToken } = useAuthStore.getState();
        const refreshResponse = await axios.post(
          `${BASE_URL}/auth/refresh`,
          { refreshToken },
          { withCredentials: true }
        );

        const {
          accessToken,
          refreshToken: newRefreshToken,
          user,
        } = refreshResponse.data.data;

        useAuthStore.getState().login(accessToken, newRefreshToken, user);

        originalRequest.headers.Authorization = `Bearer ${accessToken}`;
        return axiosInstance(originalRequest);
      } catch (refreshError) {
        useAuthStore.getState().logout();
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default axiosInstance;
