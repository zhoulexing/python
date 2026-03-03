import axios from "axios";

const request = axios.create({
  baseURL: "/api",
  timeout: 30_000,
});

request.interceptors.response.use(
  (res) => res.data,
  (err) => Promise.reject(err),
);

export default request;
