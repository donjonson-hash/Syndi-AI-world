import { api } from './client';
import type { Match, UserProfile } from '../types/matching';

export const matchingApi = {
  // Список матчей текущего пользователя
  getMatches: () =>
    api.get<Match[]>('/api/v1/matching/discover'),

  // Лайк / пасс
  sendAction: (toUserId: string, action: 'like' | 'pass') =>
    api.post<{ matched: boolean }>('/api/v1/matching/action', { to_user_id: toUserId, action }),

  // Профиль пользователя
  getProfile: (userId: string) =>
    api.get<UserProfile>(`/api/v1/profiles/${userId}`),

  // Свой профиль
  getMe: () =>
    api.get<UserProfile>('/api/v1/auth/me'),

  // Обновить OCEAN в профиле
  updateProfile: (data: Partial<UserProfile>) =>
    api.put<UserProfile>('/api/v1/profiles/me', data),
};
