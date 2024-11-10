import csv
from collections import defaultdict, Counter
import os
import datetime
import subprocess

output_directory = 'output_caged'
folder_path = './CAGEDMOV_downloads'

os.makedirs(output_directory, exist_ok=True)

log_file = 'log_CAGEDERRORS.txt'

def registrar_log(mensagem):
    with open(log_file, 'a') as f:
        f.write(mensagem + '\n')

# Inicializar contadores para subclasses e ocupações
subclass_count = Counter()
cbo_count = Counter()

# Faixas etárias
faixas_etarias = {
    '18-29': (18, 29),
    '30-39': (30, 39),
    '40-49': (40, 49),
    '50-59': (50, 59),
    '60+': (60, 200)  # 200 é um valor arbitrário para representar 60+
}

# Função para calcular média
def calcular_media(valores):
    if valores:
        return sum(valores) / len(valores)
    else:
        return 0.0

# Função para determinar a faixa etária
def determinar_faixa_etaria(idade):
    for faixa, (min_idade, max_idade) in faixas_etarias.items():
        if min_idade <= idade <= max_idade:
            return faixa
    return None

# Função para extrair data do nome do arquivo e formatar
def extrair_data(input_str):
    if len(input_str) < 6:
        return "A string deve ter pelo menos 6 caracteres."
    last_six = input_str[-10:]
    year = last_six[:4]
    month = last_six[4:-4]
    formatted_date = f"{year}-{month}-01"
   
    return formatted_date

# Gerar arquivos CSV para cnae - uf, cnae - regiao, cbo - uf, cbo - regiao
output_cnae_uf_csv = f'./{output_directory}/cnae_uf_output.csv'
output_cnae_regiao_csv = f'./{output_directory}/cnae_regiao_output.csv'
output_cbo_uf_csv = f'./{output_directory}/cbo_uf_output.csv'
output_cbo_regiao_csv = f'./{output_directory}/cbo_regiao_output.csv'

with open(output_cnae_uf_csv, mode='w', newline='', encoding='utf-8') as cnae_uf_file, \
     open(output_cnae_regiao_csv, mode='w', newline='', encoding='utf-8') as cnae_regiao_file, \
     open(output_cbo_uf_csv, mode='w', newline='', encoding='utf-8') as cbo_uf_file, \
     open(output_cbo_regiao_csv, mode='w', newline='', encoding='utf-8') as cbo_regiao_file:
         
    fieldnames = ['id', 'codigo', 'media_salarial_geral'] + list(faixas_etarias.keys()) + ['media_idade_geral', 'regiao', 'uf', 'data']
   
    cnae_uf_writer = csv.DictWriter(cnae_uf_file, fieldnames=fieldnames, delimiter=';')
    cnae_regiao_writer = csv.DictWriter(cnae_regiao_file, fieldnames=fieldnames, delimiter=';')
    cbo_uf_writer = csv.DictWriter(cbo_uf_file, fieldnames=fieldnames, delimiter=';')
    cbo_regiao_writer = csv.DictWriter(cbo_regiao_file, fieldnames=fieldnames, delimiter=';')

    cnae_uf_writer.writeheader()
    cnae_regiao_writer.writeheader()
    cbo_uf_writer.writeheader()
    cbo_regiao_writer.writeheader()
   
    cnae_uf_id = 1
    cnae_regiao_id = 1
    cbo_uf_id = 1
    cbo_regiao_id = 1
   
    with os.scandir(folder_path) as entries:
        for entry in entries:
            if entry.is_file():
                # Reiniciar as estruturas de dados para acumular dados do novo arquivo
                cnae_uf_data = defaultdict(lambda: defaultdict(list))
                cnae_regiao_data = defaultdict(lambda: defaultdict(list))
                cbo_uf_data = defaultdict(lambda: defaultdict(list))
                cbo_regiao_data = defaultdict(lambda: defaultdict(list))

                data = extrair_data(entry.name)
                csv_file_path = os.path.join(folder_path, entry.name)
                with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile, delimiter=';')
                   
                    if 'subclasse' not in reader.fieldnames or 'cbo2002ocupação' not in reader.fieldnames or 'salário' not in reader.fieldnames or 'idade' not in reader.fieldnames or 'região' not in reader.fieldnames or 'uf' not in reader.fieldnames:
                        print(f"Erro: As colunas 'subclasse', 'cbo2002ocupação', 'salário', 'idade', 'região' e/ou 'uf' não foram encontradas no arquivo CSV: {entry.name}")
                    else:
                        for row in reader:
                            subclass = row.get('subclasse', '').strip()
                            cbo = row.get('cbo2002ocupação', '').strip()
                            regiao = row.get('região', '').strip()
                            uf = row.get('uf', '').strip()
                            salario_str = row.get('salário', '').strip()
                            idade_str = row.get('idade', '').strip()
                           
                            if not subclass or not cbo or not salario_str or not idade_str or not regiao or not uf:
                                continue  # Pular linhas com dados faltantes essenciais
                           
                            try:
                                salario = float(salario_str.replace(',', '.'))
                                idade = int(idade_str)
                            except ValueError:
                                continue  # Pular linhas com valores inválidos para salário ou idade
                           
                            faixa_etaria = determinar_faixa_etaria(idade)
                           
                            subclass_count[subclass] += 1
                            cbo_count[cbo] += 1
                           
                            cnae_uf_data[(subclass, uf, data)]["salarios"].append(salario)
                            cnae_uf_data[(subclass, uf, data)]["idades"].append(idade)
                            cnae_uf_data[(subclass, uf, data)][faixa_etaria].append(salario)

                            cnae_regiao_data[(subclass, regiao, data)]["salarios"].append(salario)
                            cnae_regiao_data[(subclass, regiao, data)]["idades"].append(idade)
                            cnae_regiao_data[(subclass, regiao, data)][faixa_etaria].append(salario)

                            cbo_uf_data[(cbo, uf, data)]["salarios"].append(salario)
                            cbo_uf_data[(cbo, uf, data)]["idades"].append(idade)
                            cbo_uf_data[(cbo, uf, data)][faixa_etaria].append(salario)

                            cbo_regiao_data[(cbo, regiao, data)]["salarios"].append(salario)
                            cbo_regiao_data[(cbo, regiao, data)]["idades"].append(idade)
                            cbo_regiao_data[(cbo, regiao, data)][faixa_etaria].append(salario)

                # Função para escrever dados no arquivo CSV
                def escrever_dados(writer, data_dict, id_counter, tipo):
                    for key, faixas in data_dict.items():
                        row = {
                            'id': id_counter,
                            'codigo': key[0],
                            'media_salarial_geral': f'{calcular_media(faixas["salarios"]):.2f}',
                            'media_idade_geral': f'{calcular_media(faixas["idades"]):.2f}',
                            'regiao': key[1] if tipo == 'regiao' else '',
                            'uf': key[1] if tipo == 'uf' else '',
                            'data': key[2]
                        }
                        id_counter += 1
                        for faixa in faixas_etarias.keys():
                            salaries = faixas[faixa]
                            avg_salary = calcular_media(salaries)
                            row[faixa] = f'{avg_salary:.2f}'
                        writer.writerow(row)
                    return id_counter

                # Escrever dados nos arquivos CSV
                cnae_uf_id = escrever_dados(cnae_uf_writer, cnae_uf_data, cnae_uf_id, 'uf')
                cnae_regiao_id = escrever_dados(cnae_regiao_writer, cnae_regiao_data, cnae_regiao_id, 'regiao')
                cbo_uf_id = escrever_dados(cbo_uf_writer, cbo_uf_data, cbo_uf_id, 'uf')
                cbo_regiao_id = escrever_dados(cbo_regiao_writer, cbo_regiao_data, cbo_regiao_id, 'regiao')

print(f'Arquivos CSV gerados com sucesso: {output_cnae_uf_csv}, {output_cnae_regiao_csv}, {output_cbo_uf_csv}, {output_cbo_regiao_csv}')

total_subclasses = len(subclass_count)
total_ocupacoes = len(cbo_count)
print(f"\nTotal de Subclasses: {total_subclasses}")
print(f"Total de Ocupações (CBO2002): {total_ocupacoes}")

# Tentar chamar o script cboMunData.py
try:
    subprocess.run(['python', 'cboMunData.py'], check=True)
    registrar_log("Script cboMunData.py executado com sucesso.")
except FileNotFoundError:
    registrar_log("Erro: Script cboMunData.py não encontrado.")
except subprocess.CalledProcessError as e:
    registrar_log(f"Erro ao executar o script cboMunData.py: {e}")