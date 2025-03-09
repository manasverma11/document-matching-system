from flask import Flask, jsonify, request, session
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/admin/credit-requests", methods=["GET"])
def view_credit_requests():
    """Admin views all pending credit requests"""
    if "user_id" not in session or session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM credit_requests WHERE status = 'pending'")
    requests = [dict(row) for row in cur.fetchall()]
    conn.close()

    return jsonify(requests)

@app.route("/admin/credit-approve", methods=["POST"])
def approve_credit_request():
    """Admin approves a credit request"""
    if "user_id" not in session or session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    request_id = data.get("request_id")
    user_id = data.get("user_id")
    credits = data.get("credits")

    conn = get_db_connection()
    cur = conn.cursor()

    # Update user credits
    cur.execute("UPDATE users SET credits = credits + ? WHERE id = ?", (credits, user_id))

    # Mark request as approved
    cur.execute("UPDATE credit_requests SET status = 'approved' WHERE id = ?", (request_id,))
    
    conn.commit()
    conn.close()

    return jsonify({"message": "Credits approved successfully"})

@app.route("/admin/credit-deny", methods=["POST"])
def deny_credit_request():
    """Admin denies a credit request"""
    if "user_id" not in session or session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    request_id = data.get("request_id")

    conn = get_db_connection()
    cur = conn.cursor()

    # Mark request as denied
    cur.execute("UPDATE credit_requests SET status = 'denied' WHERE id = ?", (request_id,))
    
    conn.commit()
    conn.close()

    return jsonify({"message": "Credit request denied"})
