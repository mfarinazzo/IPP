import csv
from collections import defaultdict, Counter
import os
 
folder_path = './teste'
 
# Inicializar contadores para cboes e ocupações
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
 
# Gerar arquivos CSV para ocupações (CBO2002) e Cnaes por mun
output_cbo_mun_csv = 'cboe_mun_output.csv'
 
# Função para gerar ID único para cada arquivo CSV
def gerar_id():
    count = 1
    while True:
        yield count
        count += 1
 
id_generator = gerar_id()
 
# Inicializar estruturas de dados para acumular os dados de todos os arquivos
cbo_salaries_mun = defaultdict(list)
cbo_idades_mun = defaultdict(list)
 
cbo_faixa_salaries_mun = defaultdict(lambda: defaultdict(list))
 
with os.scandir(folder_path) as entries:
    for entry in entries:
        if entry.is_file():
            print(f"Processando arquivo: {entry.name}")
            csv_file_path = os.path.join(folder_path, entry.name)
            with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
               
                if 'cbo2002ocupação' not in reader.fieldnames or 'salário' not in reader.fieldnames or 'idade' not in reader.fieldnames or 'município' not in reader.fieldnames:
                    print(f"Erro: As colunas 'cboe', 'cbo2002ocupação', 'salário', 'idade', 'região' e/ou 'uf' não foram encontradas no arquivo CSV: {entry.name}")
                else:
                    for row in reader:
                        cbo = row.get('cbo2002ocupação', '').strip()
                        municipio = row.get('município', '').strip()
                        regiao = row.get('região', '').strip()
                        uf = row.get('uf', '').strip()
                        salario_str = row.get('salário', '').strip()
                        idade_str = row.get('idade', '').strip()
                       
                        if not cbo or not salario_str or not idade_str or not regiao or not uf:
                            continue  # Pular linhas com dados faltantes essenciais
                       
                        try:
                            salario = float(salario_str.replace(',', '.'))
                            idade = int(idade_str)
                        except ValueError:
                            continue  # Pular linhas com valores inválidos para salário ou idade
                       
                        if regiao not in {'1', '2', '3', '4', '5'}:  # Filtro para regiões válidas
                            continue
                       
                        if uf not in {'12', '27', '16', '13', '29', '23', '53', '32', '52', '21', '51', '50', '31', '15', '25', '41', '26', '22', '33', '24', '43', '11', '14', '42', '35'}:
                            continue  # Filtro para UFs válidas
                       
                        faixa_etaria = determinar_faixa_etaria(idade)
                       
                        cbo_count[cbo] += 1
                       
                        cbo_salaries_mun[(cbo, municipio)].append(salario)
                        cbo_idades_mun[(cbo, municipio)].append(idade)
                       
                        cbo_faixa_salaries_mun[(cbo, municipio)][faixa_etaria].append(salario)
 
# Após processar todos os arquivos, escrever os resultados acumulados nos arquivos de saída
with open(output_cbo_mun_csv, mode='w', newline='', encoding='utf-8') as cbo_mun_file:
                 
    cbo_fieldnames = ['id', 'ocupacao', 'media_salarial_geral'] + list(faixas_etarias.keys()) + ['media_idade_geral', 'regiao', 'uf', 'municipio']
   
    cbo_mun_writer = csv.DictWriter(cbo_mun_file, fieldnames=cbo_fieldnames, delimiter=';')
 
    cbo_mun_writer.writeheader()
 
    cbo_id = 1
   
    # Calcular médias salariais e de idade para cada cboe por mun
    cbo_avg_salary_mun = {key: calcular_media(salaries) for key, salaries in cbo_salaries_mun.items()}
    cbo_avg_idade_mun = {key: calcular_media(idades) for key, idades in cbo_idades_mun.items()}
   
    # Calcular médias salariais para cada cboe por mun e faixa etária
    for (cbo, municipio), faixas in cbo_faixa_salaries_mun.items():
        row = {
            'id': cbo_id,
            'ocupacao': cbo,
            'media_salarial_geral': f'{cbo_avg_salary_mun[(cbo, municipio)]:.2f}',
            'media_idade_geral': f'{cbo_avg_idade_mun[(cbo, municipio)]:.2f}',
            'regiao': regiao,
            'uf': uf,
            'municipio': municipio
        }
        cbo_id += 1
        for faixa in faixas_etarias.keys():
            salaries = cbo_faixa_salaries_mun[(cbo, municipio)][faixa]
            avg_salary = calcular_media(salaries)
            row[faixa] = f'{avg_salary:.2f}'
        cbo_mun_writer.writerow(row)
   
   
   
print(f"\nTotal de cboes: {len(cbo_count)}")