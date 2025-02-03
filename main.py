import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Get port from environment variable or default to 8000
    host = "0.0.0.0"  # This is the standard for making the app externally accessible
    reload = os.getenv("ENV") != "production"  # Only reload in development

    uvicorn.run("api:app", host=host, port=port, reload=reload)
