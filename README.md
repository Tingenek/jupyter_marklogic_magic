## MarkLogic Magic

This is a cell magic; a wrapper around the MarkLogic REST API so that code can be evaluated in a Jupyter Notebook cell, and the results returned as a Pandas DataFrame.

Warning. It's experimental, works on Python 3 and your MMV.

## Install

Clone the repo and either run your Jupyter notebook from there, or install it using pip install -e .
In jupyter, use %load_ext marklogic_magic

## Usage

You need:

a) A working MarkLogic server to talk to that has an XDBC server set up.
b) One or more TDE templates installed. (more on that later, but necessary for SQL)

First line of your cell should be %%marklogic <connection string>
Second line... rest of cell is your code.

Using the Titanic example:

%%ml_fetch sql://titanic-reader:titanic-reader@localhost:8079  
select * from titanic.passengers as t

Results are returned as a DataFrame named result_var. After that, you're free to use whatever Python libraries you want.
Note. After the first invocation the connection is persisted, so subsequent cell can use just

%%ml_fetch  
select * from titanic.passengers as t

## Variables

Python variable expansion works, so you can use {var} in you cell and it'll expand to a value before it gets sent to MarkLogic.

## Experimental

You don't have to use SQL, Javascript and XQuery should all work, with the proviso that it's trying to return a DataFrame regardless, so some things may not make sense. For XQuery use xquery:// for javascript javascript://
