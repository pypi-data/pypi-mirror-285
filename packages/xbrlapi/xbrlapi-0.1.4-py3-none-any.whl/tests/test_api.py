from supabase import create_client, Client

# Base URL and anon key for the Supabase database
BASE_URL = "https://ctegcahvqfnbhudovzpy.supabase.co"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN0ZWdjYWh2cWZuYmh1ZG92enB5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjEwNjIyMzAsImV4cCI6MjAzNjYzODIzMH0.ho1LMUa-WzyrR8Q3-cWvknZwbJqBhAZXK0nWiRIcXR8"

# Global variable to store the user's subscription ID and Supabase client
SUBSCRIPTION_ID = None
supabase: Client = create_client(BASE_URL, ANON_KEY)

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
        print("Exception during subscription ID validation:", e)  # Debug line
        return False

def set_api_key(subscription_id):
    """
    Set the subscription ID for user-specific requests.

    Args:
        subscription_id (str): The subscription ID provided by the user.
    """
    global SUBSCRIPTION_ID
    if not validate_subscription_id(subscription_id):
        raise ValueError("Invalid or inactive subscription ID")
    SUBSCRIPTION_ID = subscription_id

def get_financial_data(ticker, year, data_type):
    """
    Fetch financial data for a given ticker, year, and data type from Supabase.

    Args:
        ticker (str): The stock ticker symbol.
        year (str): The year for which data is requested.
        data_type (str): The type of financial data requested.

    Returns:
        list: The financial data in JSON format.

    Raises:
        ValueError: If the subscription ID is not set or invalid.
    """
    if SUBSCRIPTION_ID is None:
        raise ValueError("Subscription ID is not set. Use set_api_key() to set it.")
    
    # Example query (adjust according to your table structure)
    response = supabase.table("xbrl_data").select("*").eq("name", ticker).eq("ddate", year).eq("tag", data_type).execute()
    return response.data
