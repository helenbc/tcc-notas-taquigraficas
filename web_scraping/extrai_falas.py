import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep

def atualiza_nome_senador(nome_atual: str, texto_partido: str):
    if len(nome_atual.strip()) == 0:
        return "INDEFINIDO"
    
    if texto_partido == "INDEFINIDO":
        return nome_atual
    
    if "PRESIDENTE" in nome_atual:
        pessoa = texto_partido.split('.')[0]
        return f"{nome_atual.strip()} {pessoa.upper()}"

    return nome_atual



def adiciona_falas_de_reuniao(df_destino, url):
    sessao_id = url.split('/s/')[1]

    df = pd.DataFrame()

    def adiciona_ao_csv(id, nome, partido, fala):
        df2 = pd.DataFrame({
            'ID da Sessao': [id],
            'Nome_Senador': [nome.strip()], 
            'Partido': [partido.strip()], 
            'Fala': [fala.strip()]
        })
        return pd.concat([df, df2], ignore_index=True)

    response = requests.get(url)
    sleep(1)

    if response.status_code != 200:
        raise Exception('Não foi possível carregar a página')

    # Analisa o conteúdo HTML da página
    soup = BeautifulSoup(response.text, 'html.parser')

    # TODO: Antes de ler as linhas, salvar dados do cabeçalho da reunião

    # Encontra todas as linhas da tabela que contêm informações do deputado
    linhas_falas = soup.find_all('div', class_='principalStyle')

    ultimo_nome = ""
    ultimo_partido = ""
    fala = ""

    for linha in linhas_falas:
        nome = linha.find('b')

        if(nome is not None):
            # Salvando ultimo senador
            if ultimo_nome != "" and ultimo_partido != "":
                print('OBTENDO ', sessao_id, ultimo_nome, fala)
                df = adiciona_ao_csv(sessao_id, ultimo_nome, ultimo_partido, fala)

            ultimo_nome = nome.text
            fala = ""
            
            corpo_linha = linha.text.split(ultimo_nome)[1]

            separador = ') - '
            if separador in corpo_linha:
                partes_corpo = corpo_linha.split(') - ')

                ultimo_partido = partes_corpo[0].split('(')[1]
                fala += partes_corpo[1]
            else:
                ultimo_partido = "INDEFINIDO"
                fala += corpo_linha
            
            ultimo_nome = atualiza_nome_senador(ultimo_nome, ultimo_partido)
        else:
            fala += linha.text
    # Salvando ultimo senador
    df = adiciona_ao_csv(sessao_id, ultimo_nome, ultimo_partido, fala)

    return pd.concat([df_destino, df], ignore_index=True)



def main():
    urls_df = pd.read_csv('links_notas.csv')

    df = pd.DataFrame()
    for url in urls_df['Notas URL']:
        df = adiciona_falas_de_reuniao(df, url) # TODO: Tratar exceção caso url não for acessada
        df.to_csv('exemplo1.csv', index=False)


if __name__ == '__main__':
    main()
