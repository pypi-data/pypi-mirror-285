# xbrlapi/api.py
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import pandas as pd

# Load environment variables from .env file
load_dotenv()

# Retrieve Base URL and Service Role Key from environment variables
BASE_URL = os.getenv("SUPABASE_URL")
SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Create Supabase client
supabase: Client = create_client(BASE_URL, SERVICE_ROLE_KEY)

def validate_subscription_id(subscription_id):
    """
    Validate the provided subscription ID against the subscriptions table.

    Args:
        subscription_id (str): The subscription ID provided by the user.

    Returns:
        bool: True if the subscription ID is valid and active, False otherwise.
    """
    try:
        response = supabase.table("subscriptions").select("*").eq("id", subscription_id).eq("status", "active").execute()
        return len(response.data) > 0
    except Exception as e:
        print("Exception during subscription ID validation:", e)
        return False

def get_financial_data(subscription_id, ticker, year, data_type):
    """
    Fetch financial data for a given ticker, year, and data type from Supabase.

    Args:
        subscription_id (str): The subscription ID provided by the user.
        ticker (str): The stock ticker symbol.
        year (str): The year for which data is requested.
        data_type (str): The type of financial data requested.

    Returns:
        pd.DataFrame: The financial data in a pandas DataFrame.

    Raises:
        ValueError: If the subscription ID is not valid.
    """
    if not validate_subscription_id(subscription_id):
        raise ValueError("Invalid or inactive subscription ID")
    
    # Query the financial data
    response = supabase.table("xbrl_data").select("*").eq("name", ticker).eq("ddate", year).eq("tag", data_type).execute()
    
    # Convert the response to a pandas DataFrame
    df = pd.DataFrame(response.data)
    return df
