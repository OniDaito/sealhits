r"""
  ______  ______  ____    ____    __   _  ____    __   ______  
 |   ___||   ___||    \  |    |  |  |_| ||    | _|  |_|   ___| 
  `-.`-. |   ___||     \ |    |_ |   _  ||    ||_    _|`-.`-.  
 |______||______||__|\__\|______||__| |_||____|  |__| |______|

conftest.py - configure the tests - do the setup.
author: Benjamin Blundell (bjb8@st-andrews.ac.uk)

Configuration for the pytest tests.
"""

import pytest
import os
import psycopg
from sealhits.db.db import DB


@pytest.fixture(scope="session")
def get_data(request):
    """ See if we can connect to postgres. If we can, see if the testseals database
    already exists. If it doesn't, create it.
    TODO - eventually, we will always create it as the data may have changed. """
    test_dir = os.path.dirname(os.path.realpath(__file__))
    test_data_dir = os.path.join(test_dir, "sealhits_testdata")
    
    if not os.path.exists(test_data_dir):
        # Download data to test_data_dir via pooch
        import pooch

        test_data = pooch.retrieve(
            url="https://zenodo.org/records/12518315/files/sealhits_test_data.zip?download=1",
            known_hash="md5:e288a2968a731cf48e001927f276b71f",
        )
        
        import zipfile
        
        with zipfile.ZipFile(test_data, 'r') as zip_ref:
            zip_ref.extractall(test_dir)
  
    pg_conn = None

    pg_username = "postgres"
    pg_password = "postgres"

    try:
        pg_username = os.environ['SEALHITS_TESTDATA_PGUSER']
        pg_password = os.environ['SEALHITS_TESTDATA_PGPASS']
    except KeyError:
        print("No environment variables set for SEALHITS_TESTDATA_PGUSER and SEALHITS_TESTDATA_PGPASS. Using default postgres.")

    if pg_username is None or pg_username == "":
        pg_username = "postgres"
    
    if pg_password is None or pg_password == "":
        pg_password = "postgres"

    try:
        # In PostgreSQL, default username is 'postgres' and password is 'postgres'.
        # And also there is a default database exist named as 'postgres'.
        # Default host is 'localhost' or '127.0.0.1'
        # And default port is '54322'.
        pg_conn = psycopg.connect("user='" + pg_username + "' host='localhost' password='" + pg_password + "' port='5432'")
        print('Database connected.')

    except Exception as e:
        print('Database not connected.')
        print(e)
        assert(False)
    
    if pg_conn is not None:
        pg_conn.autocommit = True
        cur = pg_conn.cursor()

        try:
            cur.execute("CREATE USER testseals WITH PASSWORD 'testseals';")
        except Exception as e:
            # Naughty but at least it's there
            print(e)
            pass

        cur.execute("SELECT datname FROM pg_database;")

        list_database = cur.fetchall()
        list_database = [list_db[0] for list_db in list_database]

        # TODO - out for now as we need to fix the sql now we've changed the uuids
        if "testseals" not in list_database:
            cursor = pg_conn.cursor()
            cursor.execute("CREATE DATABASE testseals WITH OWNER testseals TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'C.UTF-8'")
            try:
                ts_conn = psycopg.connect("user='testseals' dbname='testseals' host='localhost' password='testseals' port='5432'")
                ts_conn.autocommit = True
                cursor = ts_conn.cursor()
                sql_file = open(os.path.join(test_data_dir, "testseals.sql"), 'r')
                cursor.execute(sql_file.read())
                ts_conn.commit()

            finally:
                ts_conn.close()

        if "testsealsblank" not in list_database:
            cursor = pg_conn.cursor()
            cursor.execute("CREATE DATABASE testsealsblank WITH OWNER testseals TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'C.UTF-8'")
            try:
                tb_conn = psycopg.connect("user='testseals' dbname='testsealsblank' host='localhost' password='testseals' port='5432'")
                tb_conn.autocommit = True
                cursor = tb_conn.cursor()
                sql_file = open(os.path.join(test_data_dir, "testseals_schema.sql"), 'r')
                cursor.execute(sql_file.read())
                tb_conn.commit()
                
            finally:
                tb_conn.close()
            
        db = DB(db_name="testseals", username="testseals", password="testseals")
        db_blank = DB(db_name="testsealsblank", username="testseals", password="testseals")

            # Now yield the stuff we need, the data directory and the two databases
        yield (test_data_dir, db, db_blank)
     
    connection = psycopg.connect("user='" + pg_username + "' host='localhost' password='" + pg_password + "' port='5432'")
    connection.autocommit = True
    cur = connection.cursor()

    cur.execute("drop database testseals;")
    cur.execute("drop database testsealsblank;")
    cur.execute("drop user testseals;")
        

