# AI PROPERTY CHATBOT

An intelligent property search assistant that allows users to query real estate listings naturally. Built using FastAPI and Python, it integrates CSV-based property data to provide accurate, filtered search results for properties across cities like Pune, Mumbai, and Dombivli.

---

## Features

- Search properties using natural language queries.
- Filter by:
  - City
  - BHK type (e.g., 1BHK, 2BHK)
  - Budget range
  - Project name
  - Locality
- Returns structured results with:
  - Project name
  - BHK type
  - Price
  - Area
  - Status
  - Possession date
  - Full address
  - Image URL
- Highlights best matches in results.
- Handles large CSV datasets with joins and cleaning.
- Max 50 results per query for performance.

---

## Project Structure



Backend/
│
├── data/
│ ├── project.csv
│ ├── ProjectAddress.csv
│ ├── ProjectConfiguration.csv
│ └── ProjectConfigurationVariant.csv
│
├── models/
│ ├── db_models.py # PropertyCard model
│ └── request_models.py # FilterSchema model
│
├── services/
│ ├── data_manager.py # Core data management & filtering
│ ├── llm_nlu_agent.py # LLM/NLU agent for natural queries
│ └── init.py
│
├── main.py # FastAPI app entry point
├── app.py # Optional Streamlit or API integration
└── .env # Environment variables


---

## Installation

1. Clone the repository:

```bash
git clone <https://github.com/Kunal-t20/AI_Property_Chatbot.git>
cd AI_Property_Chatbot


Create and activate a virtual environment:

python -m venv myenv
source myenv/bin/activate      # Linux/macOS
myenv\Scripts\activate         # Windows


Install dependencies:

pip install -r requirements.txt

Usage

Start the FastAPI server:

uvicorn main:app --reload


Access API docs at: http://127.0.0.1:8000/docs

Example query:

{
  "city": "Pune",
  "bhk": ["2BHK"],
  "min_budget": 5000000,
  "max_budget": 15000000
}


Returns a list of property cards matching the criteria.

Data Management

services/data_manager.py loads and merges multiple CSVs:

project.csv

ProjectAddress.csv

ProjectConfiguration.csv

ProjectConfigurationVariant.csv

Cleans numeric columns (min_price, carpet_area).

Adds city and locality columns for filtering.

Supports filtering by city, BHK, budget, project name, and locality.

Models

PropertyCard: Represents a single property with all relevant details.

FilterSchema: Defines the filters accepted from the user.

Notes

Ensure all CSVs are placed in Backend/data/.

 max 10 results are returned for efficiency.

City detection uses predefined keywords—addresses outside mapped cities may show as "Unknown City".