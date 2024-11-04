from fpdf import FPDF
from datetime import datetime, timedelta

# Função para criar PDFs com informações dos clientes
def create_pdfs(client_data):
    # Removendo o primeiro elemento que é o endereço geral
    client_data.pop(0)

    # Definindo as datas para os próximos 3 dias
    today = datetime.now()
    upcoming_dates = [today + timedelta(days=i) for i in range(3)]
    
    for delivery_date in upcoming_dates:
        # Filtra clientes pela data de entrega
        filtered_clients = [
            client for client in client_data 
            if datetime.strptime(client['Data Entrega'], '%m/%d/%Y').date() == delivery_date.date()
        ]
        
        # Verifica se há clientes para a data atual
        if not filtered_clients:
            print(f"Nenhum cliente encontrado para a data {delivery_date.strftime('%d/%m/%Y')}.")
            continue  # Pula para a próxima data se não houver clientes
        
        # Cria um novo PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Adiciona título
        pdf.cell(200, 10, txt=f"Entregas para {delivery_date.strftime('%d/%m/%Y')}", ln=True, align='C')
        pdf.ln(10)  # Adiciona espaço entre o título e o conteúdo
        
        # Adiciona informações dos clientes no formato desejado
        for index, client in enumerate(filtered_clients, start=1):
            # Obtendo valores, substituindo valores NaN por strings vazias
            numero_pedido = client.get("N° de pedido", "")
            numero_casa = client.get("N° Casa/Ap", "")
            entrega_retirada = client.get("Entrega / Retirada", "")
            endereco = client.get("endereco", "")
            modelo_sofa = client.get("Modelo Sofá", "")
            tipo_montador = client.get("Tipo Montador", "")
            tipo_caminhao = client.get("Tipo caminhão", "")
            local = client.get("Local", "")
            restricao_local = client.get("Restrições local", "Sem restrições") if client.get("Restrições local") is not None else "Sem restrições"
            restricao_horario = client.get("restrições Horário", "Sem restrições") if client.get("restrições Horário") is not None else "Sem restrições"

            # Texto justificado com as informações solicitadas
            pdf.multi_cell(0, 10, 
                txt=(
                    f"Cliente {index}: Nº do pedido: {numero_pedido} | "
                    f"Numero da casa: {numero_casa} | "
                    f"Entrega / Retirada: {entrega_retirada}"
                    f"Endereço: {endereco}"
                    f"Modelo do Sofá: {modelo_sofa} | "
                    f"Tipo Montador: {tipo_montador} | "
                    f"Tipo Caminhão: {tipo_caminhao} | "
                    f"Local: {local}"
                    f"Restrição de local: {restricao_local} | "
                    f"Restrição de Horário: {restricao_horario} | "
                    f"Status: [    ]"
                ),
                align="J"
            )
            pdf.ln(10)  # Adiciona espaço entre os clientes

        # Salva o PDF
        pdf_file_name = f"entregas_{delivery_date.strftime('%Y%m%d')}.pdf"
        pdf.output(pdf_file_name)
        print(f"PDF criado: {pdf_file_name}")