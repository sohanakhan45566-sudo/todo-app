from flask import Flask, request, jsonify
import os
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Database connection
mongo_host = os.getenv('MONGO_HOST', 'localhost')
mongo_port = int(os.getenv('MONGO_PORT', 27017))

client = MongoClient(mongo_host, mongo_port)
db = client['todo_db']
todos_collection = db['todos']

@app.route('/')
def home():
    return "✅ TODO App is Running! Use /todos endpoint"

@app.route('/health')
def health():
    # Check database connection
    try:
        client.admin.command('ping')
        return jsonify({"status": "OK", "database": "connected"}), 200
    except:
        return jsonify({"status": "ERROR", "database": "disconnected"}), 500

@app.route('/todos', methods=['GET'])
def get_todos():
    todos = list(todos_collection.find({}, {'_id': False}))
    return jsonify(todos), 200

@app.route('/todos', methods=['POST'])
def create_todo():
    data = request.json
    todo = {
        "task": data.get('task'),
        "completed": False,
        "created_at": datetime.now().isoformat()
    }
    todos_collection.insert_one(todo)
    return jsonify({"message": "Todo created", "todo": todo}), 201

@app.route('/todos/<task>', methods=['DELETE'])
def delete_todo(task):
    result = todos_collection.delete_one({"task": task})
    if result.deleted_count > 0:
        return jsonify({"message": f"Todo '{task}' deleted"}), 200
    return jsonify({"error": "Todo not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)