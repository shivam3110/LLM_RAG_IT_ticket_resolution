import chromadb
import pandas as pd

from ticket_resolution.data_processing import get_old_tickets_df
from ticket_resolution.embedding_utils import prepare_category_vector_db
from ticket_resolution.response_generation import get_direct_responses_old_ticket, generate_llm_responses

from ticket_resolution.config import DATA_DIR, OLD_TICKETS_DIR

chroma_client = chromadb.PersistentClient()


def user_choice_interface():
    print("Select the mode of operation:")
    print("1: Direct Query from past tickets")
    print("2: Generate response using Meta-Llama model")
    choice = input("Enter choice (1 or 2): ")
    return choice


def initialize_database(OLD_TICKETS_DIR):
    print("Loading and processing old tickets...")
    old_tickets_df = get_old_tickets_df(OLD_TICKETS_DIR)
    for category in old_tickets_df['Category'].unique():
        df_category = old_tickets_df[old_tickets_df['Category'] == category].copy()
        collection_name = category.replace(' ', '_')
        collection = chroma_client.get_or_create_collection(name=collection_name)
        print("Preparing vector database...")
        prepare_category_vector_db(category, df_category, collection_name, chroma_client)


def main():
    
    initialize_database(OLD_TICKETS_DIR)
    new_tickets_path = DATA_DIR / 'new_tickets.csv'

    choice = user_choice_interface()
    if choice == '1':
        results = get_direct_responses_old_ticket(chroma_client, new_tickets_path)
    elif choice == '2':
        results = generate_llm_responses(chroma_client, new_tickets_path)
    else:
        print("Invalid choice. Exiting program.")
        return
    
    for result in results:        
        print(result)


if __name__ == '__main__':
    main()