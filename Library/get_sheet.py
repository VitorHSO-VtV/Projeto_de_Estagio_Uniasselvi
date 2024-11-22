import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from Library import group_sheet
import json

def save_sheet(sheet_name, credentials_path="./Data/credentials.json", file_name="nova_planilha_local.xlsx", tab=1, head=1):

    # Defina o escopo de acesso (Google Drive e Sheets)
    print("\033[34mDefinindo o escopo de acesso...\033[0m")  # Azul para indicar o início do processo
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Carregue as credenciais da conta de serviço
    try:
        print("\033[34mCarregando as credenciais...\033[0m")  # Amarelo para indicar carregamento
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
        client = gspread.authorize(credentials)
    except Exception as e:
        print(f"\033[31mErro ao carregar as credenciais: {e}\033[0m")  # Vermelho para erro
        return

    # Abra a planilha pelo nome
    try:
        print(f"\033[34mAbrindo a planilha {sheet_name}...\033[0m")  # Amarelo para indicar a abertura da planilha
        spreadsheet = client.open(sheet_name)
    except Exception as e:
        print(f"\033[31mErro ao abrir a planilha {sheet_name}: {e}\033[0m")  # Vermelho para erro
        return

    # Abra a primeira aba da planilha
    worksheet = spreadsheet.get_worksheet(tab)

    # Obtenha todos os dados a partir da segunda linha
    try:
        print("\033[34mObtendo dados da planilha...\033[0m")  # Amarelo para indicar a busca de dados
        data = worksheet.get_all_records(head=head)
    except Exception as e:
        print(f"\033[31mErro ao obter dados da planilha: {e}\033[0m")  # Vermelho para erro
        return

    # Converta os dados para um DataFrame do pandas
    print("\033[34mConvertendo dados para DataFrame...\033[0m")  # Azul para conversão dos dados
    df = pd.DataFrame(data)

    # Salve o DataFrame como uma planilha Excel local
    try:
        print(f"\033[34mSalvando a planilha como {file_name}...\033[0m")  # Amarelo para salvar
        df.to_excel(f"./Data/{file_name}", index=False)
        print(f"\033[32mPlanilha salva com sucesso como {file_name}\033[0m")  # Verde para sucesso
    except Exception as e:
        print(f"\033[31mErro ao salvar a planilha: {e}\033[0m")  # Vermelho para erro

def save_trucks():
    try:
        save_sheet("pasta 1 José Carlos", file_name="caminhoes.xlsx", tab=5, head=1)
        print("Caminhões salvos com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar caminhões: {e}")
        return

    # Lê as informações dos caminhões salvas
    try:
        trucks = group_sheet.sheet_to_dict("./Data/caminhoes.xlsx")
    except Exception as e:
        print(f"Erro ao carregar dados dos caminhões: {e}")
        return

    try:
        with open("./Data/caminhoes.json", 'w', encoding='utf-8') as f:
            json.dump(trucks, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Erro ao salvar o json dos caminhões: {e}")
        return