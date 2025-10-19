import json
import re
from typing import Dict, Any, List
from ollama import chat
from models.request_models import FilterSchema


def format_price(value: float) -> str:
    """Format price in Cr/Lac with rupee symbol."""
    if value is None:
        return "N/A"
    if value >= 1e7:
        return f"₹{value/1e7:.2f} Cr"
    if value >= 1e5:
        return f"₹{value/1e5:.2f} Lacs"
    return f"₹{value:,.0f}"


class LLMNLUAgent:
    def __init__(self, model_name: str = "gemma3"):
        self.model_name = model_name

    # --- FILTER EXTRACTION ---
    def extract_filters(self, query: str) -> Dict[str, Any]:
        schema = json.dumps(FilterSchema.model_json_schema(), indent=2)
        system_prompt = (
            "You are an NLU agent for property search. "
            "Extract all filters from user query as JSON following the provided schema. "
            "Only return JSON. Convert vague budgets to integers (e.g., '1 Crore' → 10000000)."
        )
        user_prompt = f"Query: '{query}'\nSchema:\n{schema}"

        try:
            resp = chat(model=self.model_name, messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])
            content = re.sub(r"```json|```", "", resp["message"]["content"], flags=re.IGNORECASE).strip()
            return json.loads(content)
        except Exception as e:
            print(f"NLU extraction error: {e}")
            return {}

    # --- SUMMARY GENERATION ---
    def generate_summary(self, filters: Dict[str, Any], results: List[Any]) -> str:
        props = [r.dict() if hasattr(r, "dict") else r for r in results]
        if not props:
            return f"No properties found for filters: {filters}"

        prices = [p.get("min_price") for p in props if p.get("min_price") is not None]
        min_price, max_price = format_price(min(prices)), format_price(max(prices)) if prices else ("N/A", "N/A")
        bhks = sorted(set(p.get("bhk_type", "N/A") for p in props))
        cities = sorted(set(p.get("city") or "Unknown" for p in props))
        sample = [{"project": p.get("project_name"), "bhk": p.get("bhk_type"), "price": format_price(p.get("min_price", 0)), "city": p.get("city") or "Unknown"} for p in props[:3]]

        prompt = (
            f"Filters: {filters}\nReturned {len(props)} properties. Price range: {min_price}-{max_price}. "
            f"BHK types: {', '.join(bhks)}. Cities: {', '.join(cities)}. Sample: {sample}. "
            "Write a concise 5-point summary."
        )
        try:
            resp = chat(model=self.model_name, messages=[
                {"role": "system", "content": "Respond only with the summary text."},
                {"role": "user", "content": prompt}
            ])
            return resp["message"]["content"].strip()
        except Exception as e:
            print(f"Summary error: {e}")
            return "Summary could not be generated."

    # --- BEST MATCH REASON ---
    def generate_best_match_reason(self, filters: Dict[str, Any], best_match: Any) -> str:
        if not best_match:
            return "No best match found."
        best_dict = best_match.dict() if hasattr(best_match, "dict") else best_match

        prompt = (
            f"Filters: {filters}\nBest match: {best_dict}\n"
            "Explain in 2-3 sentences why this property fits the requirements (budget, BHK, location, readiness)."
        )
        try:
            resp = chat(model=self.model_name, messages=[
                {"role": "system", "content": "Respond concisely with only explanation."},
                {"role": "user", "content": prompt}
            ])
            return resp["message"]["content"].strip()
        except Exception as e:
            print(f"Best match reason error: {e}")
            return "Could not generate reason."
