from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma


def prepare_category_vector_db(category, df_category, collection_name, chroma_client):
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    # Combine issue and description into a single text field for embedding
    df_category['combined_text'] = df_category['Issue'] + " " + df_category['Description']
    # Extract metadata and convert it to string format
    metadata = df_category[['Date','Category','Agent Name','Resolution','Resolved']].astype(str).to_dict('records')

    Chroma.from_texts(
        texts=df_category['combined_text'].tolist(),
        embedding=embedding_function,
        collection_name=collection_name,
        client=chroma_client,
        ids=df_category['Ticket ID'].astype(str).tolist(),
        metadatas=metadata
    )


def query_tickets(collection, ticket_text, n_results=2):
    # # Query the collection for documents similar to the ticket_text and returns top n results
    results = collection.query(
        query_texts=[ticket_text],
        n_results=n_results,
    )
    return results