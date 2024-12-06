# Projeto de Estágio Uniasselvi

## 📦 Importação de Dados do Google Sheets para Excel e JSON

Este projeto fornece funções para acessar planilhas do Google Sheets, extrair seus dados, salvá-los localmente em arquivos Excel e convertê-los para o formato JSON. Ele é útil para manipular e armazenar dados de forma organizada.

### 📋 Pré-requisitos

Certifique-se de ter as seguintes dependências instaladas no seu ambiente Python:
```bash
pip install gspread oauth2client pandas
```

### ⚙️ Funções
#### save_sheet
##### Descrição
A função save_sheet conecta-se a uma planilha do Google Sheets, extrai os dados de uma aba específica e salva localmente em formato Excel.

##### Parâmetros
- sheet_name (str): Nome da planilha no Google Sheets.

- credentials_path (str): Caminho para o arquivo de credenciais JSON da conta de serviço. (Padrão: ./Data/credentials.json)

- file_name (str): Nome do arquivo Excel gerado localmente. (Padrão: nova_planilha_local.xlsx)

- tab (int): Índice da aba a ser lida (começa em 0). (Padrão: 1)

- head (int): Número da linha inicial que contém os cabeçalhos dos dados. (Padrão: 1)
##### Exemplo de Uso
```bash
save_sheet("nome_da_planilha", file_name="dados.xlsx", tab=0, head=1)
```
#### save_trucks
##### Descrição
A função save_trucks salva os dados de uma aba específica da planilha pasta 1 José Carlos em dois formatos:

- Excel (caminhoes.xlsx)
- JSON (caminhoes.json)
##### Etapas
Usa a função save_sheet para criar o arquivo Excel.
Converte o Excel em um dicionário usando a função sheet_to_dict da biblioteca auxiliar group_sheet.
Salva o dicionário como JSON.
##### Exemplo de Uso
```bash
save_trucks()
```
## 📚 Funções de Agrupamento de Clientes e Endereços
Este módulo contém funções para agrupar clientes de uma planilha com base em datas de entrega, CEPs, cidades e bairros. Também inclui funcionalidades para buscar informações de endereço usando o CEP e separar clientes em categorias.

### ⚙️ Funções
#### group_customers_by_date
##### 📝 Descrição
Agrupa os clientes de uma planilha Excel com base na data de entrega.

###### 📥 Parâmetros
sheet_path (str): Caminho para o arquivo Excel contendo os dados.
##### 📤 Retorno
Um dicionário onde as chaves são datas e os valores são listas de clientes.
##### 💡 Exemplo de Uso
```bash
data = group_customers_by_date("caminhos.xlsx")
```
#### get_address_info
##### 📝 Descrição
Busca informações de endereço a partir de um CEP usando a API ViaCEP.

##### 📥 Parâmetros
cep (str): O CEP do endereço a ser pesquisado.
##### 📤 Retorno
Um dicionário contendo informações do endereço (se encontradas) ou None em caso de erro.
##### 💡 Exemplo de Uso
```bash
address = get_address_info("01001000")
```
#### group_customers_by_cep
##### 📝 Descrição
Agrupa clientes por data de entrega, cidade e bairro. Inclui informações detalhadas do endereço no agrupamento.

##### 📥 Parâmetros
dictionary (dict): Dicionário de clientes, agrupados por data de entrega.
##### 📤 Retorno
Um dicionário aninhado, organizado por datas, cidades e bairros.
##### 💡 Exemplo de Uso
```bash
grouped_data = group_customers_by_cep(client_data)
```
#### group_all
##### 📝 Descrição
Executa todas as funções de agrupamento e separa clientes em duas categorias: ESPECIAL e NORMAL.

##### 📥 Parâmetros
sheet (str): Caminho para a planilha Excel.
##### 📤 Retorno
Dois dicionários:
Clientes especiais.
Clientes normais.
##### 💡 Exemplo de Uso
```bash
special_clients, normal_clients = group_all("dados.xlsx")
```
#### sheet_to_dict
##### 📝 Descrição
Converte os dados de uma planilha Excel para um dicionário.

##### 📥 Parâmetros
file_path (str): Caminho para o arquivo Excel.
##### 📤 Retorno
Um dicionário onde cada linha da planilha é representada como um dicionário.
##### 💡 Exemplo de Uso
```bash
data_dict = sheet_to_dict("dados.xlsx")
```
#### separate_clients
##### 📝 Descrição
Separa clientes em duas categorias: ESPECIAL e NORMAL.

##### 📥 Parâmetros
data (dict): Dicionário contendo clientes agrupados.
##### 📤 Retorno
Dois dicionários:
Clientes especiais.
Clientes normais.
##### 💡 Exemplo de Uso
```bash
special_clients, normal_clients = separate_clients(client_data)
```
#### build_complete_address
##### 📝 Descrição
Cria uma string de endereço formatada com base nas informações fornecidas.

##### 📥 Parâmetros
address_info (dict): Dicionário com informações do endereço, como logradouro, bairro, cidade, etc.
##### 📤 Retorno
Uma string representando o endereço completo.
##### 💡 Exemplo de Uso
```bash
address = build_complete_address({
    "logradouro": "Rua Exemplo",
    "bairro": "Centro",
    "localidade": "São Paulo",
    "uf": "SP",
    "cep": "01001000",
    "numero_casa": "123"
})
```
## 🚛 Funções de Exportação e Geração de Roteiros

As funções a seguir permitem processar, organizar e exportar dados relacionados à logística de entregas. Abaixo estão as descrições e funcionalidades de cada uma:

### 📋 Carregar Dados de Caminhões
```bash
def load_truck_data(filename='./Data/caminhões.json')
```
- Descrição: Carrega informações de caminhões a partir de um arquivo JSON e retorna um dicionário com os tamanhos e volumes disponíveis.
- Parâmetros:
  - filename (str): Caminho para o arquivo JSON. Padrão: ./Data/caminhões.json.
### 🖨️ Gerar PDF de Roteiros
```bash
def create_pdf(routes, truck_number, truck_size, output_file='roteiro_entregas.pdf')
```
- Descrição: Cria um PDF contendo os roteiros de entregas com base nos dados fornecidos.
- Parâmetros:
  - routes (dict): Dados das rotas organizados por data.
  - truck_number (int): Número do caminhão.
  - truck_size (dict): Dicionário com os tamanhos dos caminhões.
  - output_file (str): Nome do arquivo PDF gerado. Padrão: roteiro_entregas.pdf.
### 📊 Gerar Planilha Excel
```bash
def create_xlsx(routes, output_file='roteiro_entregas.xlsx')
```
- Descrição: Gera uma planilha Excel com as informações de entrega formatadas.
- Parâmetros:
  - routes (dict): Dados das rotas organizados por data.
  - output_file (str): Nome do arquivo Excel gerado. Padrão: roteiro_entregas.xlsx.
### 🔗 Criar Link de Rota no Google Maps
```bash
def create_links_txt(deliveries_json, output_file="route_link.txt")
```
- Descrição: Gera um link do Google Maps com as rotas de entrega baseadas nos endereços fornecidos e salva em um arquivo texto.
- Parâmetros:
  - deliveries_json (dict): Dados das entregas organizados por data e turnos.
  - output_file (str): Nome do arquivo de texto gerado. Padrão: route_link.txt.
### 🧰 Exemplo de Uso
```bash
# Carregar dados de caminhões
truck_data = load_truck_data()

# Gerar PDF com as rotas
create_pdf(routes, truck_number=1, truck_size=truck_data)

# Gerar planilha Excel
create_xlsx(routes)

# Criar link de rota no Google Maps
create_links_txt(routes)
```