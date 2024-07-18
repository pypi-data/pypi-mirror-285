import os
from dotenv import load_dotenv
from supabase import create_client, Client
import pandas as pd

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = "https://ctegcahvqfnbhudovzpy.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN0ZWdjYWh2cWZuYmh1ZG92enB5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjEwNjIyMzAsImV4cCI6MjAzNjYzODIzMH0.ho1LMUa-WzyrR8Q3-cWvknZwbJqBhAZXK0nWiRIcXR8"

supabase: Client = None  # Initialized later through the connect function

def create_supabase_client(subscription_id):
    global supabase
    
    # Create a Supabase client using the anonymous key
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    # Attempt to query the subscriptions table for the provided ID and status
    response = supabase.table("subscriptions").select("*").eq("id", subscription_id).eq("status", "active").execute()
    
    # Check if the response contains any data
    if not response.data:
        raise ValueError("Invalid or inactive subscription ID")
    print("Success! You are connected to XBRLInsights")
    return supabase  # Return the initialized supabase client

def connect(subscription_id):
    global supabase
    supabase = create_supabase_client(subscription_id)  # Validate and connect to Supabase

def get_financial_data(ticker, year=None, data_type=None):
    if not supabase:
        raise Exception("Not connected. Please establish a connection using connect().")
    query = supabase.table("xbrl_data").select("*").eq("name", "NATIONAL INSTRUMENTS CORP")
    response = query.execute()
    df = pd.DataFrame(response.data)
    if len(df)>0:
        return df
    else:
        print("No data found")

