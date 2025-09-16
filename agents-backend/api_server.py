from fastapi import WebSocket, WebSocketDisconnect, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from main_graph import MainGraph
import asyncio
import json
from typing import Optional

app = FastAPI(title="Intelligent Ambience API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

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
    print("Initializing Intelligent Ambience System...")
    main_graph = MainGraph()
    print("System ready!")

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

#this is a generate websocket connection that connects only whilst the system is generating and streams the system 'thinking'.
@app.websocket("/ws/generate")
async def ws_generate(websocket:WebSocket):
    await websocket.accept() #this awaits for a connection to the front-end? I think
    task = None
    queue: asyncio.Queue = asyncio.Queue()
    
    try: 
        init_msg = await websocket.receive_json()
        if init_msg.get("type") != "init": # if there is no init message then close the websocket
            await websocket.send_json({"type":"error","message":"Expected init"})
            await websocket.close()
            return
    
        #get the messages from init
        query = init_msg.get("query") or ""
        img_url = init_msg.get("img_url") or "no image provided"

        await queue.put({"type":"status","message":"Starting..."})

        async def run_graph():

            try:
                loop = asyncio.get_running_loop()
                def map_chunk_to_events(chunk):
                    events = []

                    def emit(name: str, content):
                        # Accept string or list parts with text
                        if isinstance(content, str) and content.strip():
                            events.append({"type": "token", "text": f"{name}: {content}\n"})
                        elif isinstance(content, list):
                            for part in content:
                                if isinstance(part, dict) and part.get("type") == "text" and part.get("text"):
                                    events.append({"type": "token", "text": f"{name}: {part['text']}\n"})

                    def emit_filtered_from_messages(messages, prefix: str | None = None):
                        for m in messages:
                            mtype = type(m).__name__  # "AIMessage", "ToolMessage", etc.
                            name = prefix or getattr(m, "name", None) or getattr(m, "role", None) or "agent"

                            if mtype == "AIMessage":
                                emit(name, getattr(m, "content", ""))

                            elif mtype == "ToolMessage":
                                emit(name, getattr(m, "content", ""))

                    # 1) Top-level messages (if present)
                    if isinstance(chunk.get("messages"), list):
                        emit_filtered_from_messages(chunk["messages"])

                    # 2) Node-keyed outputs: preserve node labels and only surface AI/Tool messages
                    for node_key in (
                        "supervisor",
                        "global_context_agent",
                        "local_context_agent",
                        "memory_agent",
                        "reinforcement_agent",
                        "music_generation_agent",
                    ):
                        if node_key in chunk:
                            node_val = chunk[node_key]
                            # Common shape: dict with "messages": [...]
                            if isinstance(node_val, dict) and isinstance(node_val.get("messages"), list):
                                emit_filtered_from_messages(node_val["messages"], prefix=node_key)
                            else:
                                # Fallback: single message-like object with .content
                                content = (
                                    getattr(node_val, "content", None)
                                    or (node_val.get("content") if isinstance(node_val, dict) else None)
                                )
                                if content:
                                    emit(node_key, content)

                    return events
                
                def produce():
                    try:
                        inputs = {"messages": [("user", f"{query} {img_url}")]}
                        print("produce: starting")
                        for chunk in main_graph.graph.stream(inputs):
                            if chunk is None:
                                print("produce: got None chunk"); continue
                            print("produce: chunk keys", list(chunk.keys()))

                            for evt in map_chunk_to_events(chunk):
                                print("produce: enqueue", evt)
                                loop.call_soon_threadsafe(queue.put_nowait, evt)
                        print("produce: done enqueueing")
                        loop.call_soon_threadsafe(queue.put_nowait, {"type":"done","summary":"ok"})
                    except Exception as e:
                        loop.call_soon_threadsafe(queue.put_nowait, {"type":"error","message":str(e)})
                
                await asyncio.to_thread(produce)
            except Exception as e:
                print("run_graph error:", e)
                await queue.put({"type":"error","message":str(e)})
        

        task = asyncio.create_task(run_graph())

        #optional: read client messages e.g 'cancel'. Will need to add user feedback here? 
        async def read_client():
            while True:
                try: 
                    msg = await websocket.receive_json()
                    if msg.get("type") == "cancel":
                        if task:
                            task.cancel()

                except Exception:
                    break
        
        reader_task = asyncio.create_task(read_client())

        #send events
        while True:
            event = await queue.get()
            await websocket.send_json(event)
            if event.get("type") in ("error","done"):
                break


    except WebSocketDisconnect:
        if task:
            task.cancel()

    finally:
        if task:
            task.cancel()



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
        host="127.0.0.1", 
        port=8000, 
        reload=True,
        log_level="info"
    )
