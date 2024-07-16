import requests
from datetime import datetime
from io import BytesIO
import s3fs
import pandas as pd

class extract_api:
    def __init__(self, aws_instance):
        self.aws = aws_instance
        # Atualização: Uso do s3fs com autenticação automática
        self.s3fs = s3fs.S3FileSystem(client_kwargs={'region_name': self.aws.region_name})

    def upload_s3(self, path, df):
        # Adiciona uma coluna com a data e hora atuais
        df['timestamp'] = pd.to_datetime('now').strftime('%Y-%m-%d %H:%M:%S')

        # Verifica se o caminho começa com 's3://'
        if not path.startswith('s3://'):
            raise ValueError("O caminho deve começar com 's3://'")

        # Salva o DataFrame como um arquivo Parquet particionado pela coluna 'timestamp'
        df.to_parquet(path, engine='pyarrow', compression='snappy', filesystem=self.s3fs, partition_cols=['timestamp'])
