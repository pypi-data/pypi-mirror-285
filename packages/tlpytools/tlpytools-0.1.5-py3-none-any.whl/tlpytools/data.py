import os
import numpy as np
import pandas as pd
import geopandas as gpd
import sqlalchemy as sql
import openmatrix as omx
from cryptography.fernet import Fernet
import cryptpandas as crp
import getpass


class data_tables():
    """Collection of tools to handle table data.
    """
    @staticmethod
    def read_tbl_data(s):
        """Read table data according to spec. Typically ran as part of run_yaml.load_yaml_data.
        Use get_sample_spec() to see example.
        
        Args:
            s (dict): dictionary object containing spec

        Returns:
            dfs: a dictionary of DataFrame objects
        """
        # read input data
        dfs = {}
        for tbl in s['FILES']['INPUTS'].keys():
            file_path = s['FILES']['INPUTS'][tbl]
            file_type = file_path.split('.')[-1]
            # check for INPUT_COLUMNS select
            col_select = False
            if 'INPUT_COLUMNS' in s['FILES']:
                if tbl in s['FILES']['INPUT_COLUMNS']:
                    col_select = True
            # .csv will use pd.read_csv, a file is required
            # .xlsx will use pd.read_excel, a file is required
            # .crypt requires a file and password prior set up needed, see tl_util.py
            # .sqlsvr requires valid db connection and credential, see tl_util.py
            # .omx will use openmatrix, a file is required
            # .fea will use pd.read_feather, a file is required
            if file_type == 'csv':
                dfs[tbl] = pd.read_csv(file_path)
            elif file_type == 'xlsx':
                dfs[tbl] = pd.read_excel(file_path)
            elif file_type == 'crypt':
                fsch = file_path.split('.')[0]
                ftbl = file_path.split('.')[1]
                tkey = "{}.{}".format(fsch, ftbl)
                dfs[tbl] = savona_tables.read_tables(schema=fsch, table=ftbl,
                                                     source='local')[tkey]
            elif file_type == 'sqlsvr':
                fsch = file_path.split('.')[0]
                ftbl = file_path.split('.')[1]
                tkey = "{}.{}".format(fsch, ftbl)
                dfs[tbl] = savona_tables.read_tables(schema=fsch, table=ftbl,
                                                     source='server')[tkey]
            elif file_type == 'fea':
                if col_select:
                    cols = s['FILES']['INPUT_COLUMNS'][tbl]
                    dfs[tbl] = pd.read_feather(file_path, columns=cols)
                else:
                    dfs[tbl] = pd.read_feather(file_path)
            elif file_type == 'omx':
                omxfile = omx.open_file(file_path)
                if col_select:
                    mat_list = s['FILES']['INPUT_COLUMNS'][tbl]
                else:
                    mat_list = omxfile.list_matrices()
                df = pd.DataFrame()
                for matrix in mat_list:
                    mat = np.array(omxfile[matrix])
                    df[matrix] = mat.flatten()
                dfs[tbl] = df
                omxfile.close()
            else:
                raise (ValueError("File type {} not supported.".format(file_type)))
            # post process col select
            if col_select:
                cols = s['FILES']['INPUT_COLUMNS'][tbl]
                dfs[tbl] = dfs[tbl][cols]

        return dfs
    
    @staticmethod
    def read_spatial_data(s):
        """Read spatial files using GeoPandas according to spec

        Args:
            s (dict): dictionary object containing spec

        Returns:
            dict: dictionary of GeoDataFrame objects
        """
        # read in spatial files
        gdfs = {}
        for tbl in s['FILES']['SPATIALS'].keys():
            file_path = s['FILES']['SPATIALS'][tbl]
            gdfs[tbl] = gpd.read_file(file_path)
        
        return gdfs

    @staticmethod
    def export_data(dict_df, ofiles, omx_size=None, omx_mode='a'):
        """Export dictionary of dataframes into data files. Typically ran as part of a step within run_yaml.run_steps.
        Unlike export_csv, this method supports many file types: csv, omx, fea, and sqlsvr.
        Note omx matices will always be exported as 1-d flattened if omx_size is None.
        For other omx sizes, input duples such as (NoTAZ, NoTAZ)

        Args:
            dict_df (dict): dictionary of dataframes
            files (dict): dictionary of table names with file extension in file paths
            omx_size (duple): omx mat sizes, Default None
            omx_mode (str): omx file read write mode, 'a' for append, 'w' for write, Default is 'a'
        """
        # export data
        for otbl in ofiles.keys():
            try:
                filepath = ofiles[otbl]
                file_type = filepath.split('.')[-1]
                # create directory if doesn't exist
                if file_type in ['csv', 'fea', 'omx']:
                    filedir = os.path.dirname(filepath)
                    if (not os.path.exists(filedir)):
                        os.makedirs(filedir)
                # export data of a particular type
                if file_type == 'csv':
                    dict_df[otbl].to_csv(filepath, index=False)
                elif file_type == 'sqlsvr':
                    table_spec = {otbl: filepath}
                    savona_tables.write_tables(table_spec, df_dict=dict_df)
                elif file_type == 'fea':
                    dict_df[otbl] = pd.to_feather(filepath)
                elif file_type == 'omx':
                    # by default use append mode 'a'
                    # overwrite 'w' mode is not used here
                    omxfile = omx.open_file(filepath, omx_mode)
                    omx_mat_list = omxfile.list_matrices()
                    mat_list = list(dict_df[otbl].columns)
                    for mat_name in mat_list:
                        if mat_name in omx_mat_list:
                            # delete existing mapping
                            omxfile.delete_mapping(mat_name)
                        colseries = dict_df[otbl][mat_name]
                        if omx_size == None:
                            slength = len(colseries)
                            root = np.sqrt(slength)
                            if int(root)**2 == slength:
                                mat_size = (root, root)
                            else:
                                mat_size = (1, slength)
                        else:
                            mat_size = omx_size
                        omxfile[mat_name] = colseries.to_numpy().reshape(mat_size)
                    omxfile.close()
            except Exception as e:
                print('export table {} failed. {}'.format(otbl, e))

    @staticmethod
    def export_csv(dict_df, ofiles):
        """Export dictionary of dataframes into csv files. Typically ran as part of a step within run_yaml.run_steps.

        Args:
            dict_df (dict): dictionary of dataframes
            files (dict): dictionary of table names and csv file paths
        """
        # export data
        for otbl in ofiles.keys():
            try:
                # create directory if doesn't exist
                filepath = ofiles[otbl]
                filedir = os.path.dirname(filepath)
                if (not os.path.exists(filedir)):
                    os.makedirs(filedir)
                dict_df[otbl].to_csv(filepath, index=False)
            except Exception as e:
                print('export table {} failed. {}'.format(otbl, e))


class savona_tables():
    """Collection of tools to interact with savona online and offline. Some local set up may be required to use encrypted offline mode.
    """

    __cache_pswd = None
    __cache_fkey = None

    @classmethod
    def __password_manager(cls, fromLocalEnv='savona_secret', echoEncryptedPwd=True):
        """A simple local password manager that enables access to your encrypted data.
        Do not ever log print statements within password manager as saving encrypted string and 
        salt will allow attackers to decrypt your password.

        Args:
            fromLocalEnv (str, optional): A local env stored encrypted password. Defaults to 'savona_secret'.
            echoEncryptedPwd (bool, optional): print encrypted password to help with set up. Defaults to True.

        Returns:
            decryptedPassword: password that has been decrpyted
        """
        if cls.__cache_pswd == None:
            # get encrypted password from local env, cache, return decrypt
            if fromLocalEnv != None:
                secret_var = fromLocalEnv
                secret_salt_var = fromLocalEnv + "_salt"
                if os.getenv(secret_var) != None and os.getenv(secret_salt_var) != None:
                    # load and cache local env vars
                    cls.__cache_pswd = str.encode(os.getenv(secret_var), 'utf-8')
                    cls.__cache_fkey = str.encode(os.getenv(secret_salt_var), 'utf-8')
                    fernet = Fernet(cls.__cache_fkey)
                    pswd = fernet.decrypt(cls.__cache_pswd).decode()
                    print("\Password loaded and decrypted from local env var...")
                    return pswd
                else:
                    # local env vars not specified
                    print("\nLocal env vars for password not set up...")
            # get password from console, encrypt, then cache
            print("Enter password to read encrypted data.")
            pswd = getpass.getpass()
            cls.__cache_fkey = Fernet.generate_key()
            fernet = Fernet(cls.__cache_fkey)  # save hashed password to this session
            cls.__cache_pswd = fernet.encrypt(pswd.encode())
            print("Password saved to session.")
            if echoEncryptedPwd:
                print("\nSave pwd salt to your local env variable '{secret_salt_var}': {s}".
                      format(secret_salt_var=secret_salt_var, s=cls.__cache_fkey))
                print("Save encrypted pwd to your local env variable '{secret_var}': {s}\n".
                      format(secret_var=secret_var, s=cls.__cache_pswd))
            return pswd
        else:
            # get encrypted password from cache, then decrypt
            fernet = Fernet(cls.__cache_fkey)
            pswd = fernet.decrypt(cls.__cache_pswd).decode()
            return pswd

    @staticmethod
    def write_tables(table_spec, df_dict):
        """Write a dictionary of dataframes to a list of tables

        Args:
            table (dict, optional): specify schema and tables to load. Defaults to '*'.
            df_dict (dict): dictionary of dataframes

        Raises:
            ValueError: wrong value or type provided
        """
        # push to sql server
        engine = sql.create_engine(
            'mssql+pyodbc://SAVONA/TL_RESEARCH_ANALYTICS_DEV?driver=SQL Server',
            fast_executemany=True)
        for (tbl, filepath) in table_spec.items():
            try:
                fsch = filepath.split('.')[0]
                ftbl = filepath.split('.')[1]
                print("{} table upload into {}.{} started...".format(tbl, fsch, ftbl))
                df_dict[tbl].to_sql(
                    name=ftbl,
                    con=engine,
                    schema=fsch,
                    if_exists='replace',
                    index=False,
                    chunksize=200,
                    method='multi',
                )
                print("--> data upload complete")
            except Exception as e:
                print("--> data upload failed. {}".format(e))

    @classmethod
    def read_tables(cls, schema='*', table='*', source='local'):
        """
        usage for read savona data
        - add salt of savona data to environment variable 'savona_salt'
        - add path of savona data to environment variable 'savona_path'
        - in addition to salt and path, you may also need to set up password encripted
          string and salt. Or you may forgo password set up and enter it every time
        "df_dict = read_savona_tables()"
        then input your personal password when prompted

        Args:
            schema (str, optional): specify schema to load. Defaults to '*'.
            table (str, optional): specify table to load. Defaults to '*'.
            source (str, optional): sources may be local or server. Defaults to 'local'.

        Raises:
            ValueError: wrong value or type provided
        """
        df_dict = {}
        if source == 'local':
            pswd = cls.__password_manager()
            # get savona_salt
            if os.getenv('savona_salt') == None:
                msg = """'savona_salt' env var not found.
                If you lost your salt after previous data download, 
                you will need to download again and save your salt."""
                # raise Exception(msg)
                print(msg)
                plain_salt = input("Enter your savona_salt: ")
                salt = str.encode(plain_salt, 'utf-8')
            else:
                salt = str.encode(os.getenv('savona_salt'), 'utf-8')
            # get savona_path
            if os.getenv('savona_path') == None:
                folder = input("Enter your savona_path: ")
            else:
                folder = os.getenv('savona_path')
            # read crypt files
            filetype = "crypt"
            for root, dirs, files in os.walk(folder):
                for file in files:
                    # read data
                    file_list = file.split('.')
                    fsche = file_list[0]
                    ftbl = '.'.join(file_list[1:-1])
                    ftyp = file_list[-1]
                    # check ignore criteria
                    if ftyp != filetype:
                        continue
                    if schema != '*' and schema != fsche:
                        continue
                    if table != '*' and table != ftbl:
                        continue

                    print("Reading table from local " + os.path.join(root, file) + 20 * " ",
                          end="\r")
                    # read data
                    sc = file.split('.')[0]
                    tb = '.'.join(file.split('.')[1:-1])
                    table_name = "{}.{}".format(sc, tb)
                    df_dict[table_name] = crp.read_encrypted(path=os.path.join(root, file),
                                                             password=pswd,
                                                             salt=salt)
        elif source == 'server':
            engine = sql.create_engine(
                "mssql+pyodbc://SAVONA/TL_RESEARCH_ANALYTICS_DEV?driver=SQL Server")

            # build reference of db tables
            query = 'SELECT SCHEMA_NAME(schema_id) AS schema_name,* FROM sys.tables ;'
            ref_tables = pd.read_sql_query(query, engine)
            ref_tables = ref_tables.sort_values(by=["schema_id", "schema_name", "name"])

            # filter selected schema and table
            if schema != '':
                ref_tables = ref_tables[ref_tables['schema_name'] == schema]
            if table != None:
                ref_tables = ref_tables[ref_tables['name'] == table]

            # query data into df dict
            for index, data in ref_tables.iterrows():
                db_table = "[{schema}].[{table}]".format(schema=data['schema_name'],
                                                         table=data['name'])
                table_name = "{}.{}".format(data['schema_name'], data['name'])
                print("Reading table from sql server " + db_table + 20 * " ", end="\r")
                query = 'SELECT * FROM {db_tbl};'.format(db_tbl=db_table)
                db_table_df = pd.read_sql_query(query, engine)
                df_dict[table_name] = db_table_df

        else:
            raise ValueError('source must be either local or server')
        print('\n')  # make a new line for future print
        return (df_dict)

    @classmethod
    def download_encrypted(cls, flag_csv="savona.sys.tables_flag.csv"):
        """Download tables from savona and encrypt it. 

        Args:
            flag_csv (str, optional): A list of table with flag 'extract' to download. Defaults to "savona.sys.tables_flag.csv".
        """

        # specify file extension type
        ext = "crypt"

        # get password
        pswd = cls.__password_manager()

        # read flagged_table csv
        try:
            flagged_tables = pd.read_csv(flag_csv)
            flagged_tables = flagged_tables[flagged_tables["extract"] == 1]
        except:
            print("You need to build a flagged table of savona.sys.tables")
            print("Specify tables to be extracted with 1 in the 'extract' column")

        # save list of df into encrypted parquet

        # read salt
        plain_salt = os.getenv('savona_salt')
        if plain_salt == None:
            salt = crp.make_salt()
            print("Salt was not specified, post download set up is required!\n")
            print("Save salt to your environment variable 'savona_salt': \n{}".format(salt))
            # encode decode to ensure double slash is handled properly for encryption
            plain_salt = input("Enter salt provided above: ")
            salt = str.encode(plain_salt, 'utf-8')
        else:
            salt = str.encode(plain_salt, 'utf-8')

        # read output folder
        folder = os.getenv('savona_path')
        if folder == None:
            folder = os.path.join(os.getcwd(), "data_extract")
            print("No savona_path has been specified, using current directory instead.")
            print("Specify savona_path environment variable after download")
        print("Data download completed: {}".format(folder))

        # folder = '..\savona'
        engine = sql.create_engine(
            "mssql+pyodbc://SAVONA/TL_RESEARCH_ANALYTICS_DEV?driver=SQL Server")

        for index, data in flagged_tables.iterrows():
            db_table = "[{schema}].[{table}]".format(schema=data['schema_name'],
                                                     table=data['name'])

            db_file = os.path.join(
                folder, "{schema}.{table}.{ext}".format(schema=data['schema_name'],
                                                        table=data['name'],
                                                        ext=ext))

            if not os.path.isfile(db_file):
                query = 'SELECT * FROM {db_tbl};'.format(db_tbl=db_table)
                db_table_df = pd.read_sql_query(query, engine)
                # db_table_df.to_parquet(
                #     "{}.parquet".format(db_file), engine="pyarrow")
                crp.to_encrypted(db_table_df, password=pswd, path=db_file, salt=salt)
                del db_table_df
                print("{} encrypted and saved.".format(db_table))
                pass

    @staticmethod
    def export_tbl_list(csv_file="savona.sys.tables.csv"):
        # engine = sql.create_engine(
        #     "mssql+pyodbc://SAVONA/TL_RESEARCH_ANALYTICS_DEV?driver=SQL+Server+Native+Client+11.0")
        engine = sql.create_engine(
            "mssql+pyodbc://SAVONA/TL_RESEARCH_ANALYTICS_DEV?driver=SQL Server")
        query = 'SELECT SCHEMA_NAME(schema_id) AS schema_name,* FROM sys.tables ;'
        all_tables = pd.read_sql_query(query, engine)
        all_tables = all_tables.sort_values(by=["schema_id", "schema_name", "name"])
        all_tables.insert(loc=0, column='extract', value=0)
        all_tables.to_csv(csv_file, index=False)
