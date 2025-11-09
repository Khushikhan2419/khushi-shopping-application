from flask import Flask, request, jsonify
import pymysql
from flask_cors import CORS
import bcrypt

app = Flask(__name__)
CORS(app)

# ---------------- DATABASE CONFIG ----------------
db_config = {
    "host": "  ",
    "user": "admin",
    "password": "Cloud1234",
    "database": "khushi"
}

def get_db_connection():
    return pymysql.connect(
        host=db_config["host"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        cursorclass=pymysql.cursors.DictCursor
    )

# ---------------- REGISTER USER ----------------
@app.route("/api/save", methods=["POST"])
def save_user():
    try:
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            return jsonify({"error": "All fields are required"}), 400

        # Hash password
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        cursor.execute(sql, (username, email, hashed_pw))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "User registered successfully"}), 200

    except pymysql.err.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- LOGIN USER ----------------
@app.route("/api/login", methods=["POST"])
def login_user():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        # Check credentials
        if user and bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
            return jsonify({
                "message": "Login successful",
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"]
                }
            }), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- GET ALL USERS ----------------
@app.route("/api/users", methods=["GET"])
def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, created_at FROM users ORDER BY id DESC")
        users = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
