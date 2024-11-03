import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Defina o escopo de acesso (Google Drive e Sheets)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Carregue as credenciais da conta de serviço
credentials = ServiceAccountCredentials.from_json_keyfile_name("Library/credentials.json", scope)
client = gspread.authorize(credentials)

# Abra a planilha pelo nome ou ID
spreadsheet = client.open("pasta 1 José Carlos")  # Ou use .open_by_key("ID da planilha")

# Abra a primeira aba da planilha
worksheet = spreadsheet.get_worksheet(0)

# Obtenha todos os dados a partir da segunda linha
data = worksheet.get_all_records(head=2)

# Converta os dados para um DataFrame do pandas
df = pd.DataFrame(data)

# Salve o DataFrame como uma planilha Excel local
df.to_excel("./planilha_local.xlsx", index=False)
print("Planilha salva como planilha_local.xlsx")