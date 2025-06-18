import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import cx_Oracle
from datetime import date, datetime

load_dotenv()
cx_Oracle.init_oracle_client(lib_dir=r"C:\oracle\Client\x64\instantclient_19_14")
connection_string = (
    f"oracle+cx_oracle://{os.getenv('ORACLE_USER')}:{os.getenv('ORACLE_PASSWORD')}"
    f"@{os.getenv('ORACLE_HOST')}:{os.getenv('ORACLE_PORT')}/?service_name={os.getenv('ORACLE_SERVICE')}"
)
engine = create_engine(connection_string)
def fetch_log_details(start_date, end_date, text_to_search=None, output_path="log_details.json"):
    query = """
        SELECT ld.ID as LOG_DETAIL_ID, ld.LOG_DATE, ld.PROD_DATE, ld.SHIFT, ld.USERID, ld.LOG_TEXT, s.MFGNO, SUBSTR(s.MFGNO, 1, INSTR(s.MFGNO, ' ') - 1) AS JOBNO, wc.EQNO
        FROM IQMS.MACHLOG ml LEFT OUTER JOIN IQMS.LOG_DETAIL ld ON (ml.ID = MACHLOG_ID) LEFT OUTER JOIN IQMS.STANDARD s ON (s.ID = ml.STANDARD_ID) LEFT OUTER JOIN IQMS.WORK_CENTER wc ON (wc.ID = ml.WORK_CENTER_ID)
        WHERE
            ld.PROD_DATE BETWEEN :start_date AND :end_date
            AND (
                :text_to_search IS NULL OR
                UPPER(ld.LOG_TEXT) LIKE '%' || UPPER(:text_to_search) || '%'
            )
    """

    sql=text(query)

    with engine.connect() as conn:
        df = pd.read_sql(sql, conn, params={
            "start_date": start_date,
            "end_date": end_date,
            "text_to_search": text_to_search
        })

    df.to_json(output_path, orient="records", lines=True)
    # print(df[["prod_date", "log_date"]].head(10))
    # print(df.dtypes)
    print(f"Successfully exported {len(df)} records to {output_path}")
    print(df.head(3).to_string(index=False))


if __name__ == "__main__":
    today = date.today()
    start_date = today.replace(day=1) # first of the month
    end_date = today
    text_to_search = ""

    fetch_log_details(
    start_date,
    end_date,
    text_to_search
)
