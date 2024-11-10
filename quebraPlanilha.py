import pandas as pd
import os

def split_excel_file(file_path, output_dir, chunk_size=100 * 1024 * 1024):
    # Criar diretório de saída se não existir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Ler o arquivo original em pedaços
    chunk_iter = pd.read_csv(file_path, chunksize=1000000)  # Ajuste o chunksize conforme necessário
    file_index = 0
    current_chunk = pd.DataFrame()
    
    for chunk in chunk_iter:
        current_chunk = pd.concat([current_chunk, chunk])
        current_file_path = os.path.join(output_dir, f'part_{file_index}.csv')
        
        # Salvar o pedaço atual em um arquivo temporário
        current_chunk.to_csv(current_file_path, index=False)
        
        # Verificar o tamanho do arquivo
        if os.path.getsize(current_file_path) >= chunk_size:
            file_index += 1
            current_chunk = pd.DataFrame()  # Resetar o DataFrame para o próximo arquivo
    
    # Salvar o último pedaço se houver dados restantes
    if not current_chunk.empty:
        current_file_path = os.path.join(output_dir, f'part_{file_index}.csv')
        current_chunk.to_csv(current_file_path, index=False)

# Exemplo de uso
file_path = './arruma/cnae_mun.csv'
output_dir = './arruma'
split_excel_file(file_path, output_dir)