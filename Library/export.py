from fpdf import FPDF
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font

def create_pdf(routes, output_file='roteiro_entregas.pdf'):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    def safe_value(value):
        if value is None or value != value:  # Verifica se é NaN
            return 'Sem informações'
        return str(value)
    
    pdf.set_font("Arial", size=12)
    
    for date, daily_route in routes.items():
        pdf.add_page()
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(200, 10, txt=f"Data de Entrega: {date}", ln=True)
        pdf.ln(5)  # Linha em branco
        
        for session, clients in daily_route.items():
            pdf.set_font("Arial", style='B', size=10)
            pdf.cell(200, 10, txt=f"\n{session.capitalize()}:", ln=True)
            pdf.set_font("Arial", size=10)

            for idx, client in enumerate(clients, start=1):
                pdf.cell(200, 10, txt=f"Parada {idx}", ln=True)
                
                client_info = (
                    f"Nº do pedido: {safe_value(client.get('N\u00b0 de pedido'))} | "
                    f"Data de entrega: {safe_value(client.get('Data Entrega'))} | "
                    f"CEP: {safe_value(client.get('Cep'))} | "
                    f"Número da casa: {safe_value(client.get('N\u00b0 Casa/Ap'))} | "
                    f"Endereço: {safe_value(client.get('endereco'))} | "
                    f"Modelo do Sofá: {safe_value(client.get('Modelo Sof\u00e1'))} | "
                    f"Medida Sofá: {safe_value(client.get('Medida Sof\u00e1'))} | "
                    f"Características Sofá: {safe_value(client.get('Caracter\u00edsticas sof\u00e1'))} | "
                    f"Tipo Montador: {safe_value(client.get('Tipo Montador'))} | "
                    f"Tipo Caminhão: {safe_value(client.get('Tipo caminh\u00e3o'))} | "
                    f"Local: {safe_value(client.get('Local'))} | "
                    f"Andar: {safe_value(client.get('andar'))} | "
                    f"Restrição de local: {safe_value(client.get('Restri\u00e7\u00f5es local Elevador'))} | "
                    f"Restrição de Horário: {safe_value(client.get('restri\u00e7\u00f5es Hor\u00e1rio'))} | "
                    f"Status: {safe_value(client.get('status'))}"
                )

                pdf.multi_cell(0, 10, txt=client_info)
                pdf.ln(2)  # Linha em branco para separar as paradas
    
    pdf.output(output_file)
    print(f"PDF gerado com sucesso em {output_file}")

def create_xlsx(routes, output_file='roteiro_entregas.xlsx'):
    data_for_export = []

    def safe_value(value):
        if value is None or value != value:
            return 'Sem informações'
        return str(value)

    for date, daily_route in routes.items():
        for session, clients in daily_route.items():
            for client in clients:
                if "retorno ao ponto de partida" not in str(client.get('status')).lower():
                    data_for_export.append({
                        "Nº Pedido": safe_value(client.get('N\u00b0 de pedido')),
                        "Data de entrega": safe_value(client.get('Data Entrega')),
                        "Período": session,
                        "Nome do cliente": safe_value(client.get('Cliente', 'Desconhecido')),
                        "Bairro": safe_value(client.get('bairro'))
                    })

    df = pd.DataFrame(data_for_export)
    df.to_excel(output_file, index=False, engine='openpyxl')

    wb = load_workbook(output_file)
    ws = wb.active

    bold_font = Font(bold=True)
    center_alignment = Alignment(horizontal='center', vertical='center')

    for cell in ws[1]:
        cell.font = bold_font
        cell.alignment = center_alignment

    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
        for cell in row:
            cell.alignment = center_alignment

    wb.save(output_file)
    print(f"Arquivo XLSX gerado com sucesso em {output_file}")