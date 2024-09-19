# Title

Academic world: personal dashboard & research trend

# Purpose

This application can show personal statistics for selected researcher. It can also show trend in selected research topics.

# Demo

Link: https://mediaspace.illinois.edu/media/t/1_72erbir3

# Installation and before first use

## DB setup
Set up the databases as described in MPs of CS411

You might want to open Neo4j Desktop application and let the DBSM of 'academicworld' (in my case, it's called 'CS411DBSM') be active.

## Create views & indices for mysql

In terminal (MacOS)
```bash
mysql -u root -p
```
Then enter password:*****

Then you should enter mysql shell

Change database to "academicworld"
```mysql
USE academicworld;
```

Creating an index on university name:
```mysql
CREATE INDEX uname_index ON university(name);
```
If you have time, create an index on faculty name (optional, slow):
```mysql
CREATE INDEX fname_index ON faculty(name);
```
Create a view (ResearcherFacts):

```mysql
CREATE OR REPLACE VIEW ResearcherFacts AS
    SELECT COUNT(*) AS publications,SUM(num_citations) AS num_citations,f.name AS faculty_name,u.name AS university_name
                 FROM faculty AS f
   	             LEFT JOIN faculty_publication AS fp
                 ON f.id = fp.faculty_id
                 JOIN publication AS p
                 ON fp.publication_id = p.id
                 JOIN university AS u
                 ON f.university_id = u.id
                 GROUP BY f.name,u.name;
 ```


## Clone the github repo to local

Update your credentials in "credentials.py" (you should have set some passwords when you set up the databases per instructions of previous MPs)


Open a jupyter notebook, try importing the following packages. Make sure you're in the working directory, otherwise *credentials* cannot load for sure since it is another python file storing passwords.
```python
import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output,dash_table  # pip install dash (version 2.0.0 or higher)
import dash
import mysql.connector as connection
import dash_bootstrap_components as dbc
import collections
from wordcloud import WordCloud          # pip install wordcloud
from dash_extensions import Lottie       # pip install dash-extensions
import credentials
from pymongo import MongoClient
import pickle
from neo4j import GraphDatabase
```

If any of them cannot be imported, pip install the missing package in terminal. For example:
```bash
pip install dash
```




# Usage
In terminal, go to the working directory
```bash
python project.py
```

And copy&paste the localhost address shown in the terminal (something like "http://127.0.0.1:8050/") to your browser

Select university, faculty, keywords, metric with the dropdown & radio items in the webpage

# Design

Query certain slices of data with mysql, mongodb, neo4j and pandas in the backend. Use plotly Dash to show graphs. Pretty straightforward as you use the application.

## Use of Neo4j
Top collaborators widget

## Use of mongodb
Bottom part, "Exploring research trend"

## Use of mysql
Every other widgets that shows something (except for input widgets such as dropdown menus and radio items). Use prepared statement, index and view.

# Implementation
Backend: mysql, mongodb, neo4j, pandas
Frontend: Dash

# Database techniques
View, Index, prepared statements

# Contributions
I've done this project all by myself (Tianhao Luo)