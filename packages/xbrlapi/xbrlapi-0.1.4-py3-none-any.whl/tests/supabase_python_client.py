from supabase import create_client, Client

# Base URL and anon key for the Supabase database
url: str = "https://ctegcahvqfnbhudovzpy.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN0ZWdjYWh2cWZuYmh1ZG92enB5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyMTA2MjIzMCwiZXhwIjoyMDM2NjM4MjMwfQ.ttYnyIKlNvD2ELiFj8UZ3ts-D3d5jVZ-50s6idA46bA"

supabase: Client = create_client(url, key)


response=supabase.table("subscriptions").select("*").execute()
ids = [record['id'] for record in response.data]
user_api_key = "sub_1Pcsjz0098m8TkrklZjCju6o"
if user_api_key in ids:
    print("Valid subscription ID set successfully")
else:
    print("Invalid subscription ID")
    
#example of a query
xbrl_query = (
    supabase.table("xbrl_data")
    .select("name, tag")
    .eq("name", "NATIONAL INSTRUMENTS CORP")
    .execute()
)
#convert xbql_query to a pandas dataframe
import pandas as pd
df = pd.DataFrame(xbrl_query.data)
print(df)