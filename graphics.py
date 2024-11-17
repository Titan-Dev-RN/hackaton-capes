import json
import pandas as pd
import plotly.express as px
from textblob import TextBlob
from transformers import pipeline
from flask import Flask, session, redirect, url_for
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.io as pio
import os

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

# Inicializando o servidor Flask
server = Flask(__name__)

# Inicializando o Dash com Flask
app = dash.Dash(__name__, server=server, url_base_pathname='/graphics/')

# Função para carregar o JSON
def carregar_dados_json():
    file_path = os.path.join('scraping_results', 'papers.json')
    with open(file_path, 'r', encoding='utf-8') as file:
        dados_json = json.load(file)
    return pd.json_normalize(dados_json)

# Layout redesenhado
app.layout = html.Div([
    # Componente dcc.Location para controle de URL
    dcc.Location(id='url', refresh=True),  
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
            html.Div([dcc.Graph(id='grafico-ano')], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
            html.Div([dcc.Graph(id='grafico-idioma')], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        ], style={'display': 'flex', 'justifyContent': 'space-between'}),

        # Linha 2: Gráficos lado a lado
        html.Div([
            html.Div([dcc.Graph(id='grafico-pais')], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
            html.Div([dcc.Graph(id='grafico-sentimentos')], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        ], style={'display': 'flex', 'justifyContent': 'space-between'}),

        # Linha 3: Novos gráficos
        html.Div([
            html.Div([dcc.Graph(id='grafico-sentimentos-por-pais')], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
            html.Div([dcc.Graph(id='grafico_ano_artigos')], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        ], style={'display': 'flex', 'justifyContent': 'space-between'}),
    ], style={'padding': '20px'}),

    # Botão para voltar e recarregar o novo JSON
    html.Div([  
        html.Button("Voltar para Pesquisa", id="voltar-btn", n_clicks=0, style={  
            'padding': '10px 20px',  
            'fontSize': '16px',  
            'backgroundColor': '#1f2c56',  
            'color': '#ffffff',  
            'border': 'none',  
            'cursor': 'pointer',  
            'borderRadius': '5px',  
            'marginTop': '20px',  
            'display': 'block',  
            'margin': '20px auto'  
        })  
    ])  
], style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#f4f4f4'})

@app.callback(
    Output('url', 'pathname'),
    [Input('voltar-btn', 'n_clicks')]
)
def voltar_para_pesquisa(n_clicks):
    if n_clicks > 0:
        # Limpa os dados da sessão (se necessário)
        session.clear()
        return '/search'  # Redireciona para a página de pesquisa
    return dash.no_update

# Atualizando os gráficos com base na escolha do método de análise
@app.callback(
    [Output('grafico-ano', 'figure'),
     Output('grafico-idioma', 'figure'),
     Output('grafico-pais', 'figure'),
     Output('grafico-sentimentos', 'figure'),
     Output('grafico-sentimentos-por-pais', 'figure'),
     Output('grafico_ano_artigos', 'figure')],
    [Input('dropdown-analise', 'value')]
)
def atualizar_graficos(metodo_analise):
    df = carregar_dados_json()
    if df.empty:
        print("Nenhum dado encontrado para gerar os gráficos")
        return dash.no_update

    # Aplicando a análise de sentimentos nos resumos dos artigos
    df_sentimentos = aplicar_analise_sentimentos(df, metodo=metodo_analise)

    # Adicionando os resultados da análise de sentimentos ao DataFrame original
    df['sentimento'] = df_sentimentos['sentimento']
    df['score'] = df_sentimentos['score']

    # Gráfico de número de artigos por ano
    grafico_ano = px.histogram(
        df,
        x="year",
        title="Distribuição de Artigos por Ano",
        labels={"year": "Ano", "count": "Quantidade de Artigos"},
        nbins=len(df['year'].unique())
    )

    # Gráfico de idiomas
    grafico_idioma = px.bar(
        df["language"].value_counts().reset_index(),
        x="index",
        y="language",
        title="Distribuição de Artigos por Idioma",
        labels={"index": "Idioma", "language": "Quantidade"}
    )

    # Gráfico de países
    grafico_pais = px.pie(
        df,
        names="country_paper",
        title="Distribuição de Artigos por País",
        hole=0.4
    )

    # Gráfico de sentimentos
    grafico_sentimentos = px.pie(
        df,
        names="sentimento",
        title="Distribuição de Sentimentos",
        hole=0.4
    )

    # Gráfico de sentimentos por país
    grafico_sentimentos_por_pais = px.sunburst(
        df,
        path=["country_paper", "sentimento"],
        title="Sentimentos por País"
    )

    # Retornando os gráficos
    return grafico_ano, grafico_idioma, grafico_pais, grafico_sentimentos, grafico_sentimentos_por_pais, grafico_ano


# Rodando o servidor
if __name__ == '__main__':
    app.run_server(debug=True)
