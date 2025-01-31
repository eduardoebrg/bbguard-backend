from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)  # Permite que o frontend acesse o backend

# Configuração do Banco de Dados
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "pizza",
    "database": "esp32_sensordata"
}

# 📌 Rota para receber os dados do ESP32-C3 e armazená-los no banco


@app.route("/send-data", methods=["POST"])
def receive_data():
    try:
        data = request.json
        session_id = data["session_id"]
        device_id = data["device_id"]
        x = data["x"]
        y = data["y"]
        z = data["z"]

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        sql = "INSERT INTO accelerometer (session_id, device_id, x, y, z) VALUES (%s, %s, %s, %s, %s)"
        values = (session_id, device_id, x, y, z)
        cursor.execute(sql, values)
        conn.commit()

        cursor.close()
        conn.close()
        return jsonify({"message": "✅ Dados inseridos com sucesso!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 📌 Rota para marcar um evento no banco (chamada pelo site)


@app.route("/mark-event", methods=["POST"])
def mark_event():
    try:
        data = request.json
        record_id = data["id"]  # ID do dado a ser marcado

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        sql = "UPDATE accelerometer SET event_marker = 1 WHERE id = %s"
        cursor.execute(sql, (record_id,))
        conn.commit()

        cursor.close()
        conn.close()
        return jsonify({"message": "✅ Evento marcado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 📌 Rota para listar os últimos dados gravados


@app.route("/get-data", methods=["GET"])
def get_data():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        sql = "SELECT * FROM accelerometer ORDER BY id DESC LIMIT 10"
        cursor.execute(sql)
        data = cursor.fetchall()

        cursor.close()
        conn.close()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "🚀 Backend Flask está rodando na nuvem!"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
