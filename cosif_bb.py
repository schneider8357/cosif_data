import os
import zipfile
import io

import requests
import pandas as pd


def download_csv(ano, mes, cnpj):
    url = f"https://www3.bcb.gov.br/informes/rest/balanco//download/{ano}{mes:02d}-4010-{cnpj}.zip?cnpj={cnpj}&anoMes={ano}{mes:02d}"
    resp = requests.get(url, 
        headers={
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9,pt;q=0.8",
            "sec-ch-ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "iframe",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1"
        },
    )
    resp.raise_for_status()
    print(f"DEBUG {resp.status_code=}")
    print(f"DEBUG {url=}")
    z = zipfile.ZipFile(io.BytesIO(resp.content))
    z.extractall("cosif_bb_csvs")


def download_all_years(cnpj="00000000"):
    for ano in range(2000, 2023):
        for mes in range(1, 13):
            download_csv(ano, mes, cnpj)


def compara_headers():
    header_atual = None
    for filename in sorted(os.listdir("cosif_bb_csvs")):
        with open(f"cosif_bb_csvs/{filename}", encoding="iso-8859-9") as f:
            header = f.read().splitlines()[3]
            if not header:
                print(filename)
                raise Exception("Arquivo sem header")
            if header != header_atual:
                header_atual = header
                yield filename


def get_df(ano, mes, cnpj):
    df = pd.read_csv(f"cosif_bb_csvs/{ano}{mes:02d}-4010-{cnpj}.CSV", skiprows=3, encoding="iso-8859-9", sep=";")
    df = df.rename(columns=lambda x: x.strip())
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    if ano < 2010 or (ano == 2010 and mes < 10):
        return df.rename(columns={"DATA": "#DATA_BASE", "NOME CONTA": "NOME_CONTA", "NOME INSTITUICAO": "NOME_INSTITUICAO"})
    return df


if __name__ == "__main__":
    df_final = pd.DataFrame()
    for ano in range(2000, 2023):
        for mes in range(1, 13):
            df_final = pd.concat([df_final, get_df(ano, mes, "00000000")], ignore_index=True)
    df_final = df_final.loc[df_final["CONTA"] == 11100009]
    print(df_final)
    df_final.to_csv("df_final.csv")
