import csv
from collections import defaultdict, Counter
import os
import subprocess

output_directory = 'output_caged'
folder_path = './CAGEDMOV_downloads'

os.makedirs(output_directory, exist_ok=True)

log_file = 'log_CAGEDERRORS.txt'

def registrar_log(mensagem):
    with open(log_file, 'a') as f:
        f.write(mensagem + '\n')

# Inicializar contadores para cnaes e ocupações
cnae_count = Counter()

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

# Função para gerar ID único para cada arquivo CSV
def gerar_id():
    count = 1
    while True:
        yield count
        count += 1

id_generator = gerar_id()

# Inicializar estruturas de dados para acumular os dados de todos os arquivos
cnae_salaries_mun_date = defaultdict(list)
cnae_idades_mun_date = defaultdict(list)
cnae_faixa_salaries_mun_date = defaultdict(lambda: defaultdict(list))

with os.scandir(folder_path) as entries:
    for entry in entries:
        if entry.is_file():
            print(f"Processando arquivo: {entry.name}")
            data = extrair_data(entry.name)
            csv_file_path = os.path.join(folder_path, entry.name)
            with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                
                if 'subclasse' not in reader.fieldnames or 'salário' not in reader.fieldnames or 'idade' not in reader.fieldnames or 'município' not in reader.fieldnames:
                    print(f"Erro: As colunas 'subclasse', 'salário', 'idade', 'município' não foram encontradas no arquivo CSV: {entry.name}")
                else:
                    for row in reader:
                        cnae = row.get('subclasse', '').strip()
                        municipio = row.get('município', '').strip()
                        regiao = row.get('região', '').strip()
                        uf = row.get('uf', '').strip()
                        salario_str = row.get('salário', '').strip()
                        idade_str = row.get('idade', '').strip()
                        unidade_salario_codigo = row.get('unidadesaláriocódigo', '').strip()
                        horas_contratuais_str = row.get('horascontratuais', '').strip()
                        
                        if not cnae or not salario_str or not idade_str or not municipio or not uf or not regiao:
                            continue  # Pular linhas com dados faltantes essenciais
                        
                        try:
                            salario_float = float(salario_str.replace(',', '.'))
                            idade = int(idade_str)
                        except ValueError:
                            continue  # Pular linhas com valores inválidos para salário ou idade
                        
                        # Aplicando a lógica para transformar tudo para salário mensal
                        if unidade_salario_codigo in ['99', '6', '7']:
                            continue  # Desconsiderar esses casos
                        elif unidade_salario_codigo == '5':  # Mês
                            if salario_float < 1000 or salario_float > 25000:
                                continue
                            else:
                                salario = salario_float
                        elif unidade_salario_codigo == '1':  # Hora
                            if horas_contratuais_str == '':
                                continue
                            elif int(float(horas_contratuais_str.replace(',','.'))) < 20:
                                continue
                            else:
                                horas = int(float(horas_contratuais_str.replace(',', '.')))
                                salario_hora = salario_float * (horas * 4.33)
                                if salario_hora < 1000 or salario_hora > 25000:
                                    continue
                                else:
                                    salario = salario_hora
                        elif unidade_salario_codigo == '3':  # Semana
                            salario_semanal = salario_float * 4.33
                            if salario_semanal < 1000 or salario_semanal > 25000:
                                continue
                            else:
                                salario = salario_semanal
                        elif unidade_salario_codigo == '4':  # Quinzena
                            salario_quinzenal = salario_float * 2
                            if salario_quinzenal < 1000 or salario_quinzenal > 25000:
                                continue
                            else:
                                salario = salario_quinzenal
                        
                        if regiao not in {'1', '2', '3', '4', '5'}:  # Filtro para regiões válidas
                            continue
                        
                        if uf not in {'12', '27', '16', '13', '29', '23', '53', '32', '52', '21', '51', '50', '31', '15', '25', '41', '26', '22', '33', '24', '43', '11', '14', '42', '35'}:
                            continue  # Filtro para UFs válidas
                        
                        faixa_etaria = determinar_faixa_etaria(idade)
                        
                        cnae_count[cnae] += 1
                        
                        cnae_salaries_mun_date[(cnae, municipio, data)].append(salario)
                        cnae_idades_mun_date[(cnae, municipio, data)].append(idade)
                        
                        cnae_faixa_salaries_mun_date[(cnae, municipio, data)][faixa_etaria].append(salario)

# Após processar todos os arquivos, escrever os resultados acumulados nos arquivos de saída
output_cnae_mun_csv = f'./{output_directory}/cnae_mun_output.csv'
with open(output_cnae_mun_csv, mode='w', newline='', encoding='utf-8') as cnae_mun_file:
    cnae_fieldnames = ['id', 'subclasse', 'media_salarial_geral'] + list(faixas_etarias.keys()) + ['media_idade_geral', 'regiao', 'uf', 'municipio', 'data']
    
    cnae_mun_writer = csv.DictWriter(cnae_mun_file, fieldnames=cnae_fieldnames, delimiter=';')
    
    cnae_mun_writer.writeheader()
    
    cnae_id = 1
    
    # Calcular médias salariais e de idade para cada cnae por mun e data
    cnae_avg_salary_mun_date = {key: calcular_media(salaries) for key, salaries in cnae_salaries_mun_date.items()}
    cnae_avg_idade_mun_date = {key: calcular_media(idades) for key, idades in cnae_idades_mun_date.items()}
    
    # Calcular médias salariais para cada cnae por mun, data e faixa etária
    for (cnae, municipio, data), faixas in cnae_faixa_salaries_mun_date.items():
        row = {
            'id': cnae_id,
            'subclasse': cnae,
            'media_salarial_geral': f'{cnae_avg_salary_mun_date[(cnae, municipio, data)]:.2f}',
            'media_idade_geral': f'{cnae_avg_idade_mun_date[(cnae, municipio, data)]:.2f}',
            'regiao': regiao,
            'uf': uf,
            'municipio': municipio,
            'data': data
        }
        cnae_id += 1
        for faixa in faixas_etarias.keys():
            salaries = cnae_faixa_salaries_mun_date[(cnae, municipio, data)][faixa]
            avg_salary = calcular_media(salaries)
            row[faixa] = f'{avg_salary:.2f}'
        cnae_mun_writer.writerow(row)

print(f"\nTotal de cnaes: {len(cnae_count)}")

# Tentar chamar o script ajustaCaged.py
try:
    subprocess.run(['python', 'ajustaCaged.py'], check=True)
    registrar_log("Script ajustaCaged.py executado com sucesso.")
except FileNotFoundError:
    registrar_log("Erro: Script ajustaCaged.py não encontrado.")
except subprocess.CalledProcessError as e:
    registrar_log(f"Erro ao executar o script ajustaCaged.py: {e}")