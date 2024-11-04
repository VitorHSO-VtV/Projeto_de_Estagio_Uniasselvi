import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

def save_sheet(sheet_name, credentials_path="./Data/credentials.json", file_name="planilha_local.xlsx"):

    # Defina o escopo de acesso (Google Drive e Sheets)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Carregue as credenciais da conta de serviço
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    client = gspread.authorize(credentials)

    # Abra a planilha pelo nome
    spreadsheet = client.open(sheet_name)

    # Abra a primeira aba da planilha
    worksheet = spreadsheet.get_worksheet(0)

    # Obtenha todos os dados a partir da segunda linha
    data = worksheet.get_all_records(head=2)

    # Converta os dados para um DataFrame do pandas
    df = pd.DataFrame(data)

    # Salve o DataFrame como uma planilha Excel local
    df.to_excel(f"./Data/{file_name}", index=False)
    print(f"Planilha salva como {file_name}")