from Library import get_sheet, group_sheet, make_route
import json

get_sheet.save_sheet("pasta 1 José Carlos")

grouped_sheet = group_sheet.group_all("Data/planilha_local.xlsx")

with open("file.json", "w") as file:
    json.dump(grouped_sheet, file, indent=4)  # `indent=4` organiza o JSON para melhor legibilidade