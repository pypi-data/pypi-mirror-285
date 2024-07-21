"""
This Python script defines a CompanyDao class that provides an interface for interacting with a PostgreSQL database that stores company data. The class includes methods for executing generic SQL commands, retrieving all companies, getting a company’s UUID by its LinkedIn URL, checking if a company exists in the database by its LinkedIn URL, and inserting new company data into the database. The script uses environment variables for secure database connection and includes logging for tracking operations and errors. The CompanyDao class is initialized with no arguments, and each method within the class serves a specific purpose related to the manipulation and retrieval of company data from the database. The script is designed to be used as a data access object in a larger application where company data needs to be stored and retrieved.

"""
import os
import uuid
from dotenv import load_dotenv
import pandas as pd
import psycopg2
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CompanyDao:
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

    def get_all_companies(self):
        sql = "SELECT * FROM companies"
        return self.execute_db_command(sql)

    def getCompanyUuidByLinkedInUrl(self, companyLinkedinUrl):
        sql = "SELECT company_id FROM companies WHERE linkedin_url = %s"
        result = self.execute_db_command(sql, (companyLinkedinUrl,))
        
        if not result.empty:
            return result.iloc[0, 0]
        return None


    def doesCompanyExist(self, linkedInCompanyUrl):
        sql = "SELECT 1 FROM companies WHERE linkedin_url = %s"
        result = self.execute_db_command(sql, (linkedInCompanyUrl,))
        return len(result) > 0 if result is not None else False

    def insertCompany(self, companyDataFrame):
        sql = """
        INSERT INTO companies (
            company_id, company_name, company_website, linkedin_url, industry, 
            num_employees, ownership_type, about_webpage, careers_page, 
            home_page_summary, about_page_summary, linkedin_company_summary, 
            has_datascience, has_product_operations
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        row = companyDataFrame.iloc[0].apply(lambda x: str(x) if isinstance(x, uuid.UUID) else x)
        return self.execute_db_command(sql, tuple(row))

    def getCompanyNameByCompanyId(self, company_id):
        sql = "SELECT company_name FROM companies WHERE company_id = %s"
        result = self.execute_db_command(sql, (company_id,))
        if result is not None and not result.empty:
            return result.iloc[0]['company_name']
        else:
            logging.error(f"Error in getting Company Name. Failed for company id: {company_id}")
            return None