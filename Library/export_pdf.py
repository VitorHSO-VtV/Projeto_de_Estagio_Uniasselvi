from fpdf import FPDF
from datetime import datetime, timedelta

# Função para criar PDFs com informações dos clientes
def create_pdfs(client_data):
    # Definindo as datas para ontem, hoje e amanhã
    today = datetime.now()
    date_range = [today + timedelta(days=i) for i in range(-1, 2)]
    
    # Iterar sobre as datas e criar os PDFs
    for delivery_date in date_range:
        # Formatar a data para comparação com as chaves do dicionário
        formatted_date = delivery_date.strftime("%m/%d/%Y")
        
        # Verifica se há dados para a data atual
        if formatted_date not in client_data:
            print(f"\033[33mNenhum cliente encontrado para a data {formatted_date}. Ignorando...\033[0m")
            continue  # Pula para a próxima data se não houver clientes
        
        # Filtra os dados para a data específica (dentro de uma lista de clientes)
        filtered_clients = client_data[formatted_date]
        
        # Cria um novo PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Adiciona título
        pdf.cell(200, 10, txt=f"Entregas para {formatted_date}", ln=True, align='C')
        pdf.ln(10)  # Adiciona espaço entre o título e o conteúdo
        
        # Adiciona informações dos clientes no formato desejado
        for index, client in enumerate(filtered_clients, start=1):
            # Obtendo valores, substituindo valores vazios ou None por "nan"
            numero_pedido = client.get("pedido", "nan") or "nan"
            numero_casa = client.get("numero_casa", "nan") or "nan"
            entrega_retirada = client.get("entrega_retirada", "nan") or "nan"
            endereco = client.get("endereco", "nan") or "nan"
            modelo_sofa = client.get("modelo_sofa", "nan") or "nan"
            tipo_montador = client.get("tipo_montador", "nan") or "nan"
            tipo_caminhao = client.get("tipo_caminhao", "nan") or "nan"
            local = client.get("local", "nan") or "nan"
            restricao_local = client.get("restricao_local", "Sem restrições") or "nan"
            restricao_horario = client.get("restricao_horario", "Sem restrições") or "nan"

            # Verifica inconsistências nos dados e emite alertas
            if numero_pedido == "nan":
                print(f"\033[33mAviso: Falta o número de pedido para o cliente na parada {index}.\033[0m")
            if endereco == "nan":
                print(f"\033[33mAviso: Falta o endereço para o cliente (Pedido: {numero_pedido}) na parada {index}.\033[0m")
            
            # Verifica se algum campo está com valor "nan"
            missing_info = [field for field, value in [
                ("Número de Pedido", numero_pedido),
                ("Número da Casa", numero_casa),
                ("Entrega / Retirada", entrega_retirada),
                ("Endereço", endereco),
                ("Modelo de Sofá", modelo_sofa),
                ("Tipo de Montador", tipo_montador),
                ("Tipo de Caminhão", tipo_caminhao),
                ("Local", local),
                ("Restrição de Local", restricao_local),
                ("Restrição de Horário", restricao_horario)
            ] if value == "nan"]

            if missing_info:
                print(f"\033[33mAviso: Faltam informações para o cliente (Pedido: {numero_pedido}) na(s) seguinte(s) parada(s): {', '.join(missing_info)}.\033[0m")
            
            # Texto justificado com as informações solicitadas
            pdf.multi_cell(0, 10, 
                txt=(f" | Parada {index} | Nº do pedido: {numero_pedido} | "
                     f"Numero da casa: {numero_casa} | "
                     f"Entrega / Retirada: {entrega_retirada} | "
                     f"Endereço: {endereco} | "
                     f"Modelo do Sofá: {modelo_sofa} | "
                     f"Tipo Montador: {tipo_montador} | "
                     f"Tipo Caminhão: {tipo_caminhao} | "
                     f"Local: {local} | "
                     f"Restrição de local: {restricao_local} | "
                     f"Restrição de Horário: {restricao_horario} | "
                     f"Status: [    ] | "),
                align="J"
            )
            pdf.ln(10)  # Adiciona espaço entre os clientes

        # Salva o PDF
        pdf_file_name = f"entregas_{formatted_date.replace('/', '')}.pdf"
        try:
            pdf.output(pdf_file_name)
            print(f"\033[32mPDF criado com sucesso: {pdf_file_name}\033[0m")
        except Exception as e:
            print(f"\033[31mErro ao criar o PDF: {e}\033[0m")
