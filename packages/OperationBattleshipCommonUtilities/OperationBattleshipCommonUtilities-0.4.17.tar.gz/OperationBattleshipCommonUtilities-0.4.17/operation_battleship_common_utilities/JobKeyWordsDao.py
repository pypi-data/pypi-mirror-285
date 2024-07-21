"""
This script defines the JobKeyWordsDao class, which provides functionality for inserting job keywords into a database. The class uses the psycopg2 library to connect to a PostgreSQL database and execute SQL queries. It reads job keywords from a pandas DataFrame and inserts each record into the 'Job_Keywords' table in the database. The script uses environment variables to securely access database credentials. Logging is configured for tracking the execution of the script.
"""
import os
from datetime import datetime
import uuid
import logging
from dotenv import load_dotenv
import pandas as pd
import psycopg2

load_dotenv('.env')


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class JobKeyWordsDao :
    def __init__(self):
        logging.debug(f"{self.__class__.__name__} class initialized")


    def insertJobKeyWordsForJobPosting(self, jobKeyWordsDataFrame):
        """
        When given a dataframe that has multiple records, this function will insert each record into the DB. 
        """

        conn = psycopg2.connect(
            host=os.getenv("host"),
            database=os.getenv("database"),
            user=os.getenv("digitalOcean"),
            password=os.getenv("password"),
            port=os.getenv("port")
        )
        try:
            cur = conn.cursor()

            sql_insert_query = "INSERT INTO Job_Keywords (job_posting_id, unique_id, item) VALUES (%s, %s, %s)"

            for index, row in jobKeyWordsDataFrame.iterrows():

                # Convert UUID to string before insertion
                job_posting_id_str = str(row['job_posting_id'])
                unique_id_str = str(row['unique_id'])
                data = (job_posting_id_str, unique_id_str, row['item'])
                cur.execute(sql_insert_query, data)
                
            
            conn.commit()

            cur.close()
            conn.close()

            return "Update successful!"

        except Exception as e:
            logging.error("Database connection error:", e)
            conn.close()
            return None
        


    def getKeywordsForJobID(self, job_posting_id):

        """
        This function calls the Job Keywords Table to find all the records that have the given job_posting_id 
        
        Returns the list as a Pandas DataFrame
        """

        conn = psycopg2.connect(
            host=os.getenv("host"),
            database=os.getenv("database"),
            user=os.getenv("digitalOcean"),
            password=os.getenv("password"),
            port=os.getenv("port")
        )
        try:

            cur = conn.cursor()
            
            sql_select_query = "SELECT * FROM job_keywords WHERE job_posting_id = %s"
            cur.execute(sql_select_query, (job_posting_id,))  

            rows = cur.fetchall()

            if rows:
                df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])
            else:
                df = pd.DataFrame()

            cur.close()
            conn.close()

            return df

        except Exception as e:
            logging.error(f"Database connection error in getSkillsForJobID: {e}")
            conn.close()
            return pd.DataFrame()  
