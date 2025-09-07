from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from main_graph import MainGraph
import asyncio
import threading
from typing import Optional

app = FastAPI(title="Intelligent Ambience API", version="1.0.0")

# Global instance - initialized once on startup
main_graph = None

class AmbienceRequest(BaseModel):
    query: str
    img_url: Optional[str] = "no image provided"
    user_feedback: Optional[str] = ""

class AmbienceResponse(BaseModel):
    success: bool
    message: str
    result: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize the system once on startup"""
    global main_graph
    print("🚀 Initializing Intelligent Ambience System...")
    main_graph = MainGraph()
    print("✅ System ready!")

@app.post("/generate", response_model=AmbienceResponse)
async def generate_ambience(request: AmbienceRequest):
    """Generate ambient music based on location and context"""
    try:
        if not main_graph:
            raise HTTPException(status_code=500, detail="System not initialized")
        
        # Run the system (this will be synchronous, but we can make it async)
        result = await asyncio.to_thread(
            main_graph.run_with_feedback_streaming,
            request.query,
            request.img_url,
            request.user_feedback
        )
        
        return AmbienceResponse(
            success=True,
            message="Ambient music generated successfully",
            result=str(result)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating ambience: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "system": "intelligent-ambience"}

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "message": "Intelligent Ambience API",
        "endpoints": {
            "POST /generate": "Generate ambient music",
            "GET /health": "Health check",
            "GET /": "This info"
        }
    }

if __name__ == "__main__":
    # Run with: python api_server.py
    uvicorn.run(
        "api_server:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
