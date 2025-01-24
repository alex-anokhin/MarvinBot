import os
from dotenv import load_dotenv
from notion_client import Client
from tqdm import tqdm

# Function to get all page IDs from a database (from Start page site)
def get_all_page_ids_from_database(notion_client, database_id):
    page_ids = []
    has_more = True
    next_cursor = None

    while has_more:
        response = notion_client.databases.query(
            **{"database_id": database_id, "start_cursor": next_cursor}
        )
        for page in response.get("results", []):
            page_ids.append(page["id"])
        has_more = response.get("has_more", False)
        next_cursor = response.get("next_cursor")

    return page_ids

# Function to get page title of page
def get_page_title(notion, page_id):
    page = notion.pages.retrieve(page_id)

    # Look for "Page" property
    if "Page" in page["properties"]:
        title_array = page["properties"]["Page"]["title"]
        if title_array and len(title_array) > 0:
            return title_array[0]["plain_text"]

    # Fallback if "Page" not found
    for prop_name, prop_value in page["properties"].items():
        if prop_value["type"] == "title":
            if prop_value["title"] and len(prop_value["title"]) > 0:
                return prop_value["title"][0]["plain_text"]

    return "Untitled"

# Recursive function to fetch text content from blocks
def fetch_text_content(notion, block_id):
    texts = []
    blocks = notion.blocks.children.list(block_id=block_id)

    for block in blocks["results"]:
        block_type = block.get("type")
        if block_type:
            # Get text content if it exists
            if "rich_text" in block.get(block_type, {}):
                text = "".join(
                    [t.get("plain_text", "") for t in block[block_type]["rich_text"]]
                )
                if text.strip():  # Check if empty text IMPORTANT!!!
                    texts.append(text)

            # Handle table_row blocks to look like a table
            elif block_type == "table_row":
                row_text = []
                for cell in block["table_row"]["cells"]:
                    cell_text = "".join([t.get("plain_text", "") for t in cell])
                    if cell_text.strip():
                        row_text.append(cell_text)
                if row_text:
                    texts.append(" | ".join(row_text))

        # Recursively go until page has children
        if block.get("has_children"):
            child_texts = fetch_text_content(notion, block["id"])
            texts.extend(child_texts)
        delete_useless_info(texts)
    return texts

# Function to make a link to a page
def make_url(title, page_id):
    return f"https://www.notion.so/42heilbronn/{title.replace(' ', '-')}-{page_id.replace('-', '')}"


# Remove useless info from texts
def delete_useless_info(texts):
    useless_info = "The page hasn’t been verified.\nThe information may be outdated and no longer correct!"
    if useless_info in texts:
        texts.remove(useless_info)

import psycopg2
import ollama

def fetch_all_data():
    try:
        # Load environment variables (need to create .env file with NOTION_TOKEN
        # and DB credentials)
        load_dotenv()
        str_embedd_size = int(os.getenv("STR_EMBEDD_SIZE"))
        str_overlap_size = int(os.getenv("STR_OVERLAP_SIZE"))
        
        # Connect to your postgres DB
        dbconn = psycopg2.connect(host=os.getenv("DB_HOST"),
                                  dbname=os.getenv("DB_NAME"),
                                  user=os.getenv("DB_USER"),
                                  password=os.getenv("DB_PASSWORD")
        )

        # Open a cursor to perform database operations
        dbcursor = dbconn.cursor()
        # Delete all data (only for debug and testing)
        query = ("DELETE FROM pages")
        dbcursor.execute(query)
        dbconn.commit()
        
        # Initialize Notion client
        notion = Client(auth=os.getenv("NOTION_TOKEN"))
        
        # All in 1 database i hardoceed the database id
        page_ids = get_all_page_ids_from_database(
            notion, "01328f81-2823-40fc-93d9-398a5314f8c4"
        )

    #    all_pages_content = {}

        # Process each page with cool progress bar (if Pasha want to remoove progress bar
        # just remove tqdm and desc="Processing pages", and also remove import tqdm)
        for page_id in tqdm(page_ids, desc="Processing pages"):
            try:
                page_title = get_page_title(notion, page_id)
                page_content = fetch_text_content(notion, page_id)
                page_url = make_url(page_title, page_id)
                page_text = " ".join(page_content)
                num = int(0)
                while (len(page_text) > 0):
                    response = ollama.embeddings(model="mxbai-embed-large",
                                                 prompt=page_text[0:str_embedd_size])
                    embedding = response["embedding"]
                    query = ("INSERT INTO pages (title, doc, link, embedding) VALUES (%s, %s, %s, %s)")
                    data = (page_title, page_text[0:str_embedd_size], page_url, embedding)
                    dbcursor.execute(query, data)
                    dbconn.commit()
                    rowscount = dbcursor.rowcount
                    print("""Insert part {0} of page '{1}'""".format(num, page_title))
                    num += 1
                    if (len(page_text) > str_embedd_size):
                        page_text = page_text[(str_embedd_size - str_overlap_size):]
                    else:
                        break
        dbcursor.close()
            except Exception as e:
                print(f"Error processing page {page_id}: {e}")
                continue
    except Exception as e:
        print(f"An error occurred: {e}")

fetch_all_data()
