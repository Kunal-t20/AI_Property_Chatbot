from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uvicorn

from models.db_models import PropertyCard
from models.request_models import ChatRequest, ChatResponse
from services.data_manager import DataManager
from services.llm_nlu_agent import LLMNLUAgent

app = FastAPI(title="AI Property Search Backend", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Data Manager
data_path = Path(__file__).resolve().parent / "data"
try:
    data_manager = DataManager(data_dir=str(data_path))
    print(f"Data Manager initialized from: {data_path}")
except Exception as e:
    print(f"Error loading data: {e}")
    data_manager = None

# Initialize LLM Agent
try:
    llm_agent = LLMNLUAgent(model_name="gemma3")
    print("LLM NLU Agent initialized (using Gemma3).")
except Exception as e:
    print(f"Error initializing LLM Agent: {e}")
    llm_agent = None

@app.get("/")
def health_check():
    return {
        "status": "running",
        "data_loaded": data_manager is not None,
        "llm_ready": llm_agent is not None
    }

@app.post("/search", response_model=ChatResponse)
async def chat_search(request: ChatRequest):
    if not data_manager or not llm_agent:
        raise HTTPException(
            status_code=503,
            detail="Service not fully initialized."
        )

    try:
        filters_data = llm_agent.extract_filters(request.user_query)
    except Exception as e:
        print(f"Filter extraction error: {e}")
        filters_data = {}

    try:
        matching_properties = data_manager.filter_data(filters_data)
    except Exception as e:
        print(f"Data filtering error: {e}")
        matching_properties = []

    try:
        summary_text = llm_agent.generate_summary(filters_data, matching_properties)
    except Exception as e:
        print(f"Summary generation error: {e}")
        summary_text = "Could not generate a summary due to an internal error."

    return ChatResponse(
        summary=summary_text,
        filters_applied=filters_data,
        properties=matching_properties
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
