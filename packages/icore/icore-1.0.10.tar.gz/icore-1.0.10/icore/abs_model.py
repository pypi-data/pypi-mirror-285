import pandas as pd
from sqlalchemy import create_engine, text
import urllib
import logging
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
import mysql.connector
from mysql.connector import Error

from icore.db_config import *

logger = logging.getLogger("pandas_logger")


class abs_model:

    def __init__(self, conexao=None):

        self.conexao = conexao if conexao is not None else "db_illi"
        config = get_tipo(self.conexao)

        if config is False:
            print("Configure a conexao para ", self.conexao)
            return False

        connection_string = "mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}?charset=utf8mb4".format(
            username=config["user"],
            password=urllib.parse.quote_plus(config["password"]),
            host=config["host"],
            port=config["port"],
            database=config["database"],
        )

        try:
            self.connection = create_engine(connection_string)
        except SQLAlchemyError as e:
            logger.error(
                "Erro ao conectar no banco:",
                e,
                connection_string,
            )
        except Exception as e:
            logger.error(
                "Erro ao conectar no banco:",
                e,
                connection_string,
            )

    def query(self, sql):
        try:
            df = pd.read_sql(sql, self.connection)
            logger.info(f"{sql}")
            return df

        except SQLAlchemyError as e:
            logger.error("Erro ao executar a consulta SQL:", e)
        except Exception as e:
            logger.error("Erro ao executar a consulta SQL:", e)
        finally:
            self.connection.dispose()

    def exec(self, sql):
        try:
            config = get_tipo(self.conexao)
            connection = mysql.connector.connect(
                host=config["host"],
                database=config["database"],
                user=config["user"],
                port=config["port"],
                password=config["password"],
            )
            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute(sql)
                connection.commit()

        except Error as e:
            print(f"Error: '{e}'")

        finally:
            if connection.is_connected():
                connection.close()
                print(cursor)

    def salvar_df(self, df, tabela):
        try:
            df.to_sql(tabela, con=self.connection, if_exists="append", index=False)
            print(
                "DataFrame salvo com sucesso na tabela MySQL!", self.connection, tabela
            )
            self.connection.dispose()
            return True
        except Exception as e:
            logger.info(f"{tabela}", df.to_string())
            print("Erro ao salvar o DataFrame na tabela MySQL:", e)
            return False

    def get_connection(self, sql):
        return self.connection

    def get_data(self):
        return datetime.now()
