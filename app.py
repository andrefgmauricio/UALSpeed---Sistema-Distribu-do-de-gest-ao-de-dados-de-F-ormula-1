from dotenv import load_dotenv
import os
import pymysql
from flask import Flask, request, jsonify
from kazoo.client import KazooClient
import redis


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

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

zk = KazooClient(hosts='localhost:2181')
zk.start()

zk.ensure_path("/ualspeed/api")
if not zk.exists("/ualspeed/api/servidor_1"):
    zk.create("/ualspeed/api/servidor_1", b"online", ephemeral=True)


@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'online', 'projeto': 'UalSeed Telemetry'}), 200 

@app.route('/api/telemetria', methods=['POST'])
def receber_telemetria():
    dados = request.get_json()

    if not dados or 'piloto_id' not in dados or 'velocidade' not in dados:
        return jsonify({"erro": "Dados incompletos!"}), 400
    
    piloto_id = dados['piloto_id']
    velocidade = dados['velocidade']
    rpm = dados.get('rpm', 0)
    combustivel = dados.get('combustivel', 0.0)

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

        chave_redis=f"piloto:{piloto_id}:atual"
        r.hset(chave_redis, mapping={
            "velocidade": velocidade,
            "rpm": rpm,
            "combustivel": combustivel
        })

        r.expire(chave_redis, 60)

        return jsonify({"mensagem": "Telemetria recebida com sucesso!"}), 201
    except Exception as e:
        return jsonify({"erro": f"Falha na Base de Dados: {str(e)}"}), 500

@app.route('/api/telemetria/<int:piloto_id>', methods=['GET'])
def obter_telemetria_atual(piloto_id):
    chave_redis = f"piloto:{piloto_id}:atual"

    dados_cache = r.hgetall(chave_redis)

    if dados_cache:
        return jsonify({
            "fonte": "Redis Cache (RAM)",
            "piloto_id": piloto_id,
            "dados": dados_cache
        }), 200
                   

    return jsonify({"erro": "Dados em tempo real indisponíveis ou expirados."}), 404
        
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
