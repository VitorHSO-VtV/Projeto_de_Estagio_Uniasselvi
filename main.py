from Library import get_sheet, group_sheet, make_route, export
import pandas as pd
import json
import os

quantidade_de_caminhões = 3

# Salva a planilha com o nome "pasta 1 José Carlos"
print("Salvando a planilha...")
get_sheet.save_sheet("pasta 1 José Carlos", tab=2, head=2)
print("Planilha salva com sucesso!")

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

    # Transforma os dados agrupados em um roteiro de entregas ordenado
    for truck in range(1, quantidade_de_caminhões + 1):
        print(f"\nCriando o roteiro de entregas para o caminhão {truck}...")

        # Chama a função que cria a rota e organiza os clientes não atendidos
        route, client_not_served = make_route.make_best_routes(client_not_served, 
                                                            "Rua Orlando Odilio Koerich, SN Galpão II - Picadas do Sul, São José - SC, 88102-106")
        
        # Se for o caminhão 1, adiciona os clientes especiais à rota
        if truck == 1:
            route, client_not_served = make_route.exceptions(route, client_not_served, special_clients)
            print(f"Clientes especiais adicionados ao caminhão {truck}.")
        else:
            print(f"Roteiro do caminhão {truck} gerado sem clientes especiais.")  # Para caminhões 2 e 3

        # Salva o roteiro gerado em um arquivo JSON para o caminhão atual
        print(f"Salvando o roteiro de entregas do caminhão {truck} em JSON...")
        with open(f"Data/route_truck{truck}.json", "w") as file:
            json.dump(route, file, indent=4)
        print(f"Roteiro de entregas do caminhão {truck} salvo em 'route_truck{truck}.json'.")

        # Salva os clientes não atendidos em um arquivo JSON
        print("Salvando os clientes não atendidos em JSON...")
        with open("Data/clientes_nao_atendidos.json", "w") as f:
            json.dump(client_not_served, f, indent=4)
        print("Clientes não atendidos salvos em 'clientes_nao_atendidos.json'.")

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

        # Cria um arquivo Excel com o roteiro do caminhão atual
        print(f"Gerando o arquivo Excel do roteiro de entregas do caminhão {truck}...")
        export.create_xlsx(route, output_file=f"Data/roteiro_entregas_caminhão{truck}.xlsx")
        print(f"Arquivo Excel gerado com sucesso: 'roteiro_entregas_caminhão{truck}.xlsx'.")
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

print("\nProcesso completo de criação de rotas, geração de arquivos e exportação finalizado!")