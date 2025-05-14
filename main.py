from flask import Flask, request, jsonify
from langchain_ollama import ChatOllama
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
def get_cached_sql_message(user_request, system_prompt):
    messages = [
        ("system",system_prompt),
        ("human", user_request),
    ]
    return llm.invoke(messages)

def generate_sql_message(user_request, system_prompt):
    """Generate or retrieve a cached SQL message."""
    messages = [
        ("system", system_prompt),
        ("human", user_request),
    ]
    return llm.invoke(messages)


def handle_request(request, system_prompt):
    """Handle a user request by generating and executing an SQL query."""
    user_request = json.dumps(request.json)
    if request.method == 'GET':
        sql_message = get_cached_sql_message(user_request, system_prompt)
    else:
      sql_message = generate_sql_message(user_request, system_prompt)

    print(f"SQL Message: {sql_message.content}")
    if not sql_message.content or sql_message.content.strip().upper() == "NULL":
        return {'error': 'Unable to generate SQL query'}, 400
    
    return execute_sql_queries(sql_message.content)

def execute_sql_queries(sql_query):
    """Execute the SQL queries and return the result."""
    sql_queries: str = sql_query.split(';')
    results = []
    try:
      for query in sql_queries:
          query = query.strip()
          if query:
              result = execute_sql_query(query)
              results.append(result)
    
      if len(results) == 1:
          return {'query': sql_queries[0], 'result': results[0]}, 200
      else:
          return {'query': sql_queries[0], 'result': results[-1]}, 200
    except Exception as e:
        return {'error': str(e)}, 400

def execute_sql_query(sql_query):
    """Execute the SQL querys and return the result."""
    result = db.run(sql_query, include_columns=True)
    if result == "":
        return 'success'
    else:
        data = ast.literal_eval(result)
        return data
    

@app.route('/query', methods=['GET', 'POST', 'DELETE', 'PUT'])
def query():
    system_prompt = get_system_prompt(request.method)
    response, status_code = handle_request(request, system_prompt)
    return jsonify(response), status_code
    
def get_system_prompt(method):
    
    pre = f"""
        Your task is to generate SQL queries based on user requests. 
        You are a helpful assistant that can understand natural language and convert it into SQL queries. 
        You should only create queries based on the tables and columns in the datbase {table_info}.
        You should always use explicit column names in your queries, like TableName.ColumnName.
        You should never drop tables.
        You should return a maximum of 1 SQL query.
        You should only respond with the SQL query and nothing else.
      """
    
    example = f"""
        Example:
        SomeValue: "string" should return a SQL query that has the key SomeValue and the value should be of type "string".
        SomeValue: "int" should return a SQL query that has the key SomeValue and the value should be of type "int".
        "string" should never be used in the WHERE clause.
        "int" should never be used in the WHERE clause.
      """
    
    post = """
        If you can't generate a SQL query, respond with \"NULL\".
        Thank you!
      """

    prompts = {
      'GET': """
        You should only retrieve data from the database and not modify it.
      """,
      'POST': """
        You should only modify data in the database by adding items.
        You should create a query that first inserts and then selects the data.
      """,
      'DELETE': """
        The SQL should only delete one or more items in the database.
      """,
      'PUT': """
        The SQL should only update one or more items in the database.
        You should create a query that first updates and then selects the data.
      """,
    }
    return f"""
      {pre}
      {example}
      {prompts[method]}
      {post}
      """

if __name__ == '__main__':
    app.run(debug=True)
