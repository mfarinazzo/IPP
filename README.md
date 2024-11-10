# Automação Fornecedores

Com esses códigos, apenas com simples manutenções, conseguimos automatizar quase toda a busca de dados para o módulo de fornecedores do Price Index.

## Índice

- [Sobre](#sobre)
- [Demonstração](#demonstração)
- [Instalação](#instalação)
- [Uso](#uso)
- [Explicação dos Arquivos](#explicação-dos-arquivos)

## Sobre

O projeto é todo feito em Python (com a inserção em PHP) e todos os códigos estão comentados ponto a ponto. Para localizar os pontos de destino dos resultados desses códigos, basta entrar no banco da **PlataformaTour**, ir para o banco principal do PI e procurar por `PI_fornecedores` (todas as tabelas seguem este modelo de estrutura).

Este projeto é uma cadeia de código, ele **não funcionará** se estiver faltando algum dos elementos. Os códigos são:

- ajustaCaged.py
- buscaCaged.py
- cboMunData.py
- cnaeMunData.py
- cnaePorData.py
- converterCSV.py
- enviaPHP.py
- regiaoData.py
- anos_meses_registrados.txt (Opcional)

No servidor (se alterar o caminho das APIs, você deve mudar os links no código `enviaPHP.py`):

- insere.php
- insereregiao.php
- inseremun.php

O arquivo opcional é um log dos últimos dados do seu banco e deve seguir um padrão como este: <br>
2022 - 01,02,03,04,05,06,07,08,09,10,11,12 <br>
2023 - 01,02,03,04,05,06,07,08,09,10,11,12 <br>
2024 - 01,02,03,04

O código atualizará sempre com base neste arquivo. Se ele não existir, o robô assumirá que não há nenhum dado no banco e configurará todos os valores do zero (as tabelas já devem estar criadas no banco).

Os arquivos com "média" em seu nome servem para gerar outros tipos de dados. Eles gerarão um conteúdo geral em relação aos dados, e isso deve ser ponderado de quanto em quanto tempo deve ser utilizado.

Os resultados deste robô serão uma atualização mensal do banco com as métricas recebidas pelo governo.

Se o FTP do governo (pode ser aberto no explorador de arquivos em: `ftp://ftp.mtps.gov.br/pdet/microdados/NOVO%20CAGED/`) cair, o código não encontrará nada e encerrará.

Esses códigos geram logs de erros para facilitar a manutenção, portanto, fique atento.

## Demonstração

O arquivo `busCaged.py` é o pai da cadeia e deve ser executado no cron job da aplicação. Todos os códigos devem estar na mesma pasta, exceto as APIs. Apenas um simples comando `python buscaCaged.py` é suficiente para iniciar esta cadeia.

## Instalação

Para rodar os códigos Python, devemos instalar as bibliotecas `ftplib` e `py7zr`. Apenas usando o pip é o suficiente:

bash
pip install ftplib py7zr

## Uso

Para iniciar a execução da cadeia de scripts, basta executar o arquivo buscaCaged.py:

python buscaCaged.py

## Demonstração

O arquivo busCaged.py é o pai da cadeia, deve ser executado no cron job da aplicação.
(todos os códigos devem estar na mesma pasta, exceto das APIs)
apenas um simples python buscaCaged.py serve para iniciar esta cadeia.

# Explicação dos Arquivos

Uma explicação básica de cada arquivo (em ordem de execução):

| Arquivo             | Descrição                           |
|---------------------|-------------------------------------|
| buscaCaged.py       | Este arquivo irá procurar os dados em anos_meses_registrados.txt, identificar quais dados faltam em relação ao FTP do governo e baixá-los (em várias tentativas se houver erro de execução), criando uma pasta para que esses arquivos sejam recebidos (CAGEDMOV_DOWNLOAD). Este código só baixa os arquivos de movimentação do CAGED. |
| converterCSV.py     | Ele irá entrar na pasta dos downloads e extrair e renomear os arquivos baixados para um formato mais aceitável. |
| cnaePorData.py      | Este arquivo irá gerar as métricas básicas (sem filtragem) dos CNAEs e CBOs.|
| regiaoData.py       | Este arquivo irá gerar as métricas com filtragem por região e UF (CNAEs e CBOs).|
| cnaeMunData.py      | Este arquivo irá gerar as métricas filtradas por data (Apenas CNAEs).|
| cboMunData.py       | Este arquivo irá gerar as métricas filtradas por data (Apenas CBOs).|
| ajustaCaged.py      | Este arquivo irá realizar um ajuste nas métricas para deixá-las mais padronizadas para subir ao banco. |
| enviaPHP.py         | Este arquivo irá enviar as métricas resultantes para as APIs inserirem no servidor.|
| APIs PHP         | 	Esses arquivos apenas inserem os dados no servidor.|
