"""
Authentication system for the AI Chatbot application.
Handles user registration, login, and JWT token management.
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from .config import settings
from .database import database, User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()


class Token(BaseModel):
    """JWT token response model."""
    
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    """JWT token payload data."""
    
    username: Optional[str] = None


class UserCreate(BaseModel):
    """User registration model."""
    
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    """User login model."""
    
    username: str
    password: str


class AuthManager:
    """Manages user authentication and authorization."""
    
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate a password hash."""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            
            if username is None:
                return None
            
            token_data = TokenData(username=username)
            return token_data
            
        except jwt.PyJWTError:
            return None
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password."""
        try:
            user = await database.get_user(username)
            if not user:
                return None
            
            if not self.verify_password(password, user.hashed_password):
                return None
            
            return user
            
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None
    
    async def register_user(self, user_data: UserCreate) -> User:
        """Register a new user."""
        try:
            # Check if username already exists
            existing_user = await database.get_user(user_data.username)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered"
                )
            
            # Check if email already exists
            existing_email = await database.database.users.find_one({"email": user_data.email})
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Create new user
            hashed_password = self.get_password_hash(user_data.password)
            new_user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
                is_active=True
            )
            
            # Save to database
            user_id = await database.create_user(new_user)
            new_user.id = user_id
            
            return new_user
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error registering user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during registration"
            )
    
    async def login_user(self, user_data: UserLogin) -> Token:
        """Authenticate and login a user."""
        try:
            # Authenticate user
            user = await self.authenticate_user(user_data.username, user_data.password)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password"
                )
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Inactive user account"
                )
            
            # Update last login
            await database.update_user_last_login(user_data.username)
            
            # Create access token
            access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
            access_token = self.create_access_token(
                data={"sub": user.username}, expires_delta=access_token_expires
            )
            
            return Token(
                access_token=access_token,
                token_type="bearer",
                expires_in=self.access_token_expire_minutes * 60
            )
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error logging in user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during login"
            )
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
        """Get the current authenticated user from JWT token."""
        try:
            token = credentials.credentials
            token_data = self.verify_token(token)
            
            if token_data is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            user = await database.get_user(username=token_data.username)
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Inactive user account"
                )
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error getting current user: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def change_password(self, user: User, current_password: str, new_password: str) -> bool:
        """Change user password."""
        try:
            # Verify current password
            if not self.verify_password(current_password, user.hashed_password):
                return False
            
            # Hash new password
            new_hashed_password = self.get_password_hash(new_password)
            
            # Update in database
            result = await database.database.users.update_one(
                {"username": user.username},
                {"$set": {"hashed_password": new_hashed_password}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error changing password: {e}")
            return False
    
    async def deactivate_user(self, user: User) -> bool:
        """Deactivate a user account."""
        try:
            result = await database.database.users.update_one(
                {"username": user.username},
                {"$set": {"is_active": False}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error deactivating user: {e}")
            return False


# Global auth manager instance
auth_manager = AuthManager()


# Dependency functions for FastAPI
async def get_current_user(user: User = Depends(auth_manager.get_current_user)) -> User:
    """FastAPI dependency for getting current authenticated user."""
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """FastAPI dependency for getting current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
