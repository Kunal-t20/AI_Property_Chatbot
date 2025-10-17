# utils/data_loader.py
import pandas as pd
import os

def load_all_data():
    base_path = os.path.join(os.path.dirname(__file__), "..", "data")

    df_project = pd.read_csv(os.path.join(base_path, "project.csv"))
    df_address = pd.read_csv(os.path.join(base_path, "ProjectAddress.csv"))
    df_config = pd.read_csv(os.path.join(base_path, "ProjectConfiguration.csv"))
    df_variant = pd.read_csv(os.path.join(base_path, "ProjectConfigurationVariant.csv"))

    return df_project, df_address, df_config, df_variant
