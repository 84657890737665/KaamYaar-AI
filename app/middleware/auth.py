from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

async def verify_firebase_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    """
    Dependency to verify a Firebase Auth token.
    Mocks verification for now as requested by the user.
    If no authorization header is provided, returns a default mock user ID for testing.
    """
    if not credentials or not credentials.credentials:
        return "mocked-default-uid-testing"

    token = credentials.credentials
    
    if token == "invalid_token_for_testing":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Mocking successful verification
    # In a real scenario, this would extract the UID from the decoded token
    mock_uid = "mocked-firebase-uid-123"
    
    return mock_uid
