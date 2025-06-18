from flask import Flask, request, render_template, jsonify
from query import run_query_with_results

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")
    answer, citations = run_query_with_results(question)
    return jsonify({"answer": answer, "citations": citations})

if __name__ == "__main__":
    app.run(debug=True)
