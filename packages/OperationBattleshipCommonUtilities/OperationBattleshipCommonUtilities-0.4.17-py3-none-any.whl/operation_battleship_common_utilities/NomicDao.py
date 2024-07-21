"""
This Python script is designed to interact with a PostgreSQL database to insert urls to the Nomic Table. It contains the NomicDao class, which has a method insertNomicMapUrl.

The insertNomicMapUrl method accepts a string which represents the URL that the Nomic Map is written at.

In case of any exceptions during the database operation, the method prints the error message and ensures the database connection is closed.

This script uses environment variables for sensitive data like the host, database name, user, password, and port, which should be stored in a .env file in the same directory. 
"""
import os
from datetime import datetime
import logging
from dotenv import load_dotenv
import psycopg2
import pandas as pd

load_dotenv('.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class NomicDao:
    def __init__(self):
        logging.debug(f"{self.__class__.__name__} class initialized")

    def _get_connection(self):
        return psycopg2.connect(
            host=os.getenv("host"),
            database=os.getenv("database"),
            user=os.getenv("digitalOcean"),
            password=os.getenv("password"),
            port=os.getenv("port")
        )

    def execute_db_command(self, sql_statement, data=None):
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute(sql_statement, data)
            if sql_statement.strip().lower().startswith("select"):
                result = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
            else:
                conn.commit()
                result = "Success"
            cur.close()
        except Exception as e:
            logging.error(f"Database error: {e}\nSQL Statement: {sql_statement}\nData: {data}")
            result = None
        finally:
            conn.close()
        return result

    def insertNomicMapUrl(self, url):
        """
        When given a url, insert this into the DB.
        """
        date = datetime.now()
        data = (date, url)
        sql_insert_query = "INSERT INTO nomic_map (insertion_date, url) VALUES (%s, %s)"
        return self.execute_db_command(sql_insert_query, data)

    def getLatestMapUrl(self):
        """
        Queries the nomic_map table and returns the url of the latest entry
        """
        sql_select_query = "SELECT url FROM nomic_map ORDER BY insertion_date DESC LIMIT 1"
        result = self.execute_db_command(sql_select_query)
        if result is not None and not result.empty:
            return result.iloc[0]['url']
        else:
            logging.error("Error in getting the latest map URL.")
            return None
