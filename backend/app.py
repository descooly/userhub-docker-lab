from flask import Flask, jsonify, request
from flask_cors import CORS
import redis
import psycopg2
import psycopg2.extras
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'db'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=int(os.getenv('DB_PORT', 5432))
    )

@app.route('/')
def home():
    redis_client.incr('requests:total')
    return jsonify({
        "app": "UserHub - Docker Lab",
        "version": "2.0",
        "description": "Полноценное CRUD-приложение для управления пользователями",
        "endpoints": {
            "GET /": "Информация о приложении",
            "GET /users": "Список пользователей",
            "POST /users": "Создать пользователя",
            "DELETE /users/<id>": "Удалить пользователя",
            "GET /stats": "Статистика запросов (Redis)",
            "GET /health": "Проверка здоровья"
        }
    })

@app.route('/users', methods=['GET'])
def get_users():
    redis_client.incr('requests:total')
    redis_client.incr('requests:get_users')
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # Изменяем сортировку на ORDER BY id ASC
        cur.execute("SELECT id, name, email, created_at FROM users ORDER BY id ASC")
        users = cur.fetchall()
        for user in users:
            user['created_at'] = user['created_at'].isoformat()
        cur.close()
        conn.close()
        return jsonify({"users": users, "count": len(users)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users', methods=['POST'])
def create_user():
    redis_client.incr('requests:total')
    redis_client.incr('requests:create_user')
    data = request.get_json()
    if not data or not data.get('name') or not data.get('email'):
        return jsonify({"error": "name и email обязательны"}), 400
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id, name, email, created_at",
            (data['name'], data['email'])
        )
        user = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        user['created_at'] = user['created_at'].isoformat()
        return jsonify({"message": "Пользователь создан", "user": user}), 201
    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": "Пользователь с таким email уже существует"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    redis_client.incr('requests:total')
    redis_client.incr('requests:delete_user')
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id = %s RETURNING id", (user_id,))
        deleted = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if deleted:
            return jsonify({"message": f"Пользователь {user_id} удалён"})
        return jsonify({"error": "Пользователь не найден"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stats')
def stats():
    redis_client.incr('requests:total')
    redis_client.incr('requests:stats')
    return jsonify({
        "total_requests": int(redis_client.get('requests:total') or 0),
        "get_users": int(redis_client.get('requests:get_users') or 0),
        "create_user": int(redis_client.get('requests:create_user') or 0),
        "delete_user": int(redis_client.get('requests:delete_user') or 0),
        "stats": int(redis_client.get('requests:stats') or 0)
    })

@app.route('/health')
def health():
    status = {"backend": "healthy"}
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        status["database"] = "healthy"
    except Exception as e:
        status["database"] = "error"
    try:
        if redis_client.ping():
            status["redis"] = "healthy"
    except:
        status["redis"] = "error"
    return jsonify(status), 200 if all(v == "healthy" for v in status.values() if v != "error") else 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
