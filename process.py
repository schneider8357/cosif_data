import os

import pandas as pd


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


def get_df(ano, mes, cnpj=None) -> pd.DataFrame:
    df = pd.read_csv(f"cosif_csvs/{ano}{mes:02d}BANCOS.CSV", skiprows=3, encoding="iso-8859-9", sep=";")
    if cnpj is not None:
        df = df[df["CNPJ"] == int(cnpj)]
    df = df.rename(columns=lambda x: x.strip())
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    df["SALDO"] = df["SALDO"].str.replace(",", ".").astype(float)
    # print(df)
    if ano < 2010 or (ano == 2010 and mes < 10):
        return df.rename(columns={"DATA": "#DATA_BASE", "NOME CONTA": "NOME_CONTA", "NOME INSTITUICAO": "NOME_INSTITUICAO"})
    return df


def tratamento_base(ano_inicio, ano_fim):
    """Efetua um merge de todos os csvs mantendo as colunas #DATA_BASE, CNPJ, CONTA e SALDO."""
    df_base = pd.DataFrame()
    for ano in range(ano_inicio, ano_fim):
        for mes in range(1, 13):
            print(f"processing file {ano}{mes}, mem consumption: {df_base.memory_usage().sum()}")
            df_mes = get_df(ano, mes)
            df_mes.drop(columns=["NOME_INSTITUICAO","DOCUMENTO","NOME_CONTA"],inplace=True)
            for col in ["AGENCIA","COD_CONGL","NOME_CONGL","TAXONOMIA","ATRIBUTO","REALIZAVEL ATE 3M","REALIZAVEL APOS 3M"]:
                try:
                    df_mes.drop(columns=[col],inplace=True)
                except KeyError:
                    pass
            # print(df_mes)
            df_base = pd.concat([df_base, df_mes], ignore_index=True)
    return df_base


if __name__ == "__main__":
    # df_final = pd.DataFrame()
    # for ano in range(2004, 2024):
    #     for mes in range(1, 13):
    #         df_final = pd.concat([df_final, get_df(ano, mes, "00000000")], ignore_index=True)
    # # df_final = df_final.loc[df_final["CONTA"] == 11100009]
    # print(df_final)
    # df_final.to_csv("df_final_bb.csv")
    tratamento_base(2004, 2024)
