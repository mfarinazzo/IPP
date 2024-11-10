import os
import py7zr
import subprocess
log_file = 'log_ConverterCSV.txt'

def registrar_log(mensagem):
    with open(log_file, 'a') as f:
        f.write(mensagem + '\n')

# Definir o caminho da pasta contendo os arquivos .7z
pasta = 'CAGEDMOV_downloads'

# Verificar se a pasta existe
if not os.path.exists(pasta):
    registrar_log(f"Não foi possivel encontrar a pasta CAGEDMOV_downloads")

# Iterar sobre todos os arquivos na pasta
for arquivo in os.listdir(pasta):
    if arquivo.endswith('.7z'):
        caminho_7z = os.path.join(pasta, arquivo)
        
        # Extrair o arquivo .7z
        with py7zr.SevenZipFile(caminho_7z, mode='r') as z:
            z.extractall(path=pasta)
        
        # Excluir o arquivo .7z após a extração
        os.remove(caminho_7z)

# Iterar sobre todos os arquivos na pasta novamente para converter .txt para .csv
for arquivo in os.listdir(pasta):
    if arquivo.endswith('.txt'):
        caminho_txt = os.path.join(pasta, arquivo)
        caminho_csv = os.path.join(pasta, arquivo.replace('.txt', '.csv'))
        
        # Renomear o arquivo .txt para .csv
        os.rename(caminho_txt, caminho_csv)
    
    # Registrar a conversão no log
    registrar_log(f"Arquivo {arquivo} convertido para CSV")

# Tentar chamar o script cnaePorData.py
try:
    subprocess.run(['python', 'cnaePorData.py'], check=True)
    registrar_log("Script cnaePorData.py executado com sucesso.")
except FileNotFoundError:
    registrar_log("Erro: Script cnaePorData.py não encontrado.")
except subprocess.CalledProcessError as e:
    registrar_log(f"Erro ao executar o script cnaePorData.py: {e}")