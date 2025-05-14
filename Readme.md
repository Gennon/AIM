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


## Usage

The API should provide standard CRUD operations (Create, Read, Update, Delete) for the database. The API will accept JSON payloads with structured data and return the results in a structured format.

### Read  
`GET /query`: This endpoint accepts a JSON payload with data containing the user's query. The API will process the request and return the result.

Example request:
```json
{
  "request": "Get all artists"
}
```
Example response:
```json
{
  "query": "SELECT * FROM artists",
  "result": [
    {
      "ArtistId": 1,
      "Name": "AC/DC"
    },
    {
      "ArtistId": 2,
      "Name": "Accept"
    }
  ]
}
```

A more advanced example:
```json
{
  "Albums": {
      "AlbumName": "string"
  }
}
```
Example response:
```json
{
  "query": "SELECT Album.Title AS AlbumName FROM Album;",
  "result": [
    {
			"AlbumName": "For Those About To Rock We Salute You"
		},
		{
			"AlbumName": "Balls to the Wall"
		},
  ]
}

Even more advanced example:
```json
{
  "request": {
    "Albums": {
        "AlbumName": "string",
        "Artist": "string",
        "NumberOfTracks": {
            "type": "int",
            "value": "10 < x < 15"
        }
    }
  }
}
```
Example response:
```json
{
  "query": """
  SELECT Album.Title AS AlbumName, Artist.Name AS Artist, COUNT(*) AS NumberOfTracks
  FROM Album
    JOIN Artist ON Album.ArtistId = Artist.ArtistId
    JOIN Track ON Album.AlbumId = Track.AlbumId
    GROUP BY Album.Title, Artist.Name
    HAVING COUNT(*) BETWEEN 10 AND 14;",
  "result": [
    {
			"AlbumName": "20th Century Masters - The Millennium Collection: The Best of Scorpions",
			"Artist": "Scorpions",
			"NumberOfTracks": 12
		},
		{
			"AlbumName": "A Matter of Life and Death",
			"Artist": "Iron Maiden",
			"NumberOfTracks": 11
		},
  ]
}
```


### Create
`POST /query`: This endpoint accepts a JSON payload with data containing the user's query. The API will process the request and return the result.
Example request:
```json
{
  "Customer": {
    "FirstName": "Johny",
    "LastName": "Smither",
    "Email": "johny.smither@testing.com"
  }
}
```

Example response:
```json
{
  "query": """
  INSERT INTO Customer (FirstName, LastName, Email) 
  VALUES ('Johny', 'Smither', 'johny.smither@testing.com');
  """,
	"result": "success"
}
```

A more advanced example:
```json
{
  "Customer": {
    "Name": "Jane Doit",
    "Email": "jane.doit@testing.com"
  }
}
````

Example response:
```json
{
  "query": """
  INSERT INTO Customer (FirstName, LastName, Email) 
  VALUES ('Jane', 'Doit', 'jane.doit@testing.com');
  """,
	"result": "success"
}
```

### Update
`PUT /query`: This endpoint accepts a JSON payload with data containing the user's query. The API will process the request and return the result.
Example request:
```json
{
  "Customer": {
    "CustomerId": 64,
    "FullName": "Jane Does",
    "Email": "jane.does@testing.com"
  }
}
```
Example response:
```json
{
  "query": """
  UPDATE Customer 
  SET FirstName = 'Jane', LastName = 'Does', Email = 'jane.does@testing.com' 
  WHERE CustomerId = 64;
  """,
	"result": "success"
}
```

### Delete
`DELETE /query`: This endpoint accepts a JSON payload with data containing the user's query. The API will process the request and return the result.
Example request:
```json
{
  "Customer": {
    "CustomerId": 64
  }
}
```
Example response:
```json
{
  "query": "DELETE FROM Customer WHERE CustomerId = 64;",
  "result": "success"
}
```

A more advanced example:
```json
{
  "Invoice": {
    "Customer": {
      "FullName": "Bjørn Hansen"
    },
    "InvoiceLine": {
      "TrackId": {
        "Name": "Put The Finger On You"
      }
    }
  }
}
```
Example response:
```json
{
  "query": """
    DELETE FROM InvoiceLine
    WHERE InvoiceLine.InvoiceId IN (
      SELECT Invoice.InvoiceId 
      FROM Invoice JOIN Customer ON Invoice.CustomerId = Customer.CustomerId 
      WHERE CONCAT(Customer.FirstName, ' ', Customer.LastName) = 'Bjørn Hansen'
    )
    AND TrackId IN (
      SELECT TrackId 
      FROM Track
      WHERE Name = 'Put The Finger On You'
    );""",
	"result": "success"
}
```
