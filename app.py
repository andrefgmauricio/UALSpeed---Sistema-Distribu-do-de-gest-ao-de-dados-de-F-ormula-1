from dotenv import load_dotenv
import os
import pymysql
from flask import Flask, request, jsonify


load_dotenv()

app = Flask(__name__)


def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password=os.getenv('MYSQL_ROOT_PASSWORD'),
        database='ualspeed',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'online', 'projeto': 'UalSeed Telemetry'}), 200 

@app.route('/api/telemetria', methods=['POST'])
def receber_telemetria():
    dados = request.get_json()

    if not dados or 'piloto_id' not in dados or 'velocidade' not in dados:
        return jsonify({"erro": "Dados incompletos!"}), 400
    
    try:
        conexao = get_db_connection()
        with conexao.cursor() as cursor:
            sql = """
            INSERT INTO  telemetria (piloto_id, velocidade, rpm, combustivel)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (dados['piloto_id'], dados['velocidade'], dados.get('rpm'), dados.get('combustivel')))
        conexao.commit()
        conexao.close()

        return jsonify({"mensagem": "Telemetria recebida com sucesso!"}), 201
    except Exception as e:
        return jsonify({"erro": f"Falha na Base de Dados: {str(e)}"}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
