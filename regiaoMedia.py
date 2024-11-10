import csv
from collections import defaultdict, Counter
import os
 
folder_path = './teste'
 
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
 
# Gerar arquivos CSV para ocupações (CBO2002) e Cnaes por UF e por Região
output_subclass_uf_csv = 'subclasse_uf_output.csv'
output_subclass_regiao_csv = 'subclasse_regiao_output.csv'
output_cbo_uf_csv = 'ocupacoes_uf_output.csv'
output_cbo_regiao_csv = 'ocupacoes_regiao_output.csv'
 
# Função para gerar ID único para cada arquivo CSV
def gerar_id():
    count = 1
    while True:
        yield count
        count += 1
 
id_generator = gerar_id()
 
# Inicializar estruturas de dados para acumular os dados de todos os arquivos
subclass_salaries_uf = defaultdict(list)
subclass_idades_uf = defaultdict(list)
cbo_salaries_uf = defaultdict(list)
cbo_idades_uf = defaultdict(list)
 
subclass_salaries_regiao = defaultdict(list)
subclass_idades_regiao = defaultdict(list)
cbo_salaries_regiao = defaultdict(list)
cbo_idades_regiao = defaultdict(list)
 
subclass_faixa_salaries_uf = defaultdict(lambda: defaultdict(list))
cbo_faixa_salaries_uf = defaultdict(lambda: defaultdict(list))
subclass_faixa_salaries_regiao = defaultdict(lambda: defaultdict(list))
cbo_faixa_salaries_regiao = defaultdict(lambda: defaultdict(list))
 
with os.scandir(folder_path) as entries:
    for entry in entries:
        if entry.is_file():
            print(f"Processando arquivo: {entry.name}")
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
                       
                        if regiao not in {'1', '2', '3', '4', '5'}:  # Filtro para regiões válidas
                            continue
                       
                        if uf not in {'12', '27', '16', '13', '29', '23', '53', '32', '52', '21', '51', '50', '31', '15', '25', '41', '26', '22', '33', '24', '43', '11', '14', '42', '35'}:
                            continue  # Filtro para UFs válidas
                       
                        faixa_etaria = determinar_faixa_etaria(idade)
                       
                        subclass_count[subclass] += 1
                        cbo_count[cbo] += 1
                       
                        subclass_salaries_uf[(subclass, uf)].append(salario)
                        subclass_idades_uf[(subclass, uf)].append(idade)
                        cbo_salaries_uf[(cbo, uf)].append(salario)
                        cbo_idades_uf[(cbo, uf)].append(idade)
                       
                        subclass_salaries_regiao[(subclass, regiao)].append(salario)
                        subclass_idades_regiao[(subclass, regiao)].append(idade)
                        cbo_salaries_regiao[(cbo, regiao)].append(salario)
                        cbo_idades_regiao[(cbo, regiao)].append(idade)
                       
                        subclass_faixa_salaries_uf[(subclass, uf)][faixa_etaria].append(salario)
                        cbo_faixa_salaries_uf[(cbo, uf)][faixa_etaria].append(salario)
                        subclass_faixa_salaries_regiao[(subclass, regiao)][faixa_etaria].append(salario)
                        cbo_faixa_salaries_regiao[(cbo, regiao)][faixa_etaria].append(salario)
 
# Após processar todos os arquivos, escrever os resultados acumulados nos arquivos de saída
with open(output_subclass_uf_csv, mode='w', newline='', encoding='utf-8') as subclass_uf_file, \
     open(output_subclass_regiao_csv, mode='w', newline='', encoding='utf-8') as subclass_regiao_file, \
     open(output_cbo_uf_csv, mode='w', newline='', encoding='utf-8') as cbo_uf_file, \
     open(output_cbo_regiao_csv, mode='w', newline='', encoding='utf-8') as cbo_regiao_file:
         
    subclass_fieldnames = ['id', 'cnae', 'media_salarial_geral'] + list(faixas_etarias.keys()) + ['media_idade_geral', 'regiao', 'uf']
    cbo_fieldnames = ['id', 'ocupacao', 'media_salarial_geral'] + list(faixas_etarias.keys()) + ['media_idade_geral', 'regiao', 'uf']
   
    subclass_uf_writer = csv.DictWriter(subclass_uf_file, fieldnames=subclass_fieldnames, delimiter=';')
    subclass_regiao_writer = csv.DictWriter(subclass_regiao_file, fieldnames=subclass_fieldnames, delimiter=';')
    cbo_uf_writer = csv.DictWriter(cbo_uf_file, fieldnames=cbo_fieldnames, delimiter=';')
    cbo_regiao_writer = csv.DictWriter(cbo_regiao_file, fieldnames=cbo_fieldnames, delimiter=';')
 
    subclass_uf_writer.writeheader()
    subclass_regiao_writer.writeheader()
    cbo_uf_writer.writeheader()
    cbo_regiao_writer.writeheader()
 
    subclass_id = 1
    cbo_id = 1
   
    # Calcular médias salariais e de idade para cada subclasse por UF
    subclass_avg_salary_uf = {key: calcular_media(salaries) for key, salaries in subclass_salaries_uf.items()}
    subclass_avg_idade_uf = {key: calcular_media(idades) for key, idades in subclass_idades_uf.items()}
   
    # Calcular médias salariais para cada subclasse por UF e faixa etária
    for (subclass, uf), faixas in subclass_faixa_salaries_uf.items():
        row = {
            'id': subclass_id,
            'cnae': subclass,
            'media_salarial_geral': f'{subclass_avg_salary_uf[(subclass, uf)]:.2f}',
            'media_idade_geral': f'{subclass_avg_idade_uf[(subclass, uf)]:.2f}',
            'regiao': '',
            'uf': uf
        }
        subclass_id += 1
        for faixa in faixas_etarias.keys():
            salaries = subclass_faixa_salaries_uf[(subclass, uf)][faixa]
            avg_salary = calcular_media(salaries)
            row[faixa] = f'{avg_salary:.2f}'
        subclass_uf_writer.writerow(row)
   
    # Calcular médias salariais e de idade para cada subclasse por Região
    subclass_avg_salary_regiao = {key: calcular_media(salaries) for key, salaries in subclass_salaries_regiao.items()}
    subclass_avg_idade_regiao = {key: calcular_media(idades) for key, idades in subclass_idades_regiao.items()}
   
    # Calcular médias salariais para cada subclasse por Região e faixa etária
    for (subclass, regiao), faixas in subclass_faixa_salaries_regiao.items():
        row = {
            'id': subclass_id,
            'cnae': subclass,
            'media_salarial_geral': f'{subclass_avg_salary_regiao[(subclass, regiao)]:.2f}',
            'media_idade_geral': f'{subclass_avg_idade_regiao[(subclass, regiao)]:.2f}',
            'regiao': regiao,
            'uf': ''
        }
        subclass_id += 1
        for faixa in faixas_etarias.keys():
            salaries = subclass_faixa_salaries_regiao[(subclass, regiao)][faixa]
            avg_salary = calcular_media(salaries)
            row[faixa] = f'{avg_salary:.2f}'
        subclass_regiao_writer.writerow(row)
   
    # Calcular médias salariais e de idade para cada ocupação (cbo2002ocupacao) por UF
    cbo_avg_salary_uf = {key: calcular_media(salaries) for key, salaries in cbo_salaries_uf.items()}
    cbo_avg_idade_uf = {key: calcular_media(idades) for key, idades in cbo_idades_uf.items()}
   
    # Calcular médias salariais para cada ocupação por UF e faixa etária
    for (cbo, uf), faixas in cbo_faixa_salaries_uf.items():
        row = {
            'id': cbo_id,
            'ocupacao': cbo,
            'media_salarial_geral': f'{cbo_avg_salary_uf[(cbo, uf)]:.2f}',
            'media_idade_geral': f'{cbo_avg_idade_uf[(cbo, uf)]:.2f}',
            'regiao': '',
            'uf': uf
        }
        cbo_id += 1
        for faixa in faixas_etarias.keys():
            salaries = cbo_faixa_salaries_uf[(cbo, uf)][faixa]
            avg_salary = calcular_media(salaries)
            row[faixa] = f'{avg_salary:.2f}'
        cbo_uf_writer.writerow(row)
   
    # Calcular médias salariais e de idade para cada ocupação (cbo2002ocupacao) por Região
    cbo_avg_salary_regiao = {key: calcular_media(salaries) for key, salaries in cbo_salaries_regiao.items()}
    cbo_avg_idade_regiao = {key: calcular_media(idades) for key, idades in cbo_idades_regiao.items()}
   
    # Calcular médias salariais para cada ocupação por Região e faixa etária
    for (cbo, regiao), faixas in cbo_faixa_salaries_regiao.items():
        row = {
            'id': cbo_id,
            'ocupacao': cbo,
            'media_salarial_geral': f'{cbo_avg_salary_regiao[(cbo, regiao)]:.2f}',
            'media_idade_geral': f'{cbo_avg_idade_regiao[(cbo, regiao)]:.2f}',
            'regiao': regiao,
            'uf': ''
        }
        cbo_id += 1
        for faixa in faixas_etarias.keys():
            salaries = cbo_faixa_salaries_regiao[(cbo, regiao)][faixa]
            avg_salary = calcular_media(salaries)
            row[faixa] = f'{avg_salary:.2f}'
        cbo_regiao_writer.writerow(row)
 
print(f"\nTotal de Subclasses: {len(subclass_count)}")
print(f"Total de Ocupações (CBO2002): {len(cbo_count)}")