import os
import pandas as pd
import requests
import json
import time

LOG_FILE = 'process_log.txt'

def write_log(message):
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(f"{message}\n")

def send_data_to_api(data_json, api_url):
    headers = {'Content-Type': 'application/json'}
    max_retries = 5
    retry_count = 0

    while retry_count < max_retries:
        try:
            # Enviar dados para a API
            response = requests.post(api_url, json=data_json, headers=headers)
            response.raise_for_status()  # Levanta um erro para status de resposta HTTP não bem-sucedido

            # Verificar resposta
            try:
                response_json = response.json()
            except ValueError:
                response_json = {'status': 'error', 'message': 'Resposta inválida do servidor'}

            if response_json.get('status') == 'success':
                print(f"Dados enviados com sucesso: {response_json}")
                write_log(f"Dados enviados com sucesso: {response_json}")
                return True
            else:
                print(f"Falha ao enviar dados: {response_json}")
                write_log(f"Falha ao enviar dados: {response_json}")
                return False
        except requests.exceptions.HTTPError as http_err:
            print(f"Erro HTTP: {http_err}")
            print(f"Resposta do servidor: {response.text}")
            write_log(f"Erro HTTP: {http_err} - Resposta do servidor: {response.text}")
        except requests.exceptions.RequestException as req_err:
            print(f"Erro de solicitação: {req_err}")
            write_log(f"Erro de solicitação: {req_err}")
        except ValueError:
            print(f"Falha ao enviar dados: Resposta inválida do servidor")
            print(f"Resposta do servidor: {response.text}")
            write_log(f"Falha ao enviar dados: Resposta inválida do servidor - Resposta do servidor: {response.text}")

        retry_count += 1
        time.sleep(5)  # Espera 5 segundos antes de tentar novamente

    return False

def process_file_in_chunks(file_path, api_url, chunk_size=5000):
    # Ler o arquivo CSV usando pandas
    data = pd.read_csv(file_path, delimiter=';')

    # Substituir NaN por None
    data = data.where(pd.notnull(data), None)

    # Dividir os dados em partes menores
    num_chunks = (len(data) // chunk_size) + 1
    for i in range(num_chunks):
        start = i * chunk_size
        end = (i + 1) * chunk_size
        chunk = data[start:end]

        # Converter o chunk para JSON
        data_json = json.loads(chunk.to_json(orient='records'))

        # Debug: Exibir os primeiros registros do JSON
        print(f"Chunk {i+1}/{num_chunks} - Dados JSON (primeiros 2 registros): {json.dumps(data_json[:2], indent=2)}")

        # Enviar dados do chunk para a API
        print(f"Enviando dados do chunk {i+1}/{num_chunks}")
        write_log(f"Enviando dados do chunk {i+1}/{num_chunks} do arquivo {file_path}")
        success = send_data_to_api(data_json, api_url)

        if not success:
            write_log(f"Falha ao enviar chunk {i+1}/{num_chunks} do arquivo {file_path}. Tentativas esgotadas.")
            break

def determine_api_url(filename):
    if 'mun' in filename:
        return 'https://www.priceindex.com.br/automacaoFornecedores/automacaoFornecedores/inseremun.php'
    elif 'regiao' in filename or 'uf' in filename:
        return 'https://www.priceindex.com.br/automacaoFornecedores/automacaoFornecedores/insereregiao.php'
    elif filename in ['ocupacoes.csv', 'subclasse.csv']:
        return 'https://www.priceindex.com.br/automacaoFornecedores/automacaoFornecedores/insere.php'
    else:
        raise ValueError(f"Nome de arquivo não reconhecido: {filename}")

def process_folder(folder_path, chunk_size=5000):
    for filename in os.listdir(folder_path):
        if '_mun_' in filename:
            file_path = os.path.join(folder_path, filename)
            print(f"Lendo dados de {file_path}")
            try:
                api_url = determine_api_url(filename)
                process_file_in_chunks(file_path, api_url, chunk_size)
            except ValueError as e:
                write_log(str(e))

# Caminho para o diretório contendo os arquivos CSV
folder_path = './mun'

# Chamar a função
process_folder(folder_path, chunk_size=5000)