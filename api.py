"""
FastAPI Application for Bangladesh Constitution Chatbot
Provides RESTful API endpoints for querying the Constitution
"""
import os
import sys
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import uvicorn

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config.config import Config
from src.chatbot import ConstitutionChatbot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global chatbot instance
chatbot = None

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    global chatbot
    
    # Startup
    logger.info("🚀 Starting Bangladesh Constitution Chatbot API...")
    try:
        config = Config()
        chatbot = ConstitutionChatbot(config)
        
        if not chatbot.is_ready():
            logger.warning("⚠️ Chatbot not fully initialized - some features may be limited")
        else:
            logger.info("✅ Chatbot initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize chatbot: {e}")
        chatbot = None
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down Bangladesh Constitution Chatbot API...")

# Create FastAPI app
app = FastAPI(
    title="Bangladesh Constitution Chatbot API",
    description="RESTful API for querying the Constitution of Bangladesh",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class QueryRequest(BaseModel):
    """Request model for query endpoint"""
    question: str = Field(..., min_length=1, max_length=1000, description="Question about Bangladesh Constitution")
    use_llm: bool = Field(default=True, description="Whether to use LLM for response generation")
    language: Optional[str] = Field(default=None, description="Language preference (en/bn). Auto-detected if not provided.")
    
    @validator('question')
    def validate_question(cls, v):
        """Validate and clean question"""
        v = v.strip()
        if not v:
            raise ValueError("Question cannot be empty")
        return v

class QueryResponse(BaseModel):
    """Response model for query endpoint"""
    success: bool
    question: str
    answer: str
    language: str
    scope: str
    num_sources: int
    processing_time: float
    timestamp: str
    sources: Optional[list] = None

class HealthResponse(BaseModel):
    """Response model for health endpoint"""
    status: str
    chatbot_ready: bool
    timestamp: str
    version: str
    system_info: Dict[str, Any]

class StatsResponse(BaseModel):
    """Response model for stats endpoint"""
    queries_processed: int
    session_duration_minutes: float
    system_status: str
    languages_detected: list
    additional_stats: Dict[str, Any]

class ErrorResponse(BaseModel):
    """Response model for errors"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    timestamp: str

# Exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            timestamp=datetime.now().isoformat()
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc) if os.getenv("DEBUG") else None,
            timestamp=datetime.now().isoformat()
        ).dict()
    )

# API Endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Bangladesh Constitution Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "status": "active"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    global chatbot
    
    system_info = {}
    chatbot_ready = False
    
    if chatbot:
        chatbot_ready = chatbot.is_ready()
        try:
            stats = chatbot.get_session_stats()
            system_info = {
                "queries_processed": stats.get("queries_processed", 0),
                "system_status": stats.get("system_status", "unknown")
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            system_info = {"error": str(e)}
    
    return HealthResponse(
        status="healthy" if chatbot_ready else "degraded",
        chatbot_ready=chatbot_ready,
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        system_info=system_info
    )

@app.get("/stats", response_model=StatsResponse, tags=["Statistics"])
async def get_stats():
    """Get system statistics"""
    global chatbot
    
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chatbot not initialized"
        )
    
    try:
        stats = chatbot.get_session_stats()
        
        return StatsResponse(
            queries_processed=stats.get("queries_processed", 0),
            session_duration_minutes=stats.get("session_duration_minutes", 0),
            system_status=stats.get("system_status", "unknown"),
            languages_detected=list(stats.get("languages_detected", set())),
            additional_stats={k: v for k, v in stats.items() 
                            if k not in ["queries_processed", "session_duration_minutes", 
                                       "system_status", "languages_detected"]}
        )
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )

@app.post("/query", response_model=QueryResponse, tags=["Query"])
async def query_constitution(request: QueryRequest):
    """
    Query the Bangladesh Constitution
    
    - **question**: Question about the Constitution (required)
    - **use_llm**: Whether to use LLM for enhanced responses (default: true)
    - **language**: Language preference (en/bn, auto-detected if not provided)
    """
    global chatbot
    
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chatbot not initialized. Please try again later."
        )
    
    if not chatbot.is_ready():
        logger.warning("Chatbot not fully ready, but attempting to process query")
    
    try:
        logger.info(f"Processing query: {request.question[:50]}...")
        start_time = datetime.now()
        
        # Process the query
        result = chatbot.process_query(
            query=request.question,
            use_llm=request.use_llm
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return QueryResponse(
            success=True,
            question=result["question"],
            answer=result["answer"],
            language=result.get("language", "en"),
            scope=result.get("scope", "unknown"),
            num_sources=result.get("num_sources", 0),
            processing_time=processing_time,
            timestamp=datetime.now().isoformat(),
            sources=result.get("sources", []) if request.use_llm else None
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )

@app.post("/initialize", tags=["Admin"])
async def initialize_chatbot(force_rebuild: bool = False):
    """
    Initialize or reinitialize the chatbot
    
    - **force_rebuild**: Force rebuild of vector store (default: false)
    """
    global chatbot
    
    try:
        logger.info(f"Initializing chatbot (force_rebuild={force_rebuild})...")
        
        config = Config()
        chatbot = ConstitutionChatbot(config)
        
        if force_rebuild and chatbot.rag_system:
            success = chatbot.rag_system.initialize(force_rebuild=True)
        else:
            success = chatbot.is_ready()
        
        if success:
            return {
                "success": True,
                "message": "Chatbot initialized successfully",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initialize chatbot"
            )
            
    except Exception as e:
        logger.error(f"Error initializing chatbot: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Initialization failed: {str(e)}"
        )

@app.delete("/history", tags=["Admin"])
async def clear_history():
    """Clear conversation history"""
    global chatbot
    
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chatbot not initialized"
        )
    
    try:
        chatbot.clear_conversation_history()
        return {
            "success": True,
            "message": "Conversation history cleared",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear history: {str(e)}"
        )

@app.get("/history", tags=["History"])
async def get_history(limit: int = 10):
    """
    Get conversation history
    
    - **limit**: Maximum number of recent conversations to return (default: 10)
    """
    global chatbot
    
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chatbot not initialized"
        )
    
    try:
        history = chatbot.get_conversation_history(limit)
        return {
            "success": True,
            "count": len(history),
            "history": [
                {
                    "timestamp": conv["timestamp"].isoformat(),
                    "query": conv["query"],
                    "response": conv["response"],
                    "language": conv["language"],
                    "sources": conv["sources"]
                }
                for conv in history
            ]
        }
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve history: {str(e)}"
        )

def main():
    """Run the API server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Bangladesh Constitution Chatbot API")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    
    args = parser.parse_args()
    
    logger.info(f"Starting API server on {args.host}:{args.port}")
    
    uvicorn.run(
        "api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers if not args.reload else 1,
        log_level="info"
    )

if __name__ == "__main__":
    main()
