# Google OAuth Setup Instructions

## What You Need to Do

Since you already have a Google OAuth 2.0 client created, you just need to add the credentials to your environment files.

### 1. Backend Configuration

Create or update the `.env` file in the root directory (`d:\Delyan\UNI\calendar-ai - Upgrade\.env`):

```bash
# Copy from .env.example and add your Google credentials
GOOGLE_CLIENT_ID=your-actual-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-google-client-secret
```

### 2. Frontend Configuration

Create or update the `.env` file in the frontend directory (`d:\Delyan\UNI\calendar-ai - Upgrade\frontend\.env`):

```bash
VITE_API_BASE=http://127.0.0.1:8000
VITE_GOOGLE_CLIENT_ID=your-actual-google-client-id.apps.googleusercontent.com
```

### 3. Get Your Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Select your OAuth 2.0 client
3. Copy the **Client ID** (ends with `.apps.googleusercontent.com`)
4. Copy the **Client Secret**
5. Paste them into your `.env` files

### 4. Verify Authorized Origins

Make sure your OAuth client has these authorized JavaScript origins:
- `http://localhost:5173`
- `http://localhost:3000`
- `http://127.0.0.1:5173`
- `http://127.0.0.1:8000`

And these authorized redirect URIs:
- `http://localhost:5173`
- `http://localhost:3000`

### 5. Restart Servers

After adding the credentials:

**Backend:**
```bash
# Stop the current backend (Ctrl+C) and restart
.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000
```

**Frontend:**
```bash
# Stop frontend (Ctrl+C) and restart
cd frontend
npm run dev
```

## Testing

1. Open http://localhost:5173
2. You should see a "Continue with Google" button
3. Click it to test Google OAuth login
4. After successful login, a user will be created automatically if it doesn't exist

## What Was Added

### Backend Changes:
- ✅ New file: `backend/google_oauth.py` - Google OAuth verification logic
- ✅ New endpoint: `POST /auth/google` - Handles Google ID token authentication
- ✅ Auto-creates users from Google accounts
- ✅ Links existing users by email

### Frontend Changes:
- ✅ Added `@react-oauth/google` package
- ✅ Google OAuth provider wraps the app
- ✅ Google Login button in AuthForm
- ✅ `googleLogin()` method in AuthContext
- ✅ One-Tap login support

## How It Works

1. User clicks "Continue with Google"
2. Google OAuth popup appears
3. User selects their Google account
4. Frontend receives an ID token from Google
5. Frontend sends the ID token to backend `/auth/google`
6. Backend verifies the token with Google
7. Backend creates/finds user by email
8. Backend returns JWT access token
9. User is logged in!
