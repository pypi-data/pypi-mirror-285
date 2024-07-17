import duckdb
#from whereabouts_tools.utils.au_utils import *

class LoaderAU:
    def __init__(self, db_name, data_folder):
        """
        Create the database and all tables 

        Args
        ----
        db_name (str): name of the database
        data_folder (str): path to where GNAF data is located
        """
        self.db_name = db_name 
        self.data_folder = data_folder 

         # query for creating tables
        standard_query_filename = f'whereabouts_tools/queries/au/create_tables_duckdb.sql'
        db = duckdb.connect(db_name)
        try:
            create_all_tables(db, standard_query_filename)
        except:
            print("Tables already exist")
        db.close()

    def load_data_basic(self):
        """
        Load authority code tables
        """
        db = duckdb.connect(self.db_name)
        folder_auth = f'{self.data_folder}/G-NAF FEBRUARY 2024/Authority Code'
        load_auth_data(db, folder_auth)
        db.close()

    def load_data_state(self, state_name):
        """
        Load GNAF data for a given state or list of states

        Args
        ----
        state_name (str or list of str): state names to load data for (all abbreviated)
        """
        # connect to database
        db = duckdb.connect(self.db_name)
       
        # folder where all data for standard tables located
        folder_standard = f'{self.data_folder}/G-NAF FEBRUARY 2024/Standard'

        # all valid state names
        state_names = ["VIC", "SA", "TAS", "NSW", "ACT", "QLD", "WA", "NT"]

        if isinstance(state_name, str):
            if state_name not in state_names:
                print(f"Invalid Australian state name.\nPlease specify one of {state_names}")
            else:
                print(f'Loading data for {state_name}')
                load_state_data(db, folder_standard, state_name)
        elif isinstance(state_name, list):
            for state_name_str in state_name:
                if state_name_str not in state_names:
                    print(f"Invalid Australian state name.\nPlease specify one of {state_names}")
                else:
                    print(f'Loading data for {state_name_str}')
                    load_state_data(db, folder_standard, state_name_str)
        db.close()

    def create_neat_addresses(self):
        """
        Create address table of addresses that fit the whereabouts format
        """
        db = duckdb.connect(self.db_name)
        # create address view
        view_filename = 'whereabouts_tools/queries/au/create_view_duckdb.sql'
        create_view(db, view_filename)

        # create full address table
        full_address_filename = 'whereabouts_tools/queries/au/create_full_addresses.sql'
        create_full_address_table(db, full_address_filename)
        db.close()

    def drop_nonneat_tables(self):
        """
        Drop all the tables that are not the whereabouts full address table
        """
        db = duckdb.connect(self.db_name)
        all_table_views = db.execute('show tables').df().name.values
        all_tables = [table for table in all_table_views if 'VIEW' not in table]
        all_views = [view for view in all_table_views if 'VIEW' in view]
        for table in all_tables:
            db.execute(f'drop table "{table}"')
        for view in all_views:
            db.execute(f'drop view "{view}"')
        db.close()

    def export_neat_addresses(self, path):
        """
        Export the whereabouts formatted addresses as a parquet file
        """
        db = duckdb.connect(self.db_name)
        # export full address table to parquet file
        db.execute(f"copy addrtext to '{path}' (FORMAT PARQUET);")
        db.close()
