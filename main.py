from flask import Flask, request, jsonify
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage
from langchain_community.utilities import SQLDatabase
import json
import ast
from functools import lru_cache

app = Flask(__name__)

# Initialize the LLM
llm = ChatOllama(model="mistral", temperature=0.5)

# Initialize the database connection
db = SQLDatabase.from_uri("sqlite:///Chinook.db", sample_rows_in_table_info=0)
table_info = db.get_table_info()

# Cache for storing user requests and their corresponding SQL messages
@lru_cache(maxsize=100)
def get_cached_sql_message(user_request):
    messages = [
        (
            "system",
            f"""
            Your task is to generate SQL queries based on user requests. 
            You are a helpful assistant that can understand natural language and convert it into SQL queries. 
            You should only create queries based on the tables and columns in the datbase {table_info}.
            You should always use explicit column names in your queries, like TableName.ColumnName.
            You should never drop tables.
            You should return a maximum of 1 SQL query.
            You should only respond with the SQL query and nothing else.
            You should only retrieve data from the database and not modify it.
            If you can't generate a SQL query, respond with "NULL".
            Thank you!
            """,
        ),
        ("human", user_request),
    ]
    return llm.invoke(messages)

@app.route('/query', methods=['GET'])
def get():
    user_request = json.dumps(request.json)

    # Check cache for SQL message
    sql_message = get_cached_sql_message(user_request)

    if not sql_message.content or sql_message.content.strip().upper() == "NULL":
        return jsonify({'error': 'Unable to generate SQL query'}), 400

    # Execute the SQL query
    try:
        result = db.run(sql_message.content, include_columns=True)   
        # Convert the result to JSON
        data = ast.literal_eval(result)
        return jsonify({'query': sql_message.content,'result': data})    
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    

@app.route('/query', methods=['POST'])
def insert():
    user_request = json.dumps(request.json)

    messages = [
        (
            "system",
            f"""
            Your task is to generate SQL queries based on user requests. 
            You are a helpful assistant that can understand natural language and convert it into SQL queries. 
            You should only create queries based on the tables and columns in the datbase {table_info}.
            You should always use explicit column names in your queries, like TableName.ColumnName.
            You should never drop tables.
            You should return a maximum of 1 SQL query.
            You should only respond with the SQL query and nothing else.
            You should only modify data in the database by adding items and not retrieve it.
            If you can't generate a SQL query, respond with "NULL".
            Thank you!
            """,
        ),
        ("human", user_request),
    ]
    sql_message = llm.invoke(messages)

    if not sql_message.content or sql_message.content.strip().upper() == "NULL":
        return jsonify({'error': 'Unable to generate SQL query'}), 400
    # Execute the SQL query
    print(sql_message.content)
    try:
        result = db.run(sql_message.content, include_columns=True)   
        
        # Convert the result to JSON
        if result is "":
          return jsonify({'query': sql_message.content,'result': 'success'}), 201
        else:
          data = ast.literal_eval(result)
          return jsonify({'query': sql_message.content,'result': data}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    
@app.route('/query', methods=['DELETE'])
def delete():
    user_request = json.dumps(request.json)

    messages = [
        (
            "system",
            f"""
            Your task is to generate SQL queries based on user requests. 
            You are a helpful assistant that can understand natural language and convert it into SQL queries. 
            You should only create queries based on the tables and columns in the datbase {table_info}.
            Do not make up any tables or columns, verify the table names and column names exists the database.
            You should always use explicit column names in your queries, like TableName.ColumnName.
            You should never drop tables.
            You should return a maximum of 1 SQL query.
            You should only respond with the SQL query and nothing else.
            The SQL should only delete one or more items in the database.
            If you can't generate a SQL query, respond with "NULL".
            Thank you!
            """,
        ),
        ("human", user_request),
    ]
    sql_message = llm.invoke(messages)

    if not sql_message.content or sql_message.content.strip().upper() == "NULL":
        return jsonify({'error': 'Unable to generate SQL query'}), 400
    # Execute the SQL query
    print(sql_message.content)
    try:
        result = db.run(sql_message.content, include_columns=True)   
        
        # Convert the result to JSON
        if result is "":
          return jsonify({'query': sql_message.content,'result': 'success'}), 201
        else:
          data = ast.literal_eval(result)
          return jsonify({'query': sql_message.content,'result': data}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    



if __name__ == '__main__':
    #init_db()
    app.run(debug=True)
