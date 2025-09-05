@@ .. @@
     async def connect(self):
         """Establish database connection."""
         try:
             self.client = AsyncIOMotorClient(settings.mongodb_uri)
             self.database = self.client[settings.mongodb_db_name]
             
+            # Test the connection
+            await self.client.admin.command('ping')
+            
             # Create indexes for better performance
             await self.database.conversations.create_index([("user_id", ASCENDING)])
             await self.database.conversations.create_index([("created_at", DESCENDING)])
             await self.database.users.create_index([("username", ASCENDING)])
             await self.database.users.create_index([("email", ASCENDING)])
             
             print("[OK] Connected to MongoDB successfully!")
         except Exception as e:
             print(f"[ERROR] Failed to connect to MongoDB: {e}")
-            raise
+            # Don't raise the exception, just log it
+            self.client = None
+            self.database = None