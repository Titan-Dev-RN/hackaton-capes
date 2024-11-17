from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session
from modules import search_by_title  # Importa a função do arquivo crawler.py
from graphics import server  

app = server  # Usa o servidor Flask compartilhado do Dash

#app.secret_key = 'secret_key'  # Necessário para usar sessões

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
                .catch(error => {
                    console.error("Erro na requisição:", error);
                    alert("Ocorreu um erro na requisição. Tente novamente.");
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
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    title = data.get("title", "")
    results = search_by_title(title)
    #return jsonify(results)

    # Armazena os resultados na sessão
    session['results'] = results

    # Redireciona para a página de gráficos
    return redirect(url_for('show_graphs'))


@app.route('/graphics')
def show_graphs():
    # Obtém os resultados armazenados na sessão
    results = session.get('results', [])
    
    if not results:
        return "Nenhum dado encontrado!", 400

    # Crie e retorne os gráficos (você pode adicionar a lógica de visualização aqui)
    #return f"Gráficos gerados com {len(results)} resultados!"
    #return atualizar_graficos('simples')
    # Redireciona para o painel do Dash
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
