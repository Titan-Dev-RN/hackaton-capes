from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session
from modules.crawler import search_by_title, scraping_done  # Importa a função do arquivo crawler.py
from graphics import server  
import os
import json

app = server  # Usa o servidor Flask compartilhado do Dash

app.secret_key = 'secret_key'  # Necessário para usar sessões

# HTML com CSS embutido
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pesquisa de Artigos</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }

        .container {
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            padding: 20px;
            width: 90%;
            max-width: 400px;
            text-align: center;
        }

        h1 {
            font-size: 24px;
            color: #333333;
            margin-bottom: 20px;
        }

        input[type="text"] {
            width: 100%;
            padding: 15px;
            font-size: 16px;
            border: 1px solid #ccc;
            border-radius: 8px;
            box-sizing: border-box;
            transition: border-color 0.3s ease;
        }

        input[type="text"]:focus {
            border-color: #007bff;
            outline: none;
            box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
        }

        button {
            width: 100%;
            padding: 15px;
            font-size: 16px;
            background-color: #007bff;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 10px;
            transition: background-color 0.3s ease;
        }

        button:hover {
            background-color: #0056b3;
        }

        .results {
            margin-top: 20px;
            text-align: left;
        }

        .results h2 {
            font-size: 20px;
            color: #007bff;
        }

        .results p {
            font-size: 16px;
            color: #333333;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Pesquisa de Artigos</h1>
        <form id="search-form">
            <input type="text" id="title-input" name="title" placeholder="Digite o título do artigo...">
            <button type="submit">Pesquisar</button>
        </form>
        <div class="results" id="results"></div>
    </div>

    <script>
        const searchForm = document.getElementById("search-form");
        const titleInput = document.getElementById("title-input");
        const submitButton = searchForm.querySelector("button");

        searchForm.addEventListener("submit", function (event) {
            event.preventDefault(); // Evita o envio padrão do formulário

            const title = titleInput.value;

            if (title.trim()) {
                // Desativa o botão e exibe mensagem
                submitButton.disabled = true;
                submitButton.textContent = "Fazendo a requisição...";

                fetch('/search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ title: title })
                })
                .then(response => {
                    if (response.redirected) {
                        window.location.href = response.url; // Redireciona para a URL de gráficos
                    } else {
                        throw new Error("Falha ao redirecionar.");
                    }
                })
                .finally(() => {
                    // Habilita o botão novamente
                    submitButton.disabled = false;
                    submitButton.textContent = "Pesquisar";
                });
            } else {
                alert("Por favor, insira um título para pesquisar.");
            }
        });
    </script>

</body>
</html>
"""

@app.route('/')
def redirect_to_search():
    # Redireciona para a página de pesquisa de artigos ao acessar a raiz
    return redirect(url_for('home'))

@app.route('/search')
def home():
    return render_template_string(HTML_TEMPLATE)


@app.route('/search', methods=['POST'])
def search():
    data = request.json
    title = data.get("title", "")

    # Inicia o scraping e obtém o ID do arquivo
    #papers = search_by_title(title)
    search_by_title(title)


    # Caminho completo para o arquivo 'papers.json' na pasta 'scraping_results'
    file_path = os.path.join('scraping_results', 'papers.json')
    # Armazena o ID do arquivo na sessão
    session['results_file_id'] = file_path

        # Redireciona para a página de gráficos
    return redirect(url_for('show_graphs'))
    #else:
       # return jsonify({"error": "O scraping ainda não foi concluído. Tente novamente mais tarde."}), 503



@app.route('/graphics')
def show_graphs():
    # Obtém o ID do arquivo armazenado na sessão
    file_path = session.get('results_file_id')

    if not file_path:
        return "Nenhum dado encontrado! Inicie o scraping.", 400

    # Caminho fixo para o arquivo de resultados
    #file_path = os.path.join('scraping_results', file_id)

    # Verifica se o arquivo existe
    if not os.path.exists(file_path):
        return "Arquivo de resultados não encontrado! Tente novamente mais tarde.", 404

    # Lê os resultados do arquivo
    with open(file_path, 'r', encoding='utf-8') as file:
        results = json.load(file)

    if not results:
        return "Nenhum resultado encontrado no arquivo!", 404

    # Redireciona para o painel de gráficos
    return redirect('/graphics/')    
   

if __name__ == '__main__':
    app.run(debug=True)
     # Usando a variável de ambiente 'PORT' fornecida pelo Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
