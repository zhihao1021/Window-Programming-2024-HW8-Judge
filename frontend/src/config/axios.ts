import axios, { AxiosError } from "axios";
import { jwtDecode } from "jwt-decode";

let dealError: (error: AxiosError) => any = (error) => {
    throw error;
};

export function setDealError(func: (error: AxiosError) => any) {
    dealError = func;
}

export function setRequestConfig() {
    axios.interceptors.request.use(async (config) => {
        config.baseURL = process.env.REACT_APP_API_END_POINT;

        let tokenType = localStorage.getItem("token_type");
        let token = localStorage.getItem("access_token");

        // if JWT exist, put it into header
        if (token !== null && tokenType !== null) {
            let decodeData = jwtDecode(token);
            if (decodeData.exp && decodeData.exp < Date.now() / 1000) {
                localStorage.removeItem("access_token");
                localStorage.removeItem("token_type");
                window.location.reload();
            }
            config.headers.Authorization = `${tokenType} ${token}`;
        }
        return config;
    });
};

export function setResponseConfig() {
    axios.interceptors.response.use(
        response => response,
        (error) => {
            return dealError(error);
        }
    )
};
