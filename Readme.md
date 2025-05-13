# AIM

The idea is to prototype a simple API that will combine REST and GraphQL to provide a flexible and efficient way to interact with a database. The API will allow users to perform CRUD operations on a database using a flekisble way to query and manipulate data. 
The idea is that the user sends in some structured data and a LLM will generate the SQL queries to perform the CRUD operations. 

## Requirements

- Python 3.11+
- VSCode

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd AIM
   ```

2. Install `pyenv` and `pyenv-virtualenv` if not already installed:
   ```bash
   brew update
   brew install pyenv pyenv-virtualenv
   ```

3. Add the following to your `~/.zshrc` to enable `pyenv` and `pyenv-virtualenv`:
   ```bash
   export PYENV_ROOT="$HOME/.pyenv"
   export PATH="$PYENV_ROOT/bin:$PATH"
   eval "$(pyenv init --path)"
   eval "$(pyenv init -)"
   eval "$(pyenv virtualenv-init -)"
   ```
   Then restart your terminal or run:
   ```bash
   source ~/.zshrc
   ```

4. Install Python 3.11 and create a virtual environment:
   ```bash
   pyenv install 3.11.0
   pyenv virtualenv 3.11.0 aim_env
   pyenv local aim_env
   ```

5. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

6. Download the Chinook.db file:
   ```bash
   curl -s https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql | sqlite3 Chinook.db
   ```

7. Run the Flask application:
   ```bash
   python3 main.py
   ```

8. Test the API:
   Use the following `curl` command to test the `/query` endpoint:
   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{"request": "Get all artists"}' http://127.0.0.1:5000/query
   ```



