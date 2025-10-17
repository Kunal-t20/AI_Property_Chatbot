# utils/search_engine.py
import pandas as pd

def search_properties(filters, df_project, df_address, df_config, df_variant):
    """
    Filter the dataset using parsed query filters safely.
    Auto-detect merge columns and normalize column names.
    """

    # --- Normalize all column names ---
    for df in [df_project, df_address, df_config, df_variant]:
        df.columns = [c.strip().lower().replace(" ", "").replace("_", "") for c in df.columns]

    # --- Helper to find column containing keywords ---
    def find_column(df, keywords):
        for col in df.columns:
            if all(k.lower() in col for k in keywords):
                return col
        return None

    # --- Detect merge columns ---
    projectid_col_project = find_column(df_project, ["project", "id"])
    projectid_col_address = find_column(df_address, ["project", "id"])
    projectid_col_config = find_column(df_config, ["project", "id"])
    configurationid_col_variant = find_column(df_variant, ["configuration", "id"])

    # --- Check missing columns ---
    missing = []
    if not projectid_col_project: missing.append("df_project project id")
    if not projectid_col_address: missing.append("df_address project id")
    if not projectid_col_config: missing.append("df_config project id")
    if not configurationid_col_variant: missing.append("df_variant configuration id")
    if missing:
        raise KeyError(f"Missing required columns: {', '.join(missing)}")

    # --- Rename columns to standard names ---
    df_project.rename(columns={projectid_col_project: "projectid"}, inplace=True)
    df_address.rename(columns={projectid_col_address: "projectid"}, inplace=True)
    df_config.rename(columns={projectid_col_config: "projectid"}, inplace=True)
    df_variant.rename(columns={configurationid_col_variant: "configurationid"}, inplace=True)

    # --- Merge safely ---
    df_merged = (
        df_project
        .merge(df_address, on="projectid", how="left")
        .merge(df_config, on="projectid", how="left")
        .merge(df_variant, on="configurationid", how="left")
    )

    # --- Apply filters safely ---
    if filters.get("city") and "city" in df_merged.columns:
        df_merged = df_merged[df_merged["city"].str.contains(filters["city"], case=False, na=False)]

    if filters.get("bhk") and "bhk" in df_merged.columns:
        df_merged = df_merged[df_merged["bhk"].astype(str).str.contains(str(filters["bhk"]), na=False)]

    if filters.get("budget"):
        price_col = next((col for col in df_merged.columns if "price" in col), None)
        if price_col:
            df_merged = df_merged[df_merged[price_col] <= filters["budget"]]

    if filters.get("readiness"):
        status_col = next((col for col in df_merged.columns if "status" in col or "possession" in col), None)
        if status_col:
            df_merged = df_merged[df_merged[status_col].str.contains(filters["readiness"].split()[0], case=False, na=False)]

    if filters.get("locality") and "locality" in df_merged.columns:
        df_merged = df_merged[df_merged["locality"].str.contains(filters["locality"], case=False, na=False)]

    # --- Select main columns for output ---
    cols_to_keep = [
        col for col in df_merged.columns
        if any(key in col for key in ["projectname", "city", "locality", "bhk", "price", "status", "amen"])
    ]
    df_result = df_merged[cols_to_keep].drop_duplicates()

    # --- Fallback if no results ---
    if df_result.empty:
        return pd.DataFrame([{"message": f"No matching properties found for query filters: {filters}"}])

    return df_result
