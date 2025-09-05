@@ .. @@
       // Actions
      login: async (username, password) => {
        set({ isLoading: true, error: null });
        try {
          const response = await fetch('/auth/login', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
          });
          
          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Login failed');
          }
          
          const data = await response.json();
          const { access_token } = data;
          
          // Get user profile
          const profileResponse = await fetch('/users/profile', {
            headers: {
              'Authorization': `Bearer ${access_token}`,
            },
          });
          
          const user = profileResponse.ok ? await profileResponse.json() : { username };
          
          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
          
        } catch (error) {
          const errorMessage = error.message || 'Login failed';
          set({
            isLoading: false,
            error: errorMessage,
          });
          throw new Error(errorMessage);
        }
      },

      register: async (userData) => {
        set({ isLoading: true, error: null });
        try {
          const response = await fetch('/auth/register', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
          });
          
          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Registration failed');
          }
          
          set({
            isLoading: false,
            error: null,
          });
        } catch (error) {
          const errorMessage = error.message || 'Registration failed';
          set({
            isLoading: false,
            error: errorMessage,
          });
          throw new Error(errorMessage);
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        });
      },