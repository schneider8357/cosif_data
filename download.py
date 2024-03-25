import os
import zipfile
import io

import requests


def download_csv(ano, mes, extension="zip"):
    url = f"https://www.bcb.gov.br/content/estabilidadefinanceira/cosif/Bancos/{ano}{mes:02d}BANCOS.{extension}"
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
    if extension == "zip":
        z = zipfile.ZipFile(io.BytesIO(resp.content))
        z.extractall("cosif_csvs")
    else:
        with open(f"cosif_csvs/{ano}{mes:02d}BANCOS.CSV", "w") as f:
            f.write(resp.text)


def download_all_years():
    for ano in range(2000, 2023):
        for mes in range(1, 13):
            try:
                download_csv(ano, mes)
            except requests.exceptions.HTTPError:
                download_csv(ano, mes, "csv")


if __name__ == "__main__":
    os.makedirs("cosif_csvs")
    download_all_years()
