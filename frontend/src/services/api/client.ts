import axios, { AxiosError } from "axios";


axios.defaults.headers["X-API-Key"] = import.meta.env.VITE_API_KEY;
export const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1",
    timeout: 10000
});


apiClient.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
        if (error.response) {
            throw new Error(`API request failed (${error.response.status}): ${error.response.statusText}`);
        } else if (error.request) {
            throw new Error("No response from server");
        } else {
            throw new Error(`Request error: ${error.message}`)
        }
    }
);
