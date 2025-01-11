import os
import pandas as pd
from tqdm.auto import tqdm  # Importa la versión notebook-friendly de tqdm
import sys
sys.path.append('/home/snparada/Spacionatural/Libraries')
from openai_lib.embeddings import TextEmbedding

text_embedding_obj = TextEmbedding()

def simple_read_csv(file_path):
    try:
        # Try reading with UTF-8 encoding
        return pd.read_csv(file_path, encoding='utf-8', sep = '\t')
    except UnicodeDecodeError:
        # If UTF-8 fails, try with UTF-16 encoding
        try:
            return pd.read_csv(file_path, encoding='utf-16', sep='\t')
        except Exception:
            return None

"""
 Variables
"""
nich = 'envases'
model = "text-embedding-3-large" # text-embedding-ada-002
file_path = f'/home/snparada/Spacionatural/Data/Historical/Keywords_Planner/{nich}.csv'
embedded_path = f'/home/snparada/Spacionatural/Data/Embeddings/Keywords/{nich}_embedded_keywords.csv'

df = simple_read_csv(file_path)
df['Avg. monthly searches'] = df['Avg. monthly searches'].fillna(0)
df = df[df['Avg. monthly searches']>0]

tqdm.pandas(desc="Calculating embeddings")  # Inicializa tqdm con pandas
df['ada_embedding'] = df['Keyword'].progress_apply(lambda x: text_embedding_obj.get_embedding(x,model))
df = df.rename(columns={'Keyword': 'Top queries'})
df = df[['Top queries', 'ada_embedding']]
df.to_csv(embedded_path, index=False, encoding = 'utf-8-sig')
