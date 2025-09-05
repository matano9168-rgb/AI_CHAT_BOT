@@ .. @@
       // Actions
-      login: async (credentials) => {
+      login: async (username, password) => {
         set({ isLoading: true, error: null });
         try {
-          const response = await api.post('/auth/login', credentials);
-          const { access_token, user } = response.data;
+          const response = await fetch('/auth/login', {
+            method: 'POST',
+            headers: {
+              'Content-Type': 'application/json',
+            },
+            body: JSON.stringify({ username, password }),
+          });
+          
+          if (!response.ok) {
+            const errorData = await response.json();
+            throw new Error(errorData.detail || 'Login failed');
+          }
+          
+          const data = await response.json();
+          const { access_token } = data;
           
-          // Set token in API headers
-          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
+          // Get user profile
+          const profileResponse = await fetch('/users/profile', {
+            headers: {
+              'Authorization': `Bearer ${access_token}`,
+            },
+          });
+          
+          const user = profileResponse.ok ? await profileResponse.json() : { username };
           
           set({
             user,
             token: access_token,
             isAuthenticated: true,
             isLoading: false,
             error: null,
           });
           
-          return { success: true };
         } catch (error) {
-          const errorMessage = error.response?.data?.detail || 'Login failed';
+          const errorMessage = error.message || 'Login failed';
           set({
             isLoading: false,
             error: errorMessage,
           });
-          return { success: false, error: errorMessage };
+          throw new Error(errorMessage);
         }
       },
 
       register: async (userData) => {
         set({ isLoading: true, error: null });
         try {
-          const response = await api.post('/auth/register', userData);
+          const response = await fetch('/auth/register', {
+            method: 'POST',
+            headers: {
+              'Content-Type': 'application/json',
+            },
+            body: JSON.stringify(userData),
+          });
+          
+          if (!response.ok) {
+            const errorData = await response.json();
+            throw new Error(errorData.detail || 'Registration failed');
+          }
+          
           set({
             isLoading: false,
             error: null,
           });
-          return { success: true, data: response.data };
         } catch (error) {
-          const errorMessage = error.response?.data?.detail || 'Registration failed';
+          const errorMessage = error.message || 'Registration failed';
           set({
             isLoading: false,
             error: errorMessage,
           });
-          return { success: false, error: errorMessage };
+          throw new Error(errorMessage);
         }
       },
 
       logout: () => {
-        // Remove token from API headers
-        delete api.defaults.headers.common['Authorization'];
-        
         set({
           user: null,
           token: null,
           isAuthenticated: false,
           isLoading: false,
           error: null,
         });
       },