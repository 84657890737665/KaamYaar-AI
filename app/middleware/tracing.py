import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class TracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract X-Request-ID from request headers, or generate a new one
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())
            
        # Add the request_id to the request state
        request.state.request_id = request_id
        
        # Call the next middleware or route handler
        response = await call_next(request)
        
        # Inject the X-Request-ID into the response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
