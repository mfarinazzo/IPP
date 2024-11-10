import os
import glob
import pandas as pd
import subprocess

# Definir o diretório de entrada contendo os arquivos CSV
output_directory = './output_caged'
log_file = 'log_Ajuste.txt'

# Iterar sobre cada arquivo CSV no diretório
for file_name in glob.glob(os.path.join(output_directory, '*.csv')):
    # Carregar o arquivo CSV em um DataFrame
    df = pd.read_csv(file_name, delimiter=';')

   # Renomear a coluna 'cbo2002ocupação' para 'ocupacao'
    if 'cbo_mun' in file_name:
        df = df.rename(columns={'cbo2002ocupação': 'ocupacao'})

    # Remover linhas onde a coluna é igual a 99 ou 9
    if 'regiao' in file_name:
        df = df[(df['regiao'] != 99) & (df['regiao'] != 9)]
        df = df.drop(columns=['uf'])
    elif 'uf' in file_name:
        df = df[(df['uf'] != 99)]
        df = df.drop(columns=['regiao'])

    if 'cnae_uf' in file_name: 
        df = df.rename(columns={'codigo': 'cnaeuf'})
    elif 'cbo_uf' in file_name:
        df = df.rename(columns={'codigo': 'cbouf'})
    if 'cnae_regiao' in file_name: 
        df = df.rename(columns={'codigo': 'cnaeregiao'})
    elif 'cbo_regiao' in file_name:
        df = df.rename(columns={'codigo': 'cboregiao'})

    # Resetar o índice do DataFrame para manter a ordem de ID correta
    # O parâmetro 'drop=True' descarta o índice antigo
    df = df.reset_index(drop=True)

    # Atualizar a coluna 'id' para refletir a nova ordem
    df['id'] = df.index + 1

    # if 'data' in df.columns:
    #     # Converter a coluna 'data' para o formato correto
    #     if 'ocupacoes' or 'subclasses' not in file_name:
    #         df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')

    # Verificar o nome do arquivo e remover colunas conforme a lógica solicitada
    if 'mun' in file_name:
        df = df.drop(columns=['regiao'])
        df = df.drop(columns=['uf'])
    
    output_file_name = file_name.replace('_output.csv', '.csv')
    df.to_csv(output_file_name, sep=';', index=False)

for arquivo in os.listdir(output_directory):
    if 'output' in arquivo:
        # Excluir o arquivo .7z após a extração
        caminho_completo = os.path.join(output_directory, arquivo)
        os.remove(caminho_completo)
    
def registrar_log(mensagem):
    with open(log_file, 'a') as f:
        f.write(mensagem + '\n')

# Tentar chamar o script enviaPHP.py
try:
    subprocess.run(['python', 'enviaPHP.py'], check=True)
    registrar_log("Script enviaPHP.py executado com sucesso.")
except FileNotFoundError:
    registrar_log("Erro: Script enviaPHP.py não encontrado.")
except subprocess.CalledProcessError as e:
    registrar_log(f"Erro ao executar o script enviaPHP.py: {e}")