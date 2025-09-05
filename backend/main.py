@@ .. @@
 # Startup and shutdown events
-@app.on_event("startup")
+@app.on_event("startup") 
 async def startup_event():
     """Initialize services on startup."""
     try:
         print("[STARTING] AI Chatbot...")
         
-        # Initialize database
-        await database.connect()
-        print("[OK] Database connected")
+        # Initialize database (skip if MongoDB not available)
+        try:
+            await database.connect()
+            print("[OK] Database connected")
+        except Exception as e:
+            print(f"[WARNING] Database connection failed: {e}")
+            print("[INFO] Continuing without database (some features may not work)")
         
         # Initialize memory system
         await memory_manager.initialize()
         print("[OK] Memory system initialized")
         
         # Register plugins
-        from .plugins.weather import WeatherPlugin
-        from .plugins.news import NewsPlugin
-        from .plugins.wikipedia import WikipediaPlugin
-        
-        plugin_manager.register_plugin(WeatherPlugin())
-        plugin_manager.register_plugin(NewsPlugin())
-        plugin_manager.register_plugin(WikipediaPlugin())
-        print("[OK] Plugins registered")
+        try:
+            from .plugins.weather import WeatherPlugin
+            from .plugins.news import NewsPlugin
+            from .plugins.wikipedia import WikipediaPlugin
+            
+            plugin_manager.register_plugin(WeatherPlugin())
+            plugin_manager.register_plugin(NewsPlugin())
+            plugin_manager.register_plugin(WikipediaPlugin())
+            print("[OK] Plugins registered")
+        except Exception as e:
+            print(f"[WARNING] Plugin registration failed: {e}")
         
         print("[SUCCESS] AI Chatbot started successfully!")
         
     except Exception as e:
-        print(f"[ERROR] Failed to start AI Chatbot: {e}")
-        raise
+        print(f"[WARNING] Some components failed to start: {e}")
+        print("[INFO] Server will continue with limited functionality")