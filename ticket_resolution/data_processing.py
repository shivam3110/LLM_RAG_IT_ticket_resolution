import os
import pandas as pd

def get_old_tickets_df(directory):
    old_tickets = []
    for file in os.listdir(directory):
        if file.endswith('.csv'):
            old_tickets.append(pd.read_csv(os.path.join(directory, file)))
        elif file.endswith('.xlsx'):
            old_tickets.append(pd.read_excel(os.path.join(directory, file)))
        elif file.endswith('.json'):
            old_tickets.append(pd.read_json(os.path.join(directory, file)))
    
    return pd.concat(old_tickets, ignore_index=True)

