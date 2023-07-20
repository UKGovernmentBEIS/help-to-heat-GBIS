import requests
import os
import re
import zipfile
import pandas as pd

gov_epc_url = "https://statistics.gov.scot/data/domestic-energy-performance-certificates"
zip_file_path = os.path.join("data", "epc.zip")
csv_file_path = os.path.join("data", "epc.csv")
extract_path = os.path.join("data", "epc")
download_url_regex = r"https://statistics.gov.scot/downloads/file\?id=[^ ]+.zip"

db_connection_string = (
    "postgresql+psycopg2://username:password@host:port/database"  # placeholder until this is implemented
)
table_name = "scottish_epc"  # placeholder until this is implemented
tempt_table_name = "scottish_epc_temp"  # placeholder until this is implemented


def download(url: str, save_path: str, chunk_size: int = 128):
    print(f"Downloading {url} to: {save_path}")
    r = requests.get(url, stream=True)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "wb") as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)


def unzip(zip_file_path: str, extract_path: str):
    os.makedirs(extract_path, exist_ok=True)
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)


def load_data(data_path: str) -> pd.DataFrame:
    dfs = []
    for file in os.listdir(data_path):
        if file.endswith(".csv"):
            file_path = os.path.join(data_path, file)
            df = pd.read_csv(
                file_path,
                header=0,
                skiprows=[1],
                dtype=str,
                parse_dates=["LODGEMENT_DATE"],
                usecols=["OSG_REFERENCE_NUMBER", "CURRENT_ENERGY_RATING", "LODGEMENT_DATE"],
            )
            df = df.rename(
                columns={
                    "OSG_REFERENCE_NUMBER": "uprn",
                    "CURRENT_ENERGY_RATING": "epc_rating",
                    "LODGEMENT_DATE": "date",
                }
            )
            df.drop_duplicates(subset=["uprn"], keep="last", inplace=True)
            df.dropna(inplace=True, subset=["uprn"])
            df.set_index("uprn", inplace=True)
            dfs.append(df)
    return pd.concat(dfs)


def load_data_sql(df: pd.DataFrame):
    # TODO: add to database
    # https://stackoverflow.com/questions/23103962/how-to-write-dataframe-to-postgres-table
    # 1. create temp table
    # 2. copy data to temp table
    # 3. In one transaction: rename main table to drop_table, rename temp table to main table
    # 4. drop drop_table

    pass


def main():
    gov_epc_response = requests.get(gov_epc_url).text
    try:
        download_url = re.search(download_url_regex, gov_epc_response).group(0)
    except AttributeError:
        raise ("No download URL found")

    download(download_url, "data/epc.zip")
    unzip(zip_file_path, extract_path)
    df = load_data(extract_path)
    df.to_csv(csv_file_path, index="uprn")

    load_data_sql(df)  # TODO: add to database


if __name__ == "__main__":
    main()
