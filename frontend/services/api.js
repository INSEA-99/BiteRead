import axios from 'axios';
import { Platform } from 'react-native';
import Constants from 'expo-constants';

// API base URL - 플랫폼별 자동 설정
const getApiUrl = () => {
  // .env 파일에 설정이 있으면 우선 사용
  if (process.env.EXPO_PUBLIC_API_URL) {
    return process.env.EXPO_PUBLIC_API_URL;
  }

  // 플랫폼별 자동 설정
  const localhost = Constants.expoConfig?.hostUri?.split(':').shift() || 'localhost';

  if (Platform.OS === 'web') {
    // 웹: localhost
    return 'http://localhost:8000';
  } else if (Platform.OS === 'android') {
    // 안드로이드 에뮬레이터: 10.0.2.2
    // 안드로이드 실제 기기: 개발 서버 IP
    return `http://${localhost}:8000`;
  } else if (Platform.OS === 'ios') {
    // iOS 시뮬레이터: localhost
    // iOS 실제 기기: 개발 서버 IP
    return `http://${localhost}:8000`;
  }

  // 기본값
  return 'http://localhost:8000';
};

const API_BASE_URL = getApiUrl();

console.log(`🔗 API URL: ${API_BASE_URL}`);

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Article API
export const articleAPI = {
  // 글 목록 조회
  getAll: async () => {
    const response = await api.get('/api/articles/');
    return response.data;
  },

  // 글 상세 조회 (문장 포함)
  getById: async (id) => {
    const response = await api.get(`/api/articles/${id}`);
    return response.data;
  },

  // 글 생성
  create: async (title, content) => {
    const response = await api.post('/api/articles/', { title, content });
    return response.data;
  },
};

// Translation API
export const translationAPI = {
  // 번역 체크
  check: async (sentenceId, userTranslation) => {
    const response = await api.post('/api/translation/check', {
      sentence_id: sentenceId,
      user_translation: userTranslation,
    });
    return response.data;
  },
};

export default api;
