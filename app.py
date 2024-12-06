from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, flash
from Library import export, get_sheet, group_sheet, make_route
import pandas as pd
import json
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Necessário para usar flash messages

# Configuração inicial
CONFIG_FILE = "config.json"
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w") as file:
        json.dump({
            "tolerance_time": 10,
            "limit_time": 60,
            "benefit_coefficient": 1.5,
            "truck_count": 3
        }, file, indent=4)

# Configuração inicial
NEW_CONFIG_FILE = "new_config.json"
if not os.path.exists(NEW_CONFIG_FILE):
    with open(NEW_CONFIG_FILE, "w") as file:
        json.dump({
            "tolerance_time": 10,
            "limit_time": 60,
            "benefit_coefficient": 1.5,
            "truck_count": 3
        }, file, indent=4)

# Rota inicial
@app.route("/")
def index():
    return render_template("index.html")

# Tela de carregamento
@app.route("/processing", methods=["POST"])
def processing():
    # Renderiza a tela de carregamento
    return render_template("processing.html")

@app.route("/calculate_routes", methods=["POST"])
def calculate_routes():
    try:
        # Carregar configurações atuais
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)

        truck_count = config.get("truck_count", 1)
        
        print("Salvando a planilha...")
        get_sheet.save_sheet("pasta 1 José Carlos", tab=2, head=2)
        get_sheet.save_trucks()
        print("Planilha salva com sucesso!")

        # Caminho dos arquivos
        sheet = 'Data/planilha_local.xlsx'
        new_sheet = 'Data/nova_planilha_local.xlsx'

        # Verificar se o arquivo existe
        if not os.path.exists(sheet):
            # Criar uma planilha vazia se o arquivo não existir
            print(f"Arquivo {sheet} não encontrado. Criando um arquivo vazio...")
            df = pd.DataFrame()  # Cria um DataFrame vazio
            df.to_excel(sheet, index=False)  # Salva o DataFrame vazio no arquivo
        else:
            # Ler o arquivo existente
            try:
                df = pd.read_excel(sheet)
            except ValueError:
                print(f"Erro ao ler {sheet}. Tentando criar uma planilha vazia...")
                df = pd.DataFrame()
                df.to_excel(sheet, index=False)
        
        # Ler o novo arquivo
        try:
            new_df = pd.read_excel(new_sheet)
        except ValueError:
            print(f"Erro ao ler {new_sheet}. Criando uma planilha vazia...")
            new_df = pd.DataFrame()
            new_df.to_excel(new_sheet, index=False)

        # Carregar dados dos caminhões
        with open("Data/caminhoes.json", "r") as file:
            trucks_data = json.load(file)

        truck_size_data = export.load_truck_data("Data/caminhoes.json")

        # Carregar nova configuração (se necessário)
        with open(NEW_CONFIG_FILE, "r") as file:  # Exemplo de onde carregar new_config
            new_config = json.load(file)
        
        # Verificar se os arquivos são iguais
        if not df.equals(new_df) or config != new_config:
            # Realizar ações quando as configurações forem diferentes, como salvar os novos dados
            print("As configurações foram atualizadas.")
            new_config = config  # Atualiza o new_config com o novo config

            # Salvar as novas configurações no new_config.json
            with open("Data/new_config.json", "w") as file:
                json.dump(new_config, file, indent=4)

            new_df.to_excel(sheet, index=False)
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
            for truck_number in range(1, truck_count + 1):
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
                        "R. Pedro Cota de Castro, 1993 - Picadas do Sul, São José - SC, 88108-240",
                        truck_volume,
                        config.get("tolerance_time", 240),
                        config.get("limit_time", 240),
                        config.get("benefit_coefficient", 1)
                    )


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
                        truck_size=truck_size_data,
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

            for truck_number in range(1, truck_count + 1):
                print(f"\nAbrindo o arquivo JSON do caminhão {truck_number}...")

                # Abrir o arquivo JSON do caminhão atual e carregar as rotas
                with open(f"Data/route_truck{truck_number}.json", 'r') as f:
                    route = json.load(f)  # Carrega o conteúdo do arquivo JSON de rotas
                
                try:
                    print("Tentando carregar caminhões.json...")
                    truck_size_data = export.load_truck_data("Data/caminhoes.json")
                    print("Dados de caminhões carregados:", truck_size_data)
                except Exception as e:
                    print(f"Erro ao carregar caminhões.json: {e}")

                    export.create_pdf(
                        routes=route,
                        truck_number=truck_number,
                        truck_size=truck_size_data,
                        output_file=f"Data/roteiro_entregas_caminhão{truck_number}.pdf"
                    )
                    print(f"PDF gerado com sucesso: 'roteiro_entregas_caminhão{truck_number}.pdf'.")

                    export.create_xlsx(route, output_file=f"Data/roteiro_entregas_caminhão{truck_number}.xlsx")
                    print(f"Arquivo Excel gerado com sucesso: 'roteiro_entregas_caminhão{truck_number}.xlsx'.")

                    export.create_links_txt(route, f"Data/roteiro_entregas_caminhão{truck_number}.txt")
                    print(f"Link da rota salvo em 'roteiro_entregas_caminhão{truck_number}.txt'.")
                else:
                    print(f"Dados para o caminhão {truck_number} não encontrados em trucks_data.")


        print("\nProcesso completo de criação de rotas, geração de arquivos e exportação finalizado!")

        return jsonify({"success": True, "redirect_url": url_for("generate")})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route("/generate")
def generate():
    # Carregar as configurações do arquivo
    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)
    
    truck_count = config.get("truck_count", 1)  # Número de caminhões
    
    # Verifica se houve algum erro
    error = request.args.get("error")
    if error:
        return render_template("download.html", error=error)

    # Cria uma lista de arquivos gerados para cada caminhão
    generated_files = []
    for truck_number in range(1, truck_count + 1):
        # Caminhos dos arquivos gerados para o caminhão
        pdf_path = f"Data/roteiro_entregas_caminhão{truck_number}.pdf"
        xlsx_path = f"Data/roteiro_entregas_caminhão{truck_number}.xlsx"
        txt_path = f"Data/roteiro_entregas_caminhão{truck_number}.txt"

        # Adiciona as informações dos arquivos à lista
        generated_files.append({
            "truck_number": truck_number,
            "pdf_path": pdf_path,
            "xlsx_path": xlsx_path,
            "txt_path": txt_path
        })

    # Passa a lista de arquivos gerados e o truck_count para o template
    return render_template("download.html", generated_files=generated_files, truck_count=truck_count)

# Rota para configurações
@app.route("/config", methods=["GET", "POST"])
def config():
    if request.method == "POST":
        new_config = {
            "tolerance_time": int(request.form["tolerance_time"]),
            "limit_time": int(request.form["limit_time"]),
            "benefit_coefficient": float(request.form["benefit_coefficient"]),
            "truck_count": int(request.form["truck_count"]),
        }
        with open(CONFIG_FILE, "w") as file:
            json.dump(new_config, file, indent=4)
        return redirect(url_for("index"))
    
    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)
    return render_template("config.html", config=config)

# Download dos arquivos
@app.route("/download/<path:filename>")
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(port= 8000, debug=True)