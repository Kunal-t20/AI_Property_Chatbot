# main.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from utils.data_loader import load_all_data
from utils.parser import parse_query
from utils.search_engine import search_properties
from utils.summerizer import generate_summary
import uvicorn

# --- Initialize FastAPI ---
app = FastAPI(title="AI Real Estate Assistant", version="1.0")

# --- Allow frontend (like Streamlit / React) to call this backend ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

df_project, df_address, df_config, df_variant = load_all_data()

@app.get("/")
def home():
    return {"message": "Welcome to AI Real Estate Assistant!"}

@app.post("/search/")
def search(query: str = Query(..., description="User search query")):
    try:
        filters = parse_query(query)

        results_df = search_properties(filters, df_project, df_address, df_config, df_variant)

        results_list = results_df.to_dict(orient="records")

        summary_text = ""
        if results_list and "message" not in results_list[0]:
            first_property_text = " ".join([str(v) for v in results_list[0].values()])
            summary_text = generate_summary(first_property_text)

        return {
            "query": query,
            "filters": filters,
            "results": results_list,
            "summary": summary_text
        }

    except Exception as e:
        return {"error": str(e)}

# --- Run server ---
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
