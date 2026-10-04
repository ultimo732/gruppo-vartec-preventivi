import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(page_title="Gruppo Vartec Preventivi", layout="centered")
st.title("Gruppo Vartec Preventivi")
st.subheader("Generatore Preventivi Edili")

st.sidebar.header("Carica i documenti di gara")
computo_file = st.sidebar.file_uploader("Carica computo metrico (Excel/CSV)", type=["xlsx", "csv"])
pianta_file = st.sidebar.file_uploader("Carica planimetria (PDF/Immagine)", type=["pdf", "png", "jpg"])

def calcola_preventivo(computo_data):
    prezzi_unitari = {
        'Cemento': 120.0, 
        'Acciaio': 800.0, 
        'Laterizi': 15.0, 
        'Intonaco': 25.0,
        'Scavi e Movimento Terra': 35.0,
        'Opere in Muratura': 95.0
    }
    totale = 0
    riepilogo = []
    
    if computo_data.name.endswith('.csv'):
        df = pd.read_csv(computo_data)
    else:
        df = pd.read_excel(computo_data)
        
    if 'Materiale' not in df.columns or 'Quantita' not in df.columns:
        st.error("Il file del computo metrico deve contenere le colonne 'Materiale' e 'Quantita'.")
        return None, 0

    for index, row in df.iterrows():
        materiale = str(row['Materiale']).strip()
        try:
            quantita = float(row['Quantita'])
        except ValueError:
            quantita = 0.0
            
        prezzo_unitario = prezzi_unitari.get(materiale, 50.0)
        costo_totale = quantita * prezzo_unitario
        totale += costo_totale
        riepilogo.append({
            'Materiale': materiale, 
            'Quantita': quantita, 
            'Prezzo Unitario': prezzo_unitario, 
            'Totale': costo_totale
        })
        
    return riepilogo, totale

def genera_pdf(riepilogo, totale):
    pdf_path = "preventivo_vartec.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('Title', parent=styles['Normal'], fontSize=22, leading=26, alignment=1, textColor=colors.HexColor('#051e3e'), fontName='Helvetica-Bold')
    h2_style = ParagraphStyle('H2', parent=styles['Normal'], fontSize=14, leading=18, textColor=colors.HexColor('#051e3e'), fontName='Helvetica-Bold')
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=11, leading=15)
    bold_style = ParagraphStyle('Bold', parent=styles['Normal'], fontSize=12, leading=16, fontName='Helvetica-Bold')

    story.append(Spacer(1, 10))
    story.append(Paragraph("GRUPPO VARTEC", title_style))
    story.append(Paragraph("Costruzioni edili e Nolo attrezzature - Cassano all'Ionio (CS)", ParagraphStyle('Sub', parent=normal_style, alignment=1, textColor=colors.gray)))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Preventivo Economico Lavori", h2_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Dettaglio voci computo metrico:", bold_style))
    story.append(Spacer(1, 5))
    
    for item in riepilogo:
        testo_voce = f"• <b>{item['Materiale']}</b>: {item['Quantita']} unità × {item['Prezzo Unitario']:.2f} € = <b>{item['Totale']:.2f} €</b>"
        story.append(Paragraph(testo_voce, normal_style))
        
    story.append(Spacer(1, 15))
    story.append(Paragraph(f"Costo Totale Stimato: {totale:.2f} € (IVA esclusa)", bold_style))
    
    doc.build(story)
    return pdf_path

if computo_file and pianta_file:
    st.success("Documenti caricati correttamente!")
    st.info(f"Computo caricato: {computo_file.name} | Planimetria caricata: {pianta_file.name}")
    
    if st.button("Genera Preventivo"):
        with st.spinner("Elaborazione dati e raffronto con prezzario in corso..."):
            riepilogo, totale = calcola_preventivo(computo_file)
            
            if riepilogo:
                st.write("### Riepilogo Costi Stimati")
                df_riepilogo = pd.DataFrame(riepilogo)
                st.table(df_riepilogo)
                st.markdown(f"### **Totale Complessivo: {totale:.2f} €**")
                
                pdf_path = genera_pdf(riepilogo, totale)
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="Scarica Preventivo in PDF",
                        data=pdf_file,
                        file_name="Preventivo_Gruppo_Vartec.pdf",
                        mime="application/pdf"
                    )
else:
    st.warning("⚠️ Per favore, carica sia il computo metrico (Excel/CSV) che la planimetria dalla barra laterale per procedere.")
