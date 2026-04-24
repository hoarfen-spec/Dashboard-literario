import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import plotly.express as px

st.set_page_config(page_title="Dashboard Literário", page_icon="📰", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 2rem; max-width: 1300px;}
h1,h2,h3 {font-family: Georgia, serif;}
.metric-card{background:linear-gradient(135deg,#171923,#232633);border:1px solid #33384a;border-radius:18px;padding:18px;box-shadow:0 8px 24px rgba(0,0,0,.25)}
.big-number{font-size:30px;font-weight:800}.small-label{color:#aab0c0;font-size:14px}
.editorial{border-left:5px solid #d4af37;padding:14px 18px;background:#161922;border-radius:10px;color:#e8e8e8}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def google_books(query, max_results=25):
    try:
        r=requests.get("https://www.googleapis.com/books/v1/volumes",params={"q":query,"maxResults":max_results,"printType":"books","projection":"lite"},timeout=12)
        r.raise_for_status()
        rows=[]
        for item in r.json().get("items",[]):
            v=item.get("volumeInfo",{}); sale=item.get("saleInfo",{})
            rows.append({"fonte":"Google Books","titulo":v.get("title"),"autor":", ".join(v.get("authors",[])) if v.get("authors") else "Desconhecido","editora":v.get("publisher","A confirmar"),"ano_publicacao":(v.get("publishedDate","")[:4] if v.get("publishedDate") else None),"idioma":v.get("language","n/d"),"categorias":", ".join(v.get("categories",[])) if v.get("categories") else "n/d","isbn":next((i.get("identifier") for i in v.get("industryIdentifiers",[]) if i.get("type") in ["ISBN_13","ISBN_10"]),None),"preco":sale.get("listPrice",{}).get("amount"),"moeda":sale.get("listPrice",{}).get("currencyCode"),"link":v.get("infoLink")})
        return pd.DataFrame(rows)
    except Exception as e:
        st.warning(f"Google Books indisponível agora: {e}"); return pd.DataFrame()

@st.cache_data(ttl=3600)
def open_library(query, limit=25):
    try:
        r=requests.get("https://openlibrary.org/search.json",params={"q":query,"limit":limit},timeout=12); r.raise_for_status()
        rows=[]
        for d in r.json().get("docs",[]):
            rows.append({"fonte":"Open Library","titulo":d.get("title"),"autor":", ".join(d.get("author_name",[])[:3]) if d.get("author_name") else "Desconhecido","editora":", ".join(d.get("publisher",[])[:2]) if d.get("publisher") else "A confirmar","ano_publicacao":d.get("first_publish_year"),"idioma":", ".join(d.get("language",[])[:3]) if d.get("language") else "n/d","categorias":", ".join(d.get("subject",[])[:4]) if d.get("subject") else "n/d","isbn":d.get("isbn",[None])[0] if d.get("isbn") else None,"preco":None,"moeda":None,"link":"https://openlibrary.org"+d.get("key","") if d.get("key") else None})
        return pd.DataFrame(rows)
    except Exception as e:
        st.warning(f"Open Library indisponível agora: {e}"); return pd.DataFrame()

def seed_sales():
    livros=[("Memorial do Convento","José Saramago","Portugal","Romance","Porto Editora","Portugal"),("Capitães da Areia","Jorge Amado","Brasil","Romance","Companhia das Letras","Brasil"),("A Hora da Estrela","Clarice Lispector","Brasil","Ficção","Rocco","Brasil"),("Os Maias","Eça de Queirós","Portugal","Romance","Livros do Brasil","Portugal"),("Grande Sertão: Veredas","Guimarães Rosa","Brasil","Ficção","Nova Fronteira","Brasil"),("Ensaio sobre a Cegueira","José Saramago","Portugal","Ficção","Companhia das Letras","Internacional"),("Livro do Desassossego","Fernando Pessoa","Portugal","Poesia","Assírio & Alvim","Internacional"),("Torto Arado","Itamar Vieira Junior","Brasil","Romance","Todavia","Brasil"),("A Máquina de Fazer Espanhóis","Valter Hugo Mãe","Portugal","Ficção","Porto Editora","Portugal"),("Ideias para Adiar o Fim do Mundo","Ailton Krenak","Brasil","Ensaio","Companhia das Letras","Brasil")]
    rows=[]
    for i,(titulo,autor,nac,genero,editora,mercado) in enumerate(livros,1):
        for ano in [2023,2024,2025,2026]:
            for mes in range(1,13):
                unidades=int((400+i*80+(ano-2023)*120+(mes%5)*70)*(1.25 if mercado=="Brasil" else 1.0)); preco=14.9+(i%5)*2.5
                rows.append({"book_id":i,"titulo":titulo,"autor":autor,"nacionalidade_autor":nac,"genero":genero,"editora":editora,"mercado":mercado,"pais_venda":mercado,"data_venda":f"{ano}-{mes:02d}-15","ano":ano,"mes":mes,"unidades_vendidas":unidades,"preco_unitario":preco,"receita":round(unidades*preco,2),"idioma":"pt","formato":["físico","ebook","audiobook"][i%3]})
    return pd.DataFrame(rows)

def awards():
    return pd.DataFrame([
        ["Prémio Literário José Saramago","Portugal","Fundação Círculo de Leitores","Romance/Novela","2026-01-20","2026-05-15","A confirmar","Último trimestre 2026","40000","EUR","Aberto","https://culturaportugal.gov.pt/pt/criar/apoios/diversos-2026/premio-literario-jose-saramago-2026/"],
        ["Prêmio Jabuti","Brasil","CBL","Várias categorias","2026-03-31","2026-05-19","A confirmar","A confirmar","A confirmar","BRL","Aberto","https://cbl.org.br/"],
        ["Prêmio Oceanos","Brasil/Lusofonia","Associação Oceanos","Livro em língua portuguesa","2026-02-09","2026-03-09","A confirmar","A confirmar","A confirmar","BRL","Encerrado","https://premiooceanos2026.associacaooceanos.org/"],
        ["Prémio Camões","Lusofonia","Governos Portugal/Brasil","Obra literária","A confirmar","A confirmar","A confirmar","A confirmar","100000","EUR","A confirmar","https://www.dglab.gov.pt/"],
        ["Prémios PEN Portugal","Portugal","PEN Clube Português","Poesia, Ensaio, Narrativa","2026-04-01","A confirmar","A confirmar","A confirmar","A confirmar","EUR","A confirmar","https://livro.dglab.gov.pt/"],
        ["Prêmio Biblioteca Nacional","Brasil","Fundação Biblioteca Nacional","Várias categorias","A confirmar","A confirmar","A confirmar","A confirmar","A confirmar","BRL","A confirmar","https://www.gov.br/bn/"],
    ], columns=["nome","pais","organizador","categorias","data_abertura","data_limite","data_finalistas","data_vencedor","valor_premio","moeda","estado","link_oficial"])

def kpi_card(label,value):
    st.markdown(f'<div class="metric-card"><div class="small-label">{label}</div><div class="big-number">{value}</div></div>', unsafe_allow_html=True)

def to_excel(df):
    out=BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer: df.to_excel(writer,index=False,sheet_name="dados")
    return out.getvalue()

st.title("📰 Dashboard Literário")
st.markdown('<div class="editorial">Painel editorial com vendas demonstrativas, metadados reais via APIs públicas e calendário de prémios literários. Nota: APIs públicas dão metadados; vendas comerciais reais dependem de CSV/API de livrarias, editoras ou serviços pagos.</div>', unsafe_allow_html=True)
sales=seed_sales(); premios=awards()

with st.sidebar:
    st.header("🎛️ Filtros")
    anos=st.multiselect("Ano", sorted(sales["ano"].unique()), default=sorted(sales["ano"].unique()))
    mercados=st.multiselect("Mercado", sorted(sales["mercado"].unique()), default=sorted(sales["mercado"].unique()))
    generos=st.multiselect("Género", sorted(sales["genero"].unique()), default=sorted(sales["genero"].unique()))
    nacs=st.multiselect("Nacionalidade", sorted(sales["nacionalidade_autor"].unique()), default=sorted(sales["nacionalidade_autor"].unique()))
    st.divider(); q=st.text_input("🔎 Pesquisa API", "literatura portuguesa")
    api_source=st.selectbox("Fonte de metadados", ["Google Books + Open Library","Google Books","Open Library"])

f=sales[(sales["ano"].isin(anos))&(sales["mercado"].isin(mercados))&(sales["genero"].isin(generos))&(sales["nacionalidade_autor"].isin(nacs))]
tabs=st.tabs(["Visão Geral","Géneros","Nacionalidades","Portugal vs Brasil vs Mundo","Rankings","APIs reais","Prémios","Exportações"])

with tabs[0]:
    c1,c2,c3,c4=st.columns(4)
    with c1: kpi_card("Livros vendidos", f"{f['unidades_vendidas'].sum():,.0f}".replace(",","."))
    with c2: kpi_card("Receita", f"€{f['receita'].sum():,.0f}".replace(",","."))
    with c3: kpi_card("Títulos", f"{f['titulo'].nunique()}")
    with c4: kpi_card("Autores", f"{f['autor'].nunique()}")
    mensal=f.groupby(["ano","mes"],as_index=False)["receita"].sum(); mensal["periodo"]=pd.to_datetime(mensal["ano"].astype(str)+"-"+mensal["mes"].astype(str)+"-01")
    st.plotly_chart(px.line(mensal,x="periodo",y="receita",markers=True,title="Evolução da receita"),use_container_width=True)
    a,b=st.columns(2)
    with a: st.plotly_chart(px.bar(f.groupby("genero",as_index=False)["unidades_vendidas"].sum().sort_values("unidades_vendidas"),x="unidades_vendidas",y="genero",orientation="h",title="Vendas por género"),use_container_width=True)
    with b: st.plotly_chart(px.treemap(f,path=["mercado","genero"],values="receita",title="Treemap mercado → género"),use_container_width=True)

with tabs[1]:
    g=f.groupby("genero",as_index=False).agg(unidades=("unidades_vendidas","sum"),receita=("receita","sum"))
    st.plotly_chart(px.bar(g,x="genero",y="unidades",text_auto=True,title="Unidades por género"),use_container_width=True); st.dataframe(g,use_container_width=True)

with tabs[2]:
    n=f.groupby("nacionalidade_autor",as_index=False).agg(unidades=("unidades_vendidas","sum"),receita=("receita","sum"))
    st.plotly_chart(px.pie(n,names="nacionalidade_autor",values="receita",title="Receita por nacionalidade"),use_container_width=True); st.dataframe(n,use_container_width=True)

with tabs[3]:
    m=f.groupby(["mercado","ano"],as_index=False)["receita"].sum()
    st.plotly_chart(px.bar(m,x="ano",y="receita",color="mercado",barmode="group",title="Portugal vs Brasil vs Internacional"),use_container_width=True)

with tabs[4]:
    a,b=st.columns(2)
    with a: st.subheader("Top livros"); st.dataframe(f.groupby(["titulo","autor"],as_index=False)["unidades_vendidas"].sum().sort_values("unidades_vendidas",ascending=False).head(10),use_container_width=True)
    with b: st.subheader("Top autores"); st.dataframe(f.groupby(["autor","nacionalidade_autor"],as_index=False)["receita"].sum().sort_values("receita",ascending=False).head(10),use_container_width=True)

with tabs[5]:
    st.subheader("🌐 Metadados reais via APIs públicas")
    dfs=[]
    if api_source!="Open Library": dfs.append(google_books(q))
    if api_source!="Google Books": dfs.append(open_library(q))
    meta=pd.concat(dfs,ignore_index=True) if dfs else pd.DataFrame()
    if not meta.empty:
        st.dataframe(meta,use_container_width=True)
        st.download_button("Baixar metadados CSV",meta.to_csv(index=False).encode("utf-8"),"metadados_livros.csv","text/csv")
    else: st.info("Sem resultados.")

with tabs[6]:
    st.subheader("🏆 Prémios literários"); st.dataframe(premios,use_container_width=True)
    pp=premios[premios["data_limite"].str.match(r"\d{4}-\d{2}-\d{2}",na=False)].copy()
    if not pp.empty:
        pp["data_limite_dt"]=pd.to_datetime(pp["data_limite"])
        st.plotly_chart(px.scatter(pp,x="data_limite_dt",y="nome",color="estado",size=[18]*len(pp),title="Calendário de deadlines confirmados"),use_container_width=True)

with tabs[7]:
    st.subheader("📤 Exportações")
    c1,c2,c3=st.columns(3)
    with c1: st.download_button("Vendas CSV",f.to_csv(index=False).encode("utf-8"),"vendas_filtradas.csv","text/csv")
    with c2: st.download_button("Vendas Excel",to_excel(f),"vendas_filtradas.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with c3: st.download_button("Prémios CSV",premios.to_csv(index=False).encode("utf-8"),"premios_literarios.csv","text/csv")

st.caption("Fontes API: Google Books e Open Library. Vendas são demonstrativas até ligares CSV/API comercial real.")
