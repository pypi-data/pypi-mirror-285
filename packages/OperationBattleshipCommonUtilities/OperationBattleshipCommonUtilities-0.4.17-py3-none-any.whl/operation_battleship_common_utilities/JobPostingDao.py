import os
from datetime import datetime
import uuid
import logging
from dotenv import load_dotenv
import pandas as pd
import psycopg2

load_dotenv('.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class JobPostingDao:
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

    def getAllDataScienceOrProductCategorizedJobs(self):
        sql = "SELECT * FROM job_postings WHERE job_category IN ('Product_Management', 'Data_Science')"
        return self.execute_db_command(sql)

    def getAllProductManagerJobs(self):
        sql = "SELECT * FROM job_postings WHERE job_category = 'Product_Management'"
        return self.execute_db_command(sql)

    def updateLinkedInJobRecordUpdatedDate(self, jobUrl):
        sql = """
        UPDATE job_postings
        SET job_last_collected_date = %s
        WHERE posting_url = %s;
        """
        todaysDate = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
        data = (todaysDate, jobUrl)
        return self.execute_db_command(sql, data)

    def update_job_posting(self, job_posting):
        set_sql = ', '.join([f"{col} = %s" for col in job_posting.index if col != 'job_posting_id'])
        sql = f"""
        UPDATE job_postings
        SET {set_sql}
        WHERE job_posting_id = %s;
        """
        data = tuple(job_posting[col] for col in job_posting.index if col != 'job_posting_id') + (job_posting['job_posting_id'],)
        return self.execute_db_command(sql, data)

    def fetchPmJobsRequiringEnrichment(self):
        sql = "SELECT * FROM job_postings WHERE (job_title ILIKE '%AI%' OR job_title ILIKE '%Product Manager%') AND is_ai IS NULL ORDER BY job_posting_date DESC"
        return self.execute_db_command(sql)

    def fetchJobsRequiringEnrichment(self):
        sql = """
        SELECT * FROM job_postings 
        WHERE is_ai IS NULL 
        AND job_posting_date >= CURRENT_DATE - INTERVAL '30 days'
        """
        return self.execute_db_command(sql)


    def checkIfJobExists(self, cleanedLinkedInJobURL):
        sql = "SELECT * FROM job_postings WHERE posting_url = %s"
        result = self.execute_db_command(sql, (cleanedLinkedInJobURL,))
        return len(result) > 0 if result is not None else False

    def insertNewJobRecord(self, jobpostingDataFrame):
        sql = """
        INSERT INTO job_postings (
            job_posting_id, company_id, posting_url, posting_source, posting_source_id, job_title,
            full_posting_description, job_description, is_ai, job_salary, job_posting_company_information, 
            job_posting_date, job_insertion_date, job_last_collected_date, job_active, city, state
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        # Extract the first row from the DataFrame as a dictionary
        row_dict = jobpostingDataFrame.iloc[0].to_dict()
        
        # Convert the dictionary values to a tuple
        row = tuple(row_dict.values())
        
        return self.execute_db_command(sql, row)


    def getAllJobs(self):
        sql = "SELECT * FROM job_postings"
        return self.execute_db_command(sql)

    def getActiveJobsIdsAsDataFrame(self):
        sql = "SELECT * FROM job_postings WHERE job_active = TRUE"
        return self.execute_db_command(sql)

    def getJobByJobPostingId(self, job_posting_id):
        sql = "SELECT * FROM job_postings WHERE job_posting_id = %s"
        return self.execute_db_command(sql, (job_posting_id,))

    def getUncategorizedJobs(self):
        sql = "SELECT * FROM job_postings WHERE job_category IS NULL"
        return self.execute_db_command(sql)

    def getjobsFromListOfJobsIds(self, dataframeOfJobIds):
        job_ids_tuple = tuple(dataframeOfJobIds['job_posting_id'].tolist())
        sql = """
        SELECT
            c.company_name,
            c.linkedin_url,
            jp.job_title,
            jp.posting_url,
            jp.full_posting_description,
            jp.job_description,
            jp.is_ai,
            jp.is_genai,
            jp.salary_low,
            jp.salary_midpoint,
            jp.salary_high,
            jp.job_salary,
            jp.job_category,
            jp.job_posting_date,
            jp.job_posting_id AS job_posting_id,
            jp.company_id,
            jp.posting_source,
            jp.posting_source_id,
            jp.job_posting_company_information,
            jp.job_insertion_date,
            jp.job_last_collected_date,
            jp.job_active,
            jp.city,
            jp.state,
            jp.job_skills,
            jp.is_ai_justification,
            jp.work_location_type
        FROM
            job_postings jp
        JOIN
            companies c ON jp.company_id = c.company_id
        WHERE
            jp.job_posting_id IN %s;
        """
        return self.execute_db_command(sql, (job_ids_tuple,))