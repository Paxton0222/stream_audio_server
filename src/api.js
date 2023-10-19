// frontend/src/api.js

import axios from "axios";

// 创建一个基础Axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL,  // 更新为FastAPI的API根路径
});

// Stream相关API请求
const streamApi = {
  add: async (room, channel, url) => await api.post(`/stream/add/${room}/${channel}?url=${url}`),
  play: async (room, channel) => await api.post(`/stream/play/${room}/${channel}`),
  pause: async (room, channel) => await api.post(`/stream/pause/${room}/${channel}`),
  state: async (room, channel) => await api.get(`/stream/state/${room}/${channel}`),
  next: async (room, channel) => await api.post(`/stream/next/${room}/${channel}`),
  list: async (room, channel, page, limit) => await api.get(`/stream/list/${room}/${channel}?page=${page}&limit=${limit}`),
  length: async (room, channel) => await api.get(`/stream/list/length/${room}/${channel}`),
};

// 导出所有API请求
export default {
  stream: streamApi,
};
