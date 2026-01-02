"""Google OAuth2 integration for authentication"""
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from . import models, auth

load_dotenv()

# Google OAuth2 Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

def verify_google_token(token: str) -> Optional[dict]:
    """
    Verify Google ID token and return user info
    Returns dict with: email, name, picture, email_verified
    """
    try:
        # Verify the token with Google
        idinfo = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        # Verify the issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        
        # Return user info
        return {
            'email': idinfo.get('email'),
            'name': idinfo.get('name'),
            'picture': idinfo.get('picture'),
            'email_verified': idinfo.get('email_verified', False),
            'google_id': idinfo.get('sub')
        }
    except ValueError as e:
        print(f"❌ Google token verification failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error during Google token verification: {e}")
        return None


def get_or_create_google_user(db: Session, google_user_info: dict) -> models.User:
    """
    Get existing user by email or create new user from Google info
    """
    email = google_user_info.get('email')
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not provided by Google"
        )
    
    # Check if user already exists
    user = auth.get_user_by_email(db, email)
    
    if user:
        # User exists, update profile picture if it changed
        if google_user_info.get('picture') and user.profile_picture != google_user_info.get('picture'):
            user.profile_picture = google_user_info.get('picture')
            db.commit()
            db.refresh(user)
        return user
    
    # Create new user from Google info
    # Generate username from email (before @)
    username = email.split('@')[0]
    
    # Make sure username is unique by appending numbers if needed
    base_username = username
    counter = 1
    while auth.get_user_by_username(db, username):
        username = f"{base_username}{counter}"
        counter += 1
    
    # Create user with a random password (they'll use Google login)
    import secrets
    random_password = secrets.token_urlsafe(32)
    
    user = models.User(
        email=email,
        username=username,
        hashed_password=auth.get_password_hash(random_password),
        created_at=datetime.utcnow(),
        is_active=True,
        profile_picture=google_user_info.get('picture')  # Save Google profile picture
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user
