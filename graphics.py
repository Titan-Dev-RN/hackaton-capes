import json
import pandas as pd
import plotly.express as px
from textblob import TextBlob
from transformers import pipeline
from flask import Flask
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.io as pio
import plotly.express as px

# Função para analisar o sentimento com a IA simples (TextBlob)
def analise_sentimento_simples(texto):
    blob = TextBlob(texto)
    sentimento = blob.sentiment.polarity
    if sentimento > 0:
        return 'Positivo', sentimento
    elif sentimento < 0:
        return 'Negativo', sentimento
    else:
        return 'Neutro', sentimento

# Função para analisar o sentimento com a IA avançada (Transformers)
def analise_sentimento_avancada(texto):
    analisador_sentimentos = pipeline("sentiment-analysis", truncation=True, padding=True)
    resultado = analisador_sentimentos(texto)
    return resultado[0]['label'], resultado[0]['score']

# Função para aplicar a análise de sentimentos em todos os artigos
def aplicar_analise_sentimentos(df, metodo='simples'):
    sentimentos = []
    for resumo in df['resume']:
        if metodo == 'simples':
            sentimento, score = analise_sentimento_simples(resumo)
        elif metodo == 'avancado':
            sentimento, score = analise_sentimento_avancada(resumo)
        sentimentos.append({'sentimento': sentimento, 'score': score})
    return pd.DataFrame(sentimentos)

# Dados JSON fornecidos
# Carregar dados do arquivo JSON
with open('papers.json', 'r', encoding='utf-8') as file:
    dados_json = json.load(file)

# Transformando JSON em DataFrame
df = pd.json_normalize(dados_json)

# Escolha do método de análise de sentimentos (simples ou avançado)
# Inicialmente, configurado para 'simples', mas vai ser alterado via Dash
metodo_analise = 'simples'

# Aplicando a análise de sentimentos nos resumos dos artigos
df_sentimentos = aplicar_analise_sentimentos(df, metodo=metodo_analise)

# Adicionando os resultados da análise de sentimentos ao DataFrame original
df['sentimento'] = df_sentimentos['sentimento']
df['score'] = df_sentimentos['score']

# Criando os gráficos
grafico_ano = px.histogram(
    df,
    x="year",
    title="Distribuição de Artigos por Ano",
    labels={"year": "Ano", "count": "Quantidade de Artigos"},
    nbins=len(df['year'].unique())
)

grafico_idioma = px.bar(
    df["language"].value_counts().reset_index(),
    x="index",
    y="language",
    title="Distribuição de Artigos por Idioma",
    labels={"index": "Idioma", "language": "Quantidade"}
)

grafico_pais = px.pie(
    df,
    names="country_paper",
    title="Distribuição de Artigos por País",
    hole=0.4
)

grafico_sentimentos = px.histogram(
    df,
    x="sentimento",
    title="Análise de Sentimentos dos Artigos",
    labels={"sentimento": "Sentimento", "count": "Quantidade de Artigos"},
    nbins=len(df['sentimento'].unique())
)

# Inicializando o servidor Flask
server = Flask(__name__)

# Inicializando o Dash com Flask
app = dash.Dash(__name__, server=server, url_base_pathname='/')

# Layout redesenhado
app.layout = html.Div([
    # Cabeçalho
    html.Div([
        html.H1("Dashboard de Análise de Artigos Acadêmicos", style={'color': '#ffffff'}),
        html.P("Análise interativa de artigos acadêmicos por ano, idioma, país e sentimentos.",
               style={'color': '#ffffff'})
    ], style={
        'backgroundColor': '#1f2c56',
        'padding': '20px',
        'textAlign': 'center',
        'marginBottom': '20px'
    }),

    # Filtros
    html.Div([
        html.Label("Escolha o método de análise de sentimentos:", style={'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='dropdown-analise',
            options=[
                {'label': 'Análise Simples (TextBlob)', 'value': 'simples'},
                {'label': 'Análise Avançada (Transformers)', 'value': 'avancado'}
            ],
            value='simples',
            style={'width': '50%', 'margin': 'auto'}
        )
    ], style={'padding': '10px', 'backgroundColor': '#f8f9fa', 'marginBottom': '20px'}),

    # Container dos gráficos
    html.Div([
        # Linha 1: Gráficos lado a lado
        html.Div([
            html.Div([
                dcc.Graph(id='grafico-ano')
            ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
            html.Div([
                dcc.Graph(id='grafico-idioma')
            ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        ], style={'display': 'flex', 'justifyContent': 'space-between'}),

        # Linha 2: Gráficos lado a lado
        html.Div([
            html.Div([
                dcc.Graph(id='grafico-pais')
            ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
            html.Div([
                dcc.Graph(id='grafico-sentimentos')
            ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        ], style={'display': 'flex', 'justifyContent': 'space-between'}),
    ], style={'padding': '20px'}),
], style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#f4f4f4'})

# Atualizando os gráficos com base na escolha do método de análise
@app.callback(
    [Output('grafico-ano', 'figure'),
     Output('grafico-idioma', 'figure'),
     Output('grafico-pais', 'figure'),
     Output('grafico-sentimentos', 'figure')],
    [Input('dropdown-analise', 'value')]
)
def atualizar_graficos(metodo_analise):
    # Aplicando a análise de sentimentos nos resumos dos artigos
    df_sentimentos = aplicar_analise_sentimentos(df, metodo=metodo_analise)

    # Adicionando os resultados da análise de sentimentos ao DataFrame original
    df['sentimento'] = df_sentimentos['sentimento']
    df['score'] = df_sentimentos['score']

    # Recriar os gráficos com base no novo método de análise
    grafico_ano = px.histogram(
        df,
        x="year",
        title="Distribuição de Artigos por Ano",
        labels={"year": "Ano", "count": "Quantidade de Artigos"},
        nbins=len(df['year'].unique())
    )

    grafico_idioma = px.bar(
        df["language"].value_counts().reset_index(),
        x="index",
        y="language",
        title="Distribuição de Artigos por Idioma",
        labels={"index": "Idioma", "language": "Quantidade"}
    )

    grafico_pais = px.pie(
        df,
        names="country_paper",
        title="Distribuição de Artigos por País",
        hole=0.4
    )

    grafico_sentimentos = px.histogram(
        df,
        x="sentimento",
        title="Análise de Sentimentos dos Artigos",
        labels={"sentimento": "Sentimento", "count": "Quantidade de Artigos"},
        nbins=len(df['sentimento'].unique())
    )

    # Retornar as figuras atualizadas
    return grafico_ano, grafico_idioma, grafico_pais, grafico_sentimentos
    # Converte os gráficos para HTML
    #grafico_ano_html = pio.to_html(grafico_ano, full_html=False)
    #grafico_idioma_html = pio.to_html(grafico_idioma, full_html=False)
    #grafico_pais_html = pio.to_html(grafico_pais, full_html=False)
    #grafico_sentimentos_html = pio.to_html(grafico_sentimentos, full_html=False)

    # Retorna os gráficos como HTML
    #return grafico_ano_html, grafico_idioma_html, grafico_pais_html, grafico_sentimentos_html

# Rodando o servidor Flask com Dash
if __name__ == '__main__':
    server.run(debug=True)
