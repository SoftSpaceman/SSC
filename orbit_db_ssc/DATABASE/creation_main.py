

############# SCRIPT TO SUMMON ALL FNCTIONS FROM DIFFERENT MODULES in ONE FUNCTION.

import os
import sys

# Add the parent directory to sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)


from DATABASE.db_creation.create_db import create_database
from DATABASE.db_creation.create_table import create_tables


#________________________________________________________________

def main():
    
    create_database()
    create_tables()
    #populate_gp_file()

if __name__ == "__main__":
    main()

#________________________________________________________________






