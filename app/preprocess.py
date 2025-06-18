import json
import uuid
from pathlib import Path
import pandas as pd
import datetime

def load_notes(file_path="log_details.json"):
    df = pd.read_json(file_path, lines=True)

    # normalize column names to lowercase
    df.columns = [col.lower() for col in df.columns]
    return df

def chunk_text(text, max_tokens=300):
    # naive chunking by sentences for prototyping
    sentences = text.split(". ")
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_tokens:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def preprocess_notes(df, max_tokens=300):
    records = []

    for _, row in df.iterrows():
        if not isinstance(row.get("log_text"), str):
            continue

        chunks = chunk_text(row["log_text"], max_tokens=max_tokens)
        
        try:
            prod_date_str = datetime.fromtimestamp(row.get("prod_date") / 1000).strftime('%Y-%m-%d')
        except:
            prod_date_str = str(row.get("prod_date"))

        for i, chunk in enumerate(chunks):
            record = {
                "id": str(uuid.uuid4()),
                "text": f"EQNO {row.get('eqno')} | JOB {row.get('jobno')} | DATE {prod_date_str} | SHIFT {row.get('shift')}\n{chunk}",
                "metadata": {
                    "jobno": row.get("jobno"),
                    "eqno": row.get("eqno"),
                    "shift": row.get("shift"),
                    "prod_date": row.get("prod_date"),
                    "userid": row.get("userid"),
                    "log_detail_id": row.get("log_detail_id"),
                    "chunk_index": i,
                }
            }
            records.append(record)

    return records

def save_preprocessed(records, output_path="preprocessed_chunks.json"):
    with open(output_path, "w", encoding="utf-8") as f:
        for record in records:
            json.dump(record, f)
            f.write("\n")
    print(f"Successfully ssaved {len(records)} chunks to {output_path}")

if __name__ == "__main__":
    df = load_notes()
    records = preprocess_notes(df)
    save_preprocessed(records)
