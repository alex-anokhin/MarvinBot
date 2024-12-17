import pandas as pd
from notion_client import Client
from dotenv import load_dotenv
import os

# Load enviroment variables from the .env-file
load_dotenv()

# Notion API-Token from environment variables
notion_api_token = os.getenv("NOTION_API_TOKEN")
notion = Client(auth=notion_api_token)

# Notion database ID
database_id = "01328f81282340fc93d9398a5314f8c4"

# Fetch data from the Notion
def fetch_notion_data(database_id):
    results = notion.databases.query(database_id=database_id).get("results")
    print (results)
    return results

# Convert data to a DataFrame ans structure it
def notion_to_dataframe(results):
    data = []

    for result in results:
        properties = result.get("properties", {})
        
        # Extrahieren des Namens
        title_property = properties.get("Page")
        title = ""
        if title_property and "title" in title_property and title_property["title"]:
            title = title_property["title"][0].get("plain_text", "")
        
        # Extrahieren des Links
        link = result.get("url", "")
        
        # Hinzufügen der Daten zur Liste
        data.append({"Page": title, "Links": link})

    df = pd.DataFrame(data)
    return df

# Compare and update the Excel file
def update_excel_file(new_df, file_path):
    try:
        old_df = pd.read_excel(file_path)
    except FileNotFoundError:
        old_df = pd.DataFrame()

    if old_df.equals(new_df):
        print("Everything is up to date.")
    else:
        new_df.to_excel(file_path, index=False)
        print("Data successfully saved to 'notion_data.xlsx'.")

# Main function
if __name__ == "__main__":
    results = fetch_notion_data(database_id)
    new_df = notion_to_dataframe(results)
    update_excel_file(new_df, "notion_data.xlsx")
