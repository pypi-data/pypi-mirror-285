import logging
import os
import time
from datetime import datetime
from dotenv import load_dotenv
import nomic.embed as embed
import nomic
from nomic import atlas
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv('.env')

class NomicAICaller:
    def __init__(self):
        logging.debug(f"{self.__class__.__name__} class initialized")
        self.nomicApiKey = os.getenv("NOMIC_API_KEY")
        
        if not self.nomicApiKey:
            logging.error("NOMIC_API_KEY is not set in the environment variables.")
            raise ValueError("NOMIC_API_KEY is required")
        
        nomic.login(self.nomicApiKey)

    def embedDocument(self, document):
        logging.debug("Embedding document")
        
        try:
            embeddedText = embed.text(
                texts=[document],
                model='nomic-embed-text-v1.5',
                task_type='search_document'
            )['embeddings']
        except Exception as e:
            logging.error(f"Error embedding document: {e}")
            raise

        return embeddedText
    
    def cleanDataF(self, df):
        """
        Nomic Atlas only accepts string data. This function converts all columns to strings and creates clean values for missing cells.
        """
        logging.debug("Cleaning DataFrame")

        if not isinstance(df, pd.DataFrame):
            logging.error("Input must be a pandas DataFrame")
            raise ValueError("Input must be a pandas DataFrame")

        # Convert all columns to string
        df = df.astype(str)
        
        # Replace null or empty values with "Null"
        df = df.fillna('Null')
        df.replace('', 'Null', inplace=True)

        logging.debug("DataFrame cleaned successfully")
        return df

    def createMap(self, df):
        logging.debug("Creating map")
        
        # Clean the data before using it
        df = self.cleanDataF(df)
        
        current_date = datetime.now().strftime("%B %d")
        mapTitle = f"{current_date} Jobs Map"
        description = "AI Powered Map to help you explore all jobs in the market."

        # Ensure df has the necessary columns
        required_columns = ['job_posting_id', 'full_posting_description']
        if not all(col in df.columns for col in required_columns):
            logging.error(f"DataFrame must contain the following columns: {required_columns}")
            raise ValueError(f"DataFrame must contain the following columns: {required_columns}")

        try:
            project = atlas.map_data(
                data=df,
                id_field='job_posting_id',
                indexed_field='full_posting_description',
                identifier=mapTitle,
                description=description,
                is_public=True
            )
        except Exception as e:
            logging.error(f"Error creating map: {e}")
            raise

        projection = project.maps[0]
        
        while True:
            status = projection._status
            logging.debug(f"Map creation task status: {status}")
            if status['index_build_stage'] == 'Done': 
                map_url = projection.map_link
                break
            elif status['index_build_stage'] == 'Failed':
                logging.error("Map creation task failed")
                raise Exception("Map creation task failed")
            time.sleep(30)

        logging.info(f"Map created successfully: {map_url}")
        return map_url