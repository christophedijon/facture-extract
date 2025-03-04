import streamlit as st
import pandas as pd
import pdfplumber
import os

def extract_data_from_pdf(pdf_path):
    extracted_data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split("\n")
                for line in lines:
                    parts = line.split()
                    if len(parts) > 3 and parts[0].isdigit():
                        extracted_data.append((parts[0], " ".join(parts[1:-2]), parts[-2], parts[-1]))
    
    df = pd.DataFrame(extracted_data, columns=[
        "Numéro article", "Désignation de l'article", "Montant HT (€)", "TVA"])
    
    df["Catégorie"] = df["Désignation de l'article"].apply(categorize_item)
    df["N° compte comptable"], df["Nom du plan comptable"] = zip(*df["Catégorie"].apply(map_accounting))
    
    return df

def categorize_item(description):
    if "GIN" in description or "LIQUEUR" in description or "WHISKY" in description:
        return "Spiritueux"
    elif "VIN" in description or "CHAMPAGNE" in description:
        return "Champagnes"
    elif "JUS" in description or "SODA" in description or "EAU" in description:
        return "Boissons non alcoolisées"
    elif "FROMAGE" in description:
        return "Produits laitiers"
    elif "VIANDE" in description:
        return "Charcuterie"
    elif "LÉGUMES" in description or "FRUITS" in description:
        return "Fruits et légumes"
    elif "ALCOOL MENAGER" in description:
        return "Droguerie"
    else:
        return "Épicerie sèche"

def map_accounting(category):
    accounts = {
        "Spiritueux": ("6072", "Achats de boissons alcoolisées"),
        "Champagnes": ("6072", "Achats de boissons alcoolisées"),
        "Boissons non alcoolisées": ("6071", "Achats de boissons sans alcool"),
        "Produits laitiers": ("6074", "Achats de matières premières et fournitures"),
        "Charcuterie": ("6074", "Achats de matières premières et fournitures"),
        "Fruits et légumes": ("6073", "Achats de marchandises"),
        "Droguerie": ("6063", "Fournitures d’entretien et de petit équipement"),
        "Épicerie sèche": ("6074", "Achats de matières premières et fournitures")
    }
    return accounts.get(category, ("6074", "Achats de matières premières et fournitures"))

st.title("Extraction Facture PDF vers Excel")

uploaded_file = st.file_uploader("Déposez votre facture PDF ici", type=["pdf"])

if uploaded_file is not None:
    pdf_path = os.path.join("uploads", uploaded_file.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    df_facture = extract_data_from_pdf(pdf_path)
    
    st.write("### Aperçu des données extraites")
    st.dataframe(df_facture)
    
    output_path = pdf_path.replace(".pdf", ".xlsx")
    df_facture.to_excel(output_path, index=False)
    
    with open(output_path, "rb") as f:
        st.download_button("Télécharger le fichier Excel", f, file_name="facture_extrait.xlsx")
