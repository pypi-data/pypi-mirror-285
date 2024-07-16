# xbrlapi/api.py
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import pandas as pd

load_dotenv()

SUPABASE_URL="https://ctegcahvqfnbhudovzpy.supabase.co"
SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN0ZWdjYWh2cWZuYmh1ZG92enB5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjEwNjIyMzAsImV4cCI6MjAzNjYzODIzMH0.ho1LMUa-WzyrR8Q3-cWvknZwbJqBhAZXK0nWiRIcXR8"


supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def validate_subscription_id(subscription_id):
    try:
        response = supabase.table("subscriptions").select("*").eq("id", subscription_id).eq("status", "active").execute()
        return len(response.data) > 0
    except Exception as e:
        print("Exception during subscription ID validation:", e)
        return False

def get_financial_data(subscription_id, ticker, year, data_type):
    if not validate_subscription_id(subscription_id):
        raise ValueError("Invalid or inactive subscription ID")
    
    response = supabase.table("xbrl_data").select("*").eq("name", ticker).eq("ddate", year).eq("tag", data_type).execute()
    
    df = pd.DataFrame(response.data)
    return df
