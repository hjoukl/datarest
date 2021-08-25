# sw-datarest: Python low code data-driven REST-Tool


Python low code data-driven REST-Tool short description

* License: Mozilla Public License 2.0
* Documentation: https://github.com/simon-w19/sw-datarest

## Installation and usage
Create virtualenv:

```
python -m venv datarest-venv
```

Install sw-datarest:

```
datarest-venv/bin/pip install git+https://github.com/simon-w19/sw-datarest
```

Create a simple CSV file colors.csv:

```
1,red,The color of blood
2,green,The color of hope
3,blue,The color of oceans
4,yellow,Bright as the sun
5,black,Dark as the night
```

Prepare SQLite DB and load CSV data:

```
sqlite3 app.db 'CREATE TABLE t_colors("id" TEXT NOT NULL PRIMARY KEY, "color" TEXT NOT NULL, "description" TEXT)' ".mode csv" ".separator ," ".import colors.csv t_colors"
```

Create app.yaml:

```
datarest:
  fastapi:
    app:
      title: "Colors-Service"
      description: "Provide shiny color informations"
      version: "0.1.0"
  database:
    connect_string: "sqlite:///app.db"
  data:
    colors:
      profile: "database-sqlalchemy"
      schema_specification: "https://www.sqlalchemy.org/"
      dbtable: "t_colors"
```

Fire up a fully functional data-driven REST API, powered by [SQLAlchemy](https://www.sqlalchemy.org/) database reflection (selected by the "database-sqlalchemy" profile config entry:

```
./datarest-venv/bin/sw-datarest run --host 0.0.0.0 --port 8888
```

Provide additional API documentation by using a [tableschema](https://specs.frictionlessdata.io/table-schema/) CSV file schema:

Create colors-schema.json:
```
{
  "fields": [
    {
      "name": "id",
      "type": "string",
      "description": "The color id",
      "x_datarest_example": "1"
    },
    {
      "name": "color",
      "type": "string",
      "description": "The color name",
      "x_datarest_example": "blue"
    },
    {
      "name": "description",
      "type": "string",
      "description": "The color description",
      "x_datarest_example": "This is a nice & shiny color"
    }
  ],
  "primaryKey": "id"
}      
``` 

Use this tableschema in app.yaml by selecting the "table-schema" config profile:

``` 
datarest:
  fastapi:
    app:
      title: "Colors-Service"
      description: "Provide shiny color informations"
      version: "0.1.0"
  database:
    connect_string: "sqlite:///app.db"
  data:
    colors:
      profile: "table-schema"
      schema_specification: "https://specs.frictionlessdata.io/table-schema/"
      schema: "colors-schema.json"
      dbtable: "t_colors"
```
