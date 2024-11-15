import asyncio
from urllib.parse import quote
import httpx

async def req(term, prompt):
    url = quote(f'{term}&{prompt}')
    url = 'http://localhost:8080/search/' + url
    print(f"Requisitando URL: {url}")
    try:
        async with httpx.AsyncClient(timeout=40) as client:  # Define o timeout de 10 segundos
            response = await client.get(url)
            print("Resposta recebida:", response.text)
    except httpx.ReadTimeout:
        print("Erro: a requisição excedeu o tempo limite.")

if __name__ == '__main__':
    asyncio.run(req('Sebastião Alves RepositORE', 'Quais os assuntos dos artigos?'))
