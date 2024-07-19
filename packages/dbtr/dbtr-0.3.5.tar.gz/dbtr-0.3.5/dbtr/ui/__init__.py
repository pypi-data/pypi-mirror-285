import os

CLOUD_PROVIDER = os.getenv("CLOUD_PROVIDER")
if CLOUD_PROVIDER is None or CLOUD_PROVIDER not in ["google", "azure", "local"]: 
    raise ValueError("CLOUD_PROVIDER environment variable is not set. (possible values: 'google', 'azure', 'local)")

DBT_REMOTE_URL = os.getenv("DBT_REMOTE_URL")
if DBT_REMOTE_URL is None:
    raise ValueError("DBT_REMOTE_URL environment variable is not set.")