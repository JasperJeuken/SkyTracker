import axios, { AxiosError } from "axios";


export const apiClient = axios.create({
    baseURL: import.meta.env.API_BASE_URL || "http://localhost:8000/api/v1",
    timeout: 10000,
});


apiClient.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
        if (error.response) {
            // console.error("API error:", {
            //     status: error.response.status,
            //     message: error.response.statusText,
            //     data: error.response.data,
            // });
            throw new Error(`API request failed (${error.response.status}): ${error.response.statusText}`);
        } else if (error.request) {
            // console.error("No response from server:", error.message);
            throw new Error("No response from server");
        } else {
            // console.error("Request error:", error.message);
            throw new Error(`Request error: ${error.message}`)
        }
    }
);
