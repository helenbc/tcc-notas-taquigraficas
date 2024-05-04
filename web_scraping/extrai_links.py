from typing import Optional
import pandas as pd
import requests
from bs4 import BeautifulSoup
from time import sleep

URL_PRIMEIRA_SESSAO = "https://www25.senado.leg.br/web/atividade/sessao-plenaria/-/pauta/25341"

def obter_notas(df: pd.DataFrame, sessao_url: str) -> tuple[pd.DataFrame, Optional[str]]:
    proxima_url = None

    response = requests.get(sessao_url)

    if response.status_code != 200:
        raise Exception('Não foi possível carregar a página')

    # Analisa o conteúdo HTML da página
    soup = BeautifulSoup(response.text, 'html.parser')


    data = soup.find('div', class_="painel-cabecalho").find('span')

    if '2024' in data.text:
        return df, None

    notas_url = soup.find('div', id="conteudoSessao").find('div', class_="botoes row-fluid").find('a')
    proxima_sessao = soup.find('div', id="pauta").find('div').find('div').find('div', class_="row-fluid sf-sessao--barra-navegacao").find('div').find('a', class_="pull-right")

    print(f'OBTENDO SESSÃO DE {data.text}...')
    sleep(1)

    novo_df = pd.DataFrame({
        'Data': [data.text],
        'Notas URL': [notas_url.attrs['href']]
    })

    return pd.concat([df, novo_df], ignore_index=True), proxima_sessao.attrs['href']

def main():
    df = pd.DataFrame()
    proxima_url = URL_PRIMEIRA_SESSAO

    while proxima_url:
        df, proxima_url = obter_notas(df, proxima_url)
    
    df.to_csv('links_notas.csv', index=False)


if __name__ == '__main__':
    main()