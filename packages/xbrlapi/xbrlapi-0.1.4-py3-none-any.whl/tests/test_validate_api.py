# tests/test_validate_api.py
from xbrlapi import get_financial_data
# Test with a valid subscription ID
try:
    df = get_financial_data("sub_1Pcsjz0098m8TkrklZjCju6o", "NATIONAL INSTRUMENTS CORP", "2022-12-31", "InventoryNet")  # Replace with an actual valid subscription ID
    print("Valid subscription ID set successfully")
    print(df)
except ValueError as e:
    print("Failed to set valid subscription ID:", e)
