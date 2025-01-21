from pathlib import Path

ROOT_DIR = Path('D:/ml_projects/aleph_alpha/aa-case-study-ai-solutions-engineer-main')
DATA_DIR = ROOT_DIR / 'data'
OLD_TICKETS_DIR = DATA_DIR / 'old_tickets'
QUERY_TICKET_SAVE_PATH = DATA_DIR / 'new_tickets' / 'ticket_dump_4.csv'
NEW_TICKETS_PATH = DATA_DIR / 'new_tickets.csv'

# Configuration settings for the ticket_resolution package
API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
TOKEN = "Your_huggingface_token"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"