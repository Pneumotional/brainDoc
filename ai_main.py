from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from phi.memory.agent import AgentMemory, MemoryRetrieval, Memory, AgentRun, SessionSummary
import uvicorn
from phi.model.groq import Groq
from phi.agent import Agent, RunResponse
from phi.knowledge.pdf import PDFKnowledgeBase, PDFReader
from phi.vectordb.pgvector import PgVector, SearchType
from phi.storage.agent.postgres import PgAgentStorage
from phi.embedder.google import GeminiEmbedder
from phi.tools.googlesearch import GoogleSearch
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import Json
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime

class ChatHistory(BaseModel):
    messages: List[Message]
    session_id: str

class Query(BaseModel):
    text: str
    user_id: Optional[str] = "default_user"
    session_id: Optional[str] = None
    new_session: Optional[bool] = False

class AgentResponse(BaseModel):
    content: str
    session_id: str


# Database configuration
db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
db_params = {
    "dbname": "ai",
    "user": "ai",
    "password": "ai",
    "host": "localhost",
    "port": "5532"
}

# Create messages table if it doesn't exist
def init_db():
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id SERIAL PRIMARY KEY,
            session_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_session_user ON chat_messages(session_id, user_id);
    """)
    conn.commit()
    cur.close()
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database and load models/resources
    init_db()
    print("Database initialized")
    
    yield  # Server is running and handling requests
    
    # Cleanup: You can add any cleanup code here
    print("Shutting down")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # In production, specify your Django domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# The storage is initialized once for the application
storage = PgAgentStorage(table_name="doc_management_vec", db_url=db_url)

# Function to create a user-specific knowledge base
def create_knowledge_base(user_id):
    user_path = f'media/user_{user_id}'
    
    # Ensure the directory exists
    os.makedirs(user_path, exist_ok=True)
    
    return PDFKnowledgeBase(
        path=user_path,
        vector_db=PgVector(
            table_name=f"doc_management_user_{user_id}",  # User-specific table
            db_url=db_url,
            search_type=SearchType.vector,
            embedder=GeminiEmbedder(dimensions=300),
        ),
        reader=PDFReader(chunk=True),       
    )

def store_message(session_id: str, user_id: str, role: str, content: str):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO chat_messages (session_id, user_id, role, content)
        VALUES (%s, %s, %s, %s)
        """,
        (session_id, user_id, role, content)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_chat_history(session_id: str, user_id: str) -> List[Dict]:
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT role, content, timestamp 
        FROM chat_messages 
        WHERE session_id = %s AND user_id = %s 
        ORDER BY timestamp
        """,
        (session_id, user_id)
    )
    messages = [
        {
            "role": role,
            "content": content,
            "timestamp": timestamp
        }
        for role, content, timestamp in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return messages

def get_user_sessions(user_id: str) -> List[str]:
    """Get all unique session IDs for a user from chat_messages table"""
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT DISTINCT session_id
        FROM chat_messages
        WHERE user_id = %s
        ORDER BY session_id
        """,
        (user_id,)
    )
    sessions = [session_id for (session_id,) in cur.fetchall()]
    cur.close()
    conn.close()
    return sessions

def create_agent(user_id: str, session_id: Optional[str] = None) -> Agent:
    # Create user-specific knowledge base
    user_kb = create_knowledge_base(user_id)
    
    # Load user documents - do this only when needed for performance
    user_kb.load(upsert=True, recreate=False)
    
    if not session_id:
        # Get sessions from messages table instead of agent storage
        existing_sessions = get_user_sessions(user_id)
        if existing_sessions:
            session_id = existing_sessions[-1]  # Get the most recent session
    
    return Agent(
        model=Groq(id='llama3-70b-8192'),
        knowledge=user_kb,
        search_knowledge=True,
        add_context=True,
        markdown=True,
        memory=AgentMemory(),
    # add_history_to_messages=true adds the chat history to the messages sent to the Model.
        add_history_to_messages=True,
    # Number of historical responses to add to the messages.
        num_history_responses= 5,
        show_tool_calls=False,
        add_references=True,
        session_id=session_id,  # Use the provided or latest session ID
        storage=storage,  # Still use the PgAgentStorage for agent state
        description='You are a Female PDF assistant, Assisting people to find content in their pdf',
        instructions=[
            'Search the knowledge_base extensively for the results',
            "Don't say using another tool or anything like that, just answer"
        ]
    )

@app.post("/query", response_model=AgentResponse)
async def query_agent(query: Query):
    try:
        # Create agent instance with user-specific knowledge base
        agent = create_agent(user_id=query.user_id, session_id=query.session_id)
        
        # Store user message
        store_message(agent.session_id, query.user_id, "user", query.text)
        
        # Get response
        response: RunResponse = agent.run(query.text)
        
        # Store assistant message
        store_message(agent.session_id, query.user_id, "assistant", response.content)
        
        return AgentResponse(
            content=response.content,
            session_id=agent.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat_history/{session_id}/{user_id}", response_model=ChatHistory)
async def get_session_history(session_id: str, user_id: str):
    messages = get_chat_history(session_id, user_id)
    return ChatHistory(messages=messages, session_id=session_id)

@app.get("/sessions/{user_id}")
async def get_user_sessions_endpoint(user_id: str):
    sessions = get_user_sessions(user_id)
    return {"sessions": sessions}

@app.post("/load_knowledge/{user_id}")
async def load_knowledge(user_id: str):
    """Endpoint to manually trigger knowledge base loading for a user"""
    try:
        kb = create_knowledge_base(user_id)
        kb.load(upsert=True, recreate=False)
        return {"status": "success", "message": f"Knowledge base loaded for user {user_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)