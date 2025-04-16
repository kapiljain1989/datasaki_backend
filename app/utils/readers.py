# app/utils/readers.py
import pandas as pd
import boto3
import sqlalchemy
from app.utils.logging import logger

def read_from_file(connector):
    path = connector.file_path
    logger.info(f"Reading file from {path}")
    if connector.type == "csv":
        return pd.read_csv(path)
    elif connector.type == "xlsx":
        return pd.read_excel(path)
    elif connector.type == "txt":
        return pd.read_table(path)
    elif connector.type == "pdf":
        # Use pdfplumber or PyMuPDF
        return extract_text_from_pdf(path)
    elif connector.type == "image":
        return {"image_path": path}  # For now just return path
    else:
        raise ValueError("Unsupported file type")

def read_from_db(connector):
    logger.info(f"Reading from DB with config: {connector.config}")
    engine = sqlalchemy.create_engine(connector.config["connection_string"])
    query = connector.config["query"]
    return pd.read_sql(query, engine)

def read_from_cloud(connector):
    logger.info(f"Reading from cloud connector: {connector.connector_type}")
    # Example for S3
    if connector.connector_type == "s3":
        s3 = boto3.client('s3')
        obj = s3.get_object(Bucket=connector.config["bucket"], Key=connector.config["key"])
        return pd.read_csv(obj['Body'])
    raise ValueError("Cloud connector not implemented")

def extract_text_from_pdf(path):
    import pdfplumber
    logger.info(f"Extracting text from PDF: {path}")
    with pdfplumber.open(path) as pdf:
        return pd.DataFrame({"text": [page.extract_text() for page in pdf.pages]})
