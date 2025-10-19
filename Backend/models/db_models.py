from pydantic import BaseModel, Field
from typing import Optional, List

class PropertyCard(BaseModel):
    """
    Pydantic model for a single, comprehensive Property/Project Card.
    Fields are derived from joining the various CSV data sources.
    """
    id: str = Field(..., description="Unique ID of the property/project.")
    project_name: str = Field(..., description="Name of the project.")
    
    # Explicit city and locality fields (helps avoid 'Unknown' in summaries)
    city: Optional[str] = Field(None, description="City where the project is located.")
    locality: Optional[str] = Field(None, description="Locality or sub-locality of the project.")
    
    status: Optional[str] = Field(None, description="Current status (e.g., READY_TO_MOVE, UNDER_CONSTRUCTION).")
    possession_date: Optional[str] = Field(None, description="Estimated possession date.")
    
    # Configuration / variant details
    bhk_type: Optional[str] = Field(None, description="BHK type (e.g., '2BHK', '3BHK').")
    min_price: Optional[float] = Field(None, description="The starting price of the unit in the variant.")
    carpet_area: Optional[float] = Field(None, description="Carpet area in square units.")
    bathrooms: Optional[int] = Field(None, description="Number of bathrooms.")
    
    summary: Optional[str] = Field(None, description="A short summary of the project.")

    image_url: Optional[str] = Field(None, description="Primary image URL for the property card.")
    
    formatted_price: Optional[str] = Field(None, description="Price formatted as '₹X Cr/Lac' for frontend display.")

    full_address: Optional[str] = Field(None, description="Full address of the property including city and locality.")
