from Library import get_sheet, group_sheet, make_route, export
import pandas as pd
import json
import os

quantidade_de_caminhões = 3

# Salva a planilha com o nome "pasta 1 José Carlos"
print("Salvando a planilha...")
get_sheet.save_sheet("pasta 1 José Carlos", tab=2, head=2, )
print("Planilha salva com sucesso!")

get_sheet.save_trucks()

# Caminho dos arquivos
arquivo_existente = 'Data/planilha_local.xlsx'
arquivo_novo = 'Data/nova_planilha_local.xlsx'

# Verificar se o arquivo existe
if not os.path.exists(arquivo_existente):
    # Criar uma planilha vazia se o arquivo não existir
    print(f"Arquivo {arquivo_existente} não encontrado. Criando um arquivo vazio...")
    df_existente = pd.DataFrame()  # Cria um DataFrame vazio
    df_existente.to_excel(arquivo_existente, index=False)  # Salva o DataFrame vazio no arquivo
else:
    # Ler o arquivo existente
    try:
        df_existente = pd.read_excel(arquivo_existente)
    except ValueError:
        print(f"Erro ao ler {arquivo_existente}. Tentando criar uma planilha vazia...")
        df_existente = pd.DataFrame()
        df_existente.to_excel(arquivo_existente, index=False)

# Ler o novo arquivo
df_novo = pd.read_excel(arquivo_novo)

with open("Data/caminhoes.json", "r") as file:
    trucks_data = json.load(file)

# Verificar se os arquivos são iguais
if not df_existente.equals(df_novo):
    # Substituir o conteúdo do arquivo existente pelo novo
    df_novo.to_excel(arquivo_existente, index=False)
    print("Os dados eram diferentes. O arquivo existente foi atualizado com o conteúdo do novo arquivo.")
    
    # Agrupa os dados da planilha e transforma em um dicionário
    print("Agrupando dados da planilha...")
    special_clients, client_not_served = group_sheet.group_all("Data/planilha_local.xlsx")
    print("Dados agrupados com sucesso!")

    # Salva os dados agrupados em um arquivo JSON chamado 'planilha_agrupada.json'
    print("Salvando os dados agrupados em JSON...")
    with open("Data/planilha_de_clientes_especiais_agrupada.json", "w") as file:
        json.dump(special_clients, file, indent=4)  # `indent=4` organiza o JSON para melhor legibilidade
    with open("Data/planilha_agrupada.json", "w") as file:
        json.dump(client_not_served, file, indent=4)  # `indent=4` organiza o JSON para melhor legibilidade
    print("Dados agrupados salvos com sucesso em 'planilha_agrupada.json'.")

    route = {}  # Rota vazia para iniciar

    # Iterar sobre a quantidade de caminhões
    for truck_number in range(1, quantidade_de_caminhões + 1):
        print(f"\nCriando o roteiro de entregas para o caminhão {truck_number}...")

        # Procurar o caminhão correspondente nos dados de trucks_data
        truck_data = next((t for t in trucks_data if t["Numero Equipe"] == truck_number), None)

        if truck_data:
            # Extrair e processar o volume do caminhão
            raw_volume = truck_data.get("volume", "0m³").replace("m³", "").replace(",", ".")

            try:
                truck_volume = float(raw_volume)
                print(f"Volume do caminhão {truck_number}: {truck_volume} m³")
            except ValueError:
                print(f"Erro ao converter o volume: {raw_volume}. Valor padrão 0m³ será utilizado.")
                truck_volume = 0  # Caso ocorra um erro, definir o volume como 0

            print(f"Volume do caminhão {truck_number}: {truck_volume} m³")

            # Criar a rota inicial
            route, client_not_served = make_route.make_best_routes(
                client_not_served,
                "Rua Orlando Odilio Koerich, SN Galpão II - Picadas do Sul, São José - SC, 88102-106",
                truck_volume
            )

            # Se for o caminhão da equipe 1, adicionar clientes especiais
            if truck_data["Numero Equipe"] == 1:
                route, client_not_served = make_route.exceptions(route, client_not_served, special_clients, truck_volume)
                print(f"Clientes especiais adicionados ao caminhão {truck_number}.")
            else:
                print(f"Roteiro do caminhão {truck_number} gerado sem clientes especiais.")

            # Salvar o roteiro e demais arquivos
            with open(f"Data/route_truck{truck_number}.json", "w") as file:
                json.dump(route, file, indent=4)
            print(f"Roteiro de entregas do caminhão {truck_number} salvo em 'route_truck{truck_number}.json'.")

            with open("Data/clientes_nao_atendidos.json", "w") as f:
                json.dump(client_not_served, f, indent=4)
            print("Clientes não atendidos salvos em 'clientes_nao_atendidos.json'.")

            export.create_pdf(
                routes=route,
                truck_number=truck_number,
                truck_size=trucks_data,
                output_file=f"Data/roteiro_entregas_caminhão{truck_number}.pdf"
            )
            print(f"PDF gerado com sucesso: 'roteiro_entregas_caminhão{truck_number}.pdf'.")

            export.create_xlsx(route, output_file=f"Data/roteiro_entregas_caminhão{truck_number}.xlsx")
            print(f"Arquivo Excel gerado com sucesso: 'roteiro_entregas_caminhão{truck_number}.xlsx'.")

            export.create_links_txt(route, f"Data/roteiro_entregas_caminhão{truck_number}.txt")
            print(f"Link da rota salvo em 'roteiro_entregas_caminhão{truck_number}.txt'.")
        else:
            print(f"Dados para o caminhão {truck_number} não encontrados em trucks_data.")

else:
    print("Os arquivos já são iguais. Nenhuma ação foi necessária.")

    # Gera os PDFs caso as rotas já estejam prontas
    print("\nRegenerando os PDFs e arquivos Excel para os caminhões...")

    for truck in range(1, quantidade_de_caminhões + 1):
        print(f"\nAbrindo o arquivo JSON do caminhão {truck}...")

        # Abrir o arquivo JSON do caminhão atual e carregar as rotas
        with open(f"Data/route_truck{truck}.json", 'r') as f:
            route = json.load(f)  # Carrega o conteúdo do arquivo JSON de rotas
        
        try:
            print("Tentando carregar caminhões.json...")
            truck_size_data = export.load_truck_data("Data/caminhoes.json")
            print("Dados de caminhões carregados:", truck_size_data)
        except Exception as e:
            print(f"Erro ao carregar caminhões.json: {e}")

        # Gerar o PDF do roteiro de entregas para o caminhão atual
        print(f"Gerando o PDF para o caminhão {truck}...")
        export.create_pdf(routes=route, truck_number=truck, truck_size=truck_size_data, output_file=f"Data/roteiro_entregas_caminhão{truck}.pdf")
        print(f"PDF gerado com sucesso: 'roteiro_entregas_caminhão{truck}.pdf'.")

        # Gerar o arquivo Excel para o caminhão atual
        print(f"Gerando o arquivo Excel para o caminhão {truck}...")
        export.create_xlsx(route, output_file=f"Data/roteiro_entregas_caminhão{truck}.xlsx")
        print(f"Arquivo Excel gerado com sucesso: 'roteiro_entregas_caminhão{truck}.xlsx'.")

        # Adiciona a funcionalidade para exportar a rota como link do Google Maps
        print(f"Gerando o arquivo de texto com o link da rota para o caminhão {truck}...")
        export.create_links_txt(route, f"Data/roteiro_entregas_caminhão{truck}.txt")
        print(f"Link da rota salvo em 'roteiro_entregas_caminhão{truck}.txt'.")

print("\nProcesso completo de criação de rotas, geração de arquivos e exportação finalizado!")