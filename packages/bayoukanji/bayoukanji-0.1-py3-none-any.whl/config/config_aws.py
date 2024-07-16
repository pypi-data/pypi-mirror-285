import boto3
import pandas as pd
import s3fs
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import pyarrow.parquet as pq
import json

class aws:
    def __init__(self, region_name, bucket_name):
        self.region_name = region_name
        self.bucket_name = bucket_name
        self.s3_client = self._create_s3_client()

    def _create_s3_client(self):
        try:
            s3_client = boto3.client('s3', region_name=self.region_name)
            return s3_client
        except (NoCredentialsError, PartialCredentialsError) as e:
            print(f"Error in credentials: {e}")
            return None

    def read_csv_file(self, file, delimiter):
        try:
            obj = self.s3_client.get_object(Bucket=self.bucket_name, Key=file)
            data = obj['Body'].read().decode('utf-8')
            df = pd.read_csv(StringIO(data), header=0, delimiter=delimiter)
            return df
        except Exception as e:
            print(f"Error reading file: {e}")
            return None

    def read_parquet_file(self, file):
        try:
            # Verifica se o caminho começa com 's3://'
            if not file.startswith('s3://'):
                file = f's3://{self.bucket_name}/{file}'
            # Lê o arquivo Parquet usando o s3fs e pyarrow
            df = pq.read_table(file, filesystem=self.s3fs).to_pandas()
            return df
        except Exception as e:
            print(f"Error reading Parquet file: {e}")
            return None

    def read_parquet_folder(self, folder_path):
        try:
            # Caminho completo no S3
            s3_path = f"s3://{self.bucket_name}/{folder_path}"

            # Listar todos os arquivos na pasta e subpastas
            parquet_files = []
            for dirpath, dirnames, filenames in self.s3fs.walk(s3_path):
                for filename in filenames:
                    if filename.endswith('.parquet'):
                        parquet_files.append(f"{dirpath}/{filename}")

            # Verificar se encontrou arquivos Parquet
            if not parquet_files:
                raise FileNotFoundError(f"No Parquet files found in path: {s3_path}")

            # Ler todos os arquivos Parquet encontrados
            df_list = [pd.read_parquet(f"s3://{file}", filesystem=self.s3fs, engine='pyarrow') for file in parquet_files]

            # Concatenar todos os dataframes em um único dataframe
            df = pd.concat(df_list, ignore_index=True)

            return df
        except Exception as e:
            print(f"Error reading Parquet folder: {e}")
            return None
