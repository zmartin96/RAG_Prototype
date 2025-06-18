import json
import re
import requests
import chromadb
from chromadb import PersistentClient
from datetime import datetime

def get_question_embedding(question, model="mxbai-embed-large"):
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": model, "prompt": question}
    )
    response.raise_for_status()
    return response.json()["embedding"]

def retrieve_similar_chunks(query_vector, collection_name="work_center_notes", top_k=10):
    client = PersistentClient(path="./vectorstore")
    collection = client.get_or_create_collection(name=collection_name)

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "embeddings"]
    )
    return results

def build_prompt(question, chunks):
    context = "\n\n".join(
        f"[{i+1}] (EQNO {meta.get('eqno')}, Shift {meta.get('shift')}, Date {datetime.fromtimestamp(meta.get('prod_date', 0)/1000).strftime('%Y-%m-%d') if isinstance(meta.get('prod_date'), int) else meta.get('prod_date')})\n{doc}"
        for i, (doc, meta) in enumerate(zip(chunks["documents"][0], chunks["metadatas"][0]))
    )

    system_note = """
Interpret the following work center log entries. Each entry includes:
- EQNO: the machine or press number. For example, "Press 5" refers to EQNO 005
- SHIFT: the shift during which the note was logged
- PROD_DATE: the production date of the log (formatted as YYYY-MM-DD)
- JOBNO: the job number, which may be helpful for context

When answering, use EQNO to determine which press/machine is referenced. Do not guess — only answer based on exact EQNO matches in the context. If an EQNO is not present, say so. Ignore semantically similar logs with other EQNOs. Same goes for the rest of the metadata.
"""

    prompt = f"""{system_note}

### Context:
{context}

### Question:
{question}

### Answer:"""
    return prompt

def ask_llm(prompt, model="deepseek-r1", strip_thinking=True):
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
    )
    response.raise_for_status()
    answer = response.json()["message"]["content"]

    if strip_thinking:
        answer = re.sub(r"<think>.*?</think>\s*", "", answer, flags=re.DOTALL)

    return answer.strip()

def run_query(question):
    query_vector = get_question_embedding(question)
    chunks = retrieve_similar_chunks(query_vector)

    if not chunks["documents"]:
        print("No matching documents found.")
        return

    prompt = build_prompt(question, chunks)
    answer = ask_llm(prompt)

    print("\n🧠 Response:\n")
    print(answer)

    print("\n📚 Citations:")
    for i, metadata in enumerate(chunks["metadatas"][0]):
        ts = metadata.get("prod_date")
        if isinstance(ts, int) and ts > 1e12:  # assume millis
            try:
                ts = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
            except:
                pass
        print(f"[{i+1}] Job {metadata.get('jobno')} | EQNO {metadata.get('eqno')} | Shift {metadata.get('shift')} | Date {ts}")

if __name__ == "__main__":
    question = input("❓ Please enter a prompt: ")
    run_query(question)



def run_query_with_results(question):
    query_vector = get_question_embedding(question)
    chunks = retrieve_similar_chunks(query_vector)

    if not chunks["documents"]:
        return "No matching documents found.", []

    prompt = build_prompt(question, chunks)
    answer = ask_llm(prompt)

    citations = []
    for i, metadata in enumerate(chunks["metadatas"][0]):
        ts = metadata.get("prod_date")
        if isinstance(ts, int) and ts > 1e12:
            ts = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
        citations.append({
            "index": i + 1,
            "jobno": metadata.get("jobno"),
            "eqno": metadata.get("eqno"),
            "shift": metadata.get("shift"),
            "prod_date": ts
        })

    return answer, citations
