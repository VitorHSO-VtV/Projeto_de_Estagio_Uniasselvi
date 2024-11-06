from Library import get_sheet, group_sheet, make_route, export_pdf
import json

get_sheet.save_sheet("pasta 1 José Carlos")

grouped_sheet = group_sheet.group_all("Data/planilha_local.xlsx")

with open("Data/file.json", "w") as file:
    json.dump(grouped_sheet, file, indent=4)  # `indent=4` organiza o JSON para melhor legibilidade

route = make_route.make_best_routes(grouped_sheet, "Rua Orlando Odilio Koerich, SN Galpão II - Picadas do Sul, São José - SC, 88102-106")

with open("Data/file2.json", "w") as file:
    json.dump(route, file, indent=4)  # `indent=4` organiza o JSON para melhor legibilidade

export_pdf.create_pdfs(route)