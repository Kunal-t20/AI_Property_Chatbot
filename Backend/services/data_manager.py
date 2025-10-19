from typing import Dict, List, Any, Optional
import os
import pandas as pd
from models.db_models import PropertyCard

class DataManager:
    """
    Manages all property data operations: loading CSVs, joining them into a
    master DataFrame, and filtering based on structured inputs.
    """

    COLUMNS = {
        "project": "project.csv",
        "address": "ProjectAddress.csv",
        "config": "ProjectConfiguration.csv",
        "variant": "ProjectConfigurationVariant.csv",
    }
    master_df: Optional[pd.DataFrame] = None

    # City mapping for strict filtering
    CITY_MAPPING = {
        "Pune": ["Pune", "Somwar Peth", "Mangalwar Peth", "Shivajinagar", "Mundhwa", "Mamurdi", "Model Colony", "Punawale", "Dattwadi", "MCA Stadium", "Sai Nagar"],
        "Mumbai": ["Mumbai", "Chembur", "Mulund", "Ghatkopar", "Andheri", "Sewri", "Pant Nagar"],
        "Dombivli": ["Dombivli"]
    }

    def __init__(self, data_dir: str):
        print(f"Attempting to load data from: {data_dir}")
        self.data_dir = data_dir
        self._load_and_join_data()

    def _load_and_join_data(self):
        dataframes = {}

        # Load all CSVs
        for key, filename in self.COLUMNS.items():
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Missing required CSV file: {filepath}")

            if key == "variant":
                try:
                    df = pd.read_csv(filepath, quoting=1, escapechar='\\')
                except pd.errors.ParserError:
                    df = pd.read_csv(filepath)
            else:
                df = pd.read_csv(filepath)

            dataframes[key] = df
            print(f"Loaded {key} with {len(df)} rows.")

        # --- Data Joining ---
        df_project = dataframes["project"].rename(columns={'id': 'projectId'})
        df_address = dataframes["address"]

        df_master = pd.merge(
            df_project,
            df_address[['projectId', 'fullAddress', 'pincode']],
            on='projectId',
            how='inner'
        )

        df_config = dataframes["config"].rename(columns={'id': 'configId', 'type': 'bhk_type'})
        df_master = pd.merge(
            df_master,
            df_config[['projectId', 'configId', 'bhk_type', 'customBHK']],
            on='projectId',
            how='inner'
        )

        df_variant = dataframes["variant"].rename(columns={
            'id': 'variantId',
            'configurationId': 'configId',
            'carpetArea': 'carpet_area',
            'price': 'min_price',
            'bathrooms': 'bathrooms_count',
            'propertyImages': 'image_url'
        })
        df_master = pd.merge(
            df_master,
            df_variant[['configId', 'variantId', 'carpet_area', 'min_price', 'bathrooms_count', 'image_url']],
            on='configId',
            how='inner'
        )

        # Clean numeric columns
        df_master['min_price'] = pd.to_numeric(df_master['min_price'].replace({',': ''}, regex=True), errors='coerce')
        df_master['carpet_area'] = pd.to_numeric(df_master['carpet_area'], errors='coerce')

        df_master.dropna(subset=['min_price', 'carpet_area'], inplace=True)

        # Rename columns to match PropertyCard
        df_master.rename(columns={
            'projectId': 'id',
            'projectName': 'project_name',
            'status': 'status',
            'possessionDate': 'possession_date',
            'projectSummary': 'summary',
            'bhk_type': 'bhk_type',
            'bathrooms_count': 'bathrooms',
        }, inplace=True)

        # Select final columns
        self.master_df = df_master.filter(items=[
            'id', 'project_name', 'status', 'possession_date', 'summary',
            'bhk_type', 'min_price', 'carpet_area', 'bathrooms', 'image_url',
            'fullAddress'
        ])

        # Extract city using CITY_MAPPING
        def map_city(address: str) -> str:
            if not isinstance(address, str):
                return "Unknown City"
            address_lower = address.lower()
            for city, keywords in self.CITY_MAPPING.items():
                for kw in keywords:
                    if kw.lower() in address_lower:
                        return city
            return "Unknown City"

        self.master_df['city'] = self.master_df['fullAddress'].apply(map_city)

        # Extract locality (first part of address)
        self.master_df['locality'] = self.master_df['fullAddress'].apply(
            lambda x: x.split(',')[0].strip() if isinstance(x, str) else 'Unknown Locality'
        )

        print(f"Master DataFrame ready with {len(self.master_df)} final rows.")

    def filter_data(self, filters: Dict[str, Any]) -> List[PropertyCard]:
        if self.master_df is None or self.master_df.empty:
            return []

        df = self.master_df.copy()
        conditions = []

        # City (strict match)
        if filters.get("city"):
            city = filters["city"].strip().lower()
            conditions.append(df['city'].str.lower() == city)

        # BHK
        if filters.get("bhk"):
            bhk_list = [b.lower().replace('bhk', '').strip() for b in filters["bhk"]]
            conditions.append(df['bhk_type'].str.lower().str.replace('bhk', '').isin(bhk_list))

        # Budget
        if filters.get("min_budget"):
            conditions.append(df['min_price'] >= filters["min_budget"])
        if filters.get("max_budget"):
            conditions.append(df['min_price'] <= filters["max_budget"])

        # Project name
        if filters.get("project_name"):
            pname = filters["project_name"].strip().lower()
            conditions.append(df['project_name'].str.lower().str.contains(pname, na=False))

        # Locality
        if filters.get("locality"):
            loc = filters["locality"].strip().lower()
            conditions.append(df['locality'].str.lower().str.contains(loc, na=False))

        # Apply filters
        if conditions:
            final_condition = conditions[0]
            for cond in conditions[1:]:
                final_condition &= cond
            df_filtered = df[final_condition]
        else:
            df_filtered = df.head(100)

        df_filtered = df_filtered.where(pd.notnull(df_filtered), None)

        properties_list = [
            PropertyCard(
                id=row.get('id'),
                project_name=row.get('project_name', 'N/A'),
                city=row.get('city'),
                locality=row.get('locality'),
                status=row.get('status'),
                possession_date=row.get('possession_date'),
                bhk_type=row.get('bhk_type'),
                min_price=row.get('min_price'),
                carpet_area=row.get('carpet_area'),
                bathrooms=row.get('bathrooms'),
                summary=row.get('summary'),
                image_url=row.get('image_url'),
                full_address=row.get('fullAddress')
            )
            for _, row in df_filtered.iterrows()
        ]

        return properties_list[:50]
