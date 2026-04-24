import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard Literário", layout="wide")

st.title("📰 Dashboard Literário")

# Dados fake simples
data = {
    "Genero": ["Romance", "Ficção", "Poesia", "Ensaios"],
    "Vendas": [12000, 9000, 3000, 2000]
}

df = pd.DataFrame(data)

st.subheader("📊 Vendas por Género")
st.bar_chart(df.set_index("Genero"))

st.subheader("📋 Dados")
st.dataframe(df)
