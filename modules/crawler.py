from bs4 import BeautifulSoup
from urllib.parse import quote
import json
from requests_html import HTMLSession
import requests
DOMAIN = 'https://www.periodicos.capes.gov.br'

def get_soup(url):
    # session = HTMLSession()
    # response = session.get(url)
    # response.html.render(timeout=30)
    # response = response.html.html
    response = requests.get(url, timeout=30).text
    # print(response)
    return BeautifulSoup(response, 'html.parser')

def get_text(bs4_element):
    if bs4_element:
        return bs4_element.text.strip()
    return None

def scraping(url):
    soup = get_soup(url)
    source_url_paper = soup.find('a', attrs={'id':'item-acessar'}).get('href')
    # print(source_url_paper)
    if source_url_paper.startswith('/index.php') :
        page = get_soup(DOMAIN + source_url_paper)
    else:
        page = get_soup(source_url_paper)
    paper_title = soup.find('h5', attrs={'id':'item-titulo'})
    paper_title = get_text(paper_title)
    type_publication = soup.find('strong', attrs={'id':'type-publicacao'})
    type_publication = get_text(type_publication)
    revisor = soup.find('span', attrs={'class':'ml-2'})
    if revisor:
        revisor = revisor.text.replace('Revisado por','').strip()
    country_paper_image = soup.find('img', attrs={'src':'/images/flag-brazil.png'})
    if country_paper_image:
        country_paper = 'Brasil'
    else:
        country_paper = 'Estrangeiro'
    div_open_acess = soup.find('span', attrs={'class':'open-acess ml-2'})
    if div_open_acess:
        open_access = True
    else:
        open_access = False
    year = soup.find('strong', attrs={'id':'item-ano'})
    if year:
        year = year.text.strip()
    instituto = soup.find('strong', attrs={'id':'item-instituicao'})
    if instituto:
        instituto = instituto.text.strip().replace(';','')
    volume = soup.find('strong', attrs={'id':'item-volume'})
    if volume:
        volume = volume.text.replace(';','').replace('Volume:','').strip()
    issue = soup.find('strong', attrs={'id':'item-issue'})
    if issue:
        issue = issue.text.replace(';','').replace('Issue:','').strip()
    language = soup.find('strong', attrs={'id':'item-language'})
    if language:
        language = language.text.replace('Linguagem:', '').strip()
    doi = soup.find('p', attrs={'class':'small text-muted mb-3 block'})
    doi = get_text(doi)
    issn = soup.find('p', attrs={'class':'text-muted mb-3 block'})
    issn = get_text(issn)
    authors = soup.find('p', attrs={'id':'item-autores'})
    if authors:
        authors = authors.text.strip().split(',')
        authors = [author.strip() for author in authors]
    topics = soup.find_all('p', attrs={'id':'item-autores'})
    if topics:
        topics = topics[1].text.strip()
    resume = soup.find('p', attrs={'id':'item-resumo'})
    resume = get_text(resume)
    cited_by = soup.find('div', attrs={'id':'cited-by'})
    if cited_by:
        cites = cited_by.find_all('a', attrs={'class':'titulo-cited-by text-justify'})
        cited_by = [cite.text.strip() for cite in cites]
    paper =  {
        'title':paper_title,
        'source_url_paper':source_url_paper,
        'type_publication':type_publication,
        'revisor':revisor,
        'country_paper':country_paper,
        'open_access':open_access,
        'year':year,
        'instituto':instituto,
        'volume':volume,
        'issue':issue,
        'language':language,
        'doi':doi,
        'issn':issn,
        'authors':authors,
        'topics':topics,
        'resume':resume,
        'cited_by':cited_by,
    }
    # for key, value in paper.items():
        # print(f'{value}:{type(value)}')
    with open('paper.json', 'w') as file:
        json.dump(paper, file, indent=4, ensure_ascii=False)
    return paper

def search_by_title(title):
    papers = []
    base_url = 'https://www.periodicos.capes.gov.br/index.php/acervo/buscador.html?q='
    title = title.strip().split(' ')
    title = '+'.join(title)
    base_url += title
    soup = get_soup(base_url)
    results = soup.find('div', attrs={'id':'resultados'})
    results_divs = results.find_all('div', class_='row')
    for div in results_divs:
        if 'Acesso aberto' in div.text:
            paper_url = div.find('a', attrs={'class':'titulo-busca'})
            if paper_url is None:
                continue
            # print(DOMAIN + paper_url.get('href'))
            paper = scraping(DOMAIN + paper_url.get('href'))
            papers.append(paper)
    return papers

if __name__ == '__main__':
    search_by_title('RepositORE Sebastião Alves')
    # crawl('https://www.periodicos.capes.gov.br/index.php/acervo/buscador.html?q=RepositORE+Sebasti%C3%A3o+Alves')