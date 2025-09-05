import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api from '../services/api';

const useAuthStore = create(
  persist(
    (set, get) => ({
      // State
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (credentials) => {
        set({ isLoading: true, error: null });
        try {
          const response = await api.post('/auth/login', credentials);
          const { access_token, user } = response.data;
          
          // Set token in API headers
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
          
          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
          
          return { success: true };
        } catch (error) {
          const errorMessage = error.response?.data?.detail || 'Login failed';
          set({
            isLoading: false,
            error: errorMessage,
          });
          return { success: false, error: errorMessage };
        }
      },

      register: async (userData) => {
        set({ isLoading: true, error: null });
        try {
          const response = await api.post('/auth/register', userData);
          set({
            isLoading: false,
            error: null,
          });
          return { success: true, data: response.data };
        } catch (error) {
          const errorMessage = error.response?.data?.detail || 'Registration failed';
          set({
            isLoading: false,
            error: errorMessage,
          });
          return { success: false, error: errorMessage };
        }
      },

      logout: () => {
        // Remove token from API headers
        delete api.defaults.headers.common['Authorization'];
        
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        });
      },

      updateProfile: async (profileData) => {
        try {
          const response = await api.put('/users/profile', profileData);
          set({
            user: { ...get().user, ...response.data },
          });
          return { success: true };
        } catch (error) {
          const errorMessage = error.response?.data?.detail || 'Profile update failed';
          set({ error: errorMessage });
          return { success: false, error: errorMessage };
        }
      },

      changePassword: async (passwordData) => {
        try {
          await api.put('/users/password', passwordData);
          return { success: true };
        } catch (error) {
          const errorMessage = error.response?.data?.detail || 'Password change failed';
          set({ error: errorMessage });
          return { success: false, error: errorMessage };
        }
      },

      clearError: () => set({ error: null }),

      // Initialize auth state from stored token
      initializeAuth: async () => {
        const { token } = get();
        if (token) {
          try {
            // Set token in API headers
            api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            
            // Verify token by getting user profile
            const response = await api.get('/users/profile');
            set({
              user: response.data,
              isAuthenticated: true,
            });
          } catch (error) {
            // Token is invalid, clear auth state
            get().logout();
          }
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token }),
    }
  )
);

export { useAuthStore };
export default useAuthStore;
