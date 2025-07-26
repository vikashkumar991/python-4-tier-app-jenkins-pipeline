from flask import Flask, jsonify, render_template
import psycopg2
import redis
import json

app = Flask(__name__, template_folder='templates')

DB_HOST = 'postgres'
DB_NAME = 'users_db'
DB_USER = 'user'
DB_PASS = 'password'

REDIS_HOST = 'redis'
REDIS_PORT = 6379
r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


@app.route('/admin')
def admin_page():
    return render_template('admin.html')

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)

@app.route('/users', methods=['GET'])
def get_users():
    cached_users = r.get('users')

    if cached_users:
        return jsonify({"source": "redis", "users": json.loads(cached_users)})

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, email FROM users")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    users = [{"name": row[0], "email": row[1]} for row in rows]
    r.set('users', json.dumps(users))

    return jsonify({"source": "postgres", "users": users})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

