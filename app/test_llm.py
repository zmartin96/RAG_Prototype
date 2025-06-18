import requests

prompt = "Summarize what a hydraulic press does in two sentences."

res = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "deepseek-r1",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False # turn off streaming for a 
    }
)

answer=res.json()["message"]["content"]
print("\nResponse:\n")
print(answer.split("</think>")[-1].strip() if "<think>" in answer else answer)
print("\n")