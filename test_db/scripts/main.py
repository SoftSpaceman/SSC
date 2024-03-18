# This script serves as the entry point of your application.
# It imports functions from other modules (such as api_request.py and db_functions.py) to orchestrate the workflow of your application.
# Typically, main.py will define the main logic of your application, such as fetching data from the API, processing it,
# and storing it in the database, or retrieving data from the database and presenting it to the user.
# It may also handle command-line arguments, user input, or any other interaction with the user or external systems.


## INFO ON HOW TO STRUCTURE FILES.

# 2. **__init__.py**: In Python, directories are not recognized as packages unless they contain a file named `__init__.py`.
# Make sure that your [`database`](command:_github.copilot.openRelativePath?%5B%22database%22%5D "database")
# directory contains an `__init__.py` file. It can be empty.

# 3. **Relative Import**: The dot before [`database`](command:_github.copilot.openRelativePath?%5B%22database%22%5D "database")
# in `.database.create_table` means it's a relative import. Relative imports depend on the current module's name,
# so they can't be used in scripts that are meant to be run directly from the command line.
# If your script is meant to be run from the command line, you should use an absolute import instead.
# For example, if your project's structure looks like this:


# my_project/
# ├── main.py
# └── database/
#     ├── __init__.py
#     └── create_table.py



############# SCRIPT TO SUMMON ALL FNCTIONS FROM DIFFERENT MODULES in ONE FUNCTION.
# # database/create_db.py
# def create_database():
#     # Implementation for creating a database

# # database/create_table.py
# def create_tables():
#     # Implementation for creating tables

# # main.py
# from .database.create_db import create_database
# from .database.create_table import create_tables

# def main():
#     create_database()
#     create_tables()

# if __name__ == "__main__":
#     main()







from database.create_db import create_database
from database.create_table import create_tables


#________________________________________________________________
#A function to call on the funtion to creat the database.
def main():
    # call function from database/create_database.py >> create_database()
    create_database()
if __name__ == "__main__":
    main()

# to use this, open terminal and navigat eto the directory where the main.py
    # file is located and run the following command: python main.py
#________________________________________________________________







#________________________________________________________________
# A FUNCTION TO CALL ON THE create_table.py >> create_tables()

def main():
    # Call functions from different modules as needed
    create_tables()

if __name__ == "__main__":
    main()

# to use this, open terminal and navigat eto the directory where the main.py
    # file is located and run the following command: python main.py
#________________________________________________________________



