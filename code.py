from flask import Flask, request, jsonify, render_template
from datetime import datetime
import os

try:
    from google.cloud import firestore
    db = firestore.Client()
    tasks_ref = db.collection("tasks")
except ImportError:
    db = None
    tasks_ref = None
    print("Error: google.cloud.firestore module not found. Install it using 'pip install google-cloud-firestore'")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tasks', methods=['GET'])
def get_tasks():
    if not tasks_ref:
        return jsonify({"error": "Firestore is not initialized"}), 500
    tasks = [{**doc.to_dict(), "id": doc.id} for doc in tasks_ref.stream()]
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def add_task():
    if not tasks_ref:
        return jsonify({"error": "Firestore is not initialized"}), 500
    data = request.json
    if 'text' not in data or not data['text'].strip():
        return jsonify({"error": "Task text is required"}), 400
    task = {"text": data['text'], "timestamp": datetime.utcnow().isoformat()}
    task_ref = tasks_ref.add(task)
    return jsonify({"id": task_ref[1].id, **task}), 201

@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    if not tasks_ref:
        return jsonify({"error": "Firestore is not initialized"}), 500
    task_doc = tasks_ref.document(task_id)
    if task_doc.get().exists:
        task_doc.delete()
        return jsonify({"message": "Task deleted successfully"})
    return jsonify({"error": "Task not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
