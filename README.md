# Comscore Coding Challenge

This repo contains a pair of Python programs that performs the Comscore Coding Challenge.

* The first program, `import.py`, reads a CSV file and stores the data in a datastore.

* The second program, `query.py`, performs a set of queries based on command-line arguments.

* They share a module, `datastore.py`, with data access and storage methods.

## Setup

Clone this repository into a directory on your local computer.  Make sure it has Python 2.7 at `/usr/bin/python`.

## Running `import.py`

From a terminal window, run the following command: `./import.py`

The program assumes the CSV data is stored in pipe-delimited format in a file named data.csv and reads this file.

The data.csv file provided in this repository uses the example data described in the coding challenge:

    STB|TITLE|PROVIDER|DATE|REV|VIEW_TIME
    stb1|the matrix|warner bros|2014-04-01|4.00|1:30
    stb1|unbreakable|buena vista|2014-04-03|6.00|2:05
    stb2|the hobbit|warner bros|2014-04-02|8.00|2:45
    stb3|the matrix|warner bros|2014-04-02|4.00|1:05

If there were no problems, the data will be stored in the datastore and the program will print a single line:
4 rows imported

The program can be run multiple times, and the existing data will be overwritten each time.  The datastore will not increase in size until new CSV data is imported.

## Running `query.py`

From a terminal window, run the following command: `./query.py (options)`
The options are:
* `-s columns` -- Select from a comma-separated list of columns, e.g. `-s TITLE,REV,DATE`
* `-o columns` -- Order the output according to a comma-separated list of columns, e.g., `-o DATE,TITLE`
* `-f column=value` -- Filter the output so that it only includes certain rows, e.g., `-f DATE=2014-04-01`

Using the examples in the Coding Challenge, these three options will result in the following output:

    $ ./query.py -s TITLE,REV,DATE -o DATE,TITLE
    the matrix,4.00,2014-04-01
    the hobbit,8.00,2014-04-02
    the matrix,4.00,2014-04-02
    unbreakable,6.00,2014-04-03

    $ ./query.py -s TITLE,REV,DATE -f DATE=2014-04-01
    the matrix,4.00,2014-04-01

An advanced Select option is available with a Group option:
* `-s columns_with_aggregation` -- Select from a comma-separated list of columns with an aggregation, e.g. `-s TITLE,REV:sum,STB:collect`
* `-g column` -- Group the rows by this column, applying the column aggregations

The following aggregations are available: `min`, `max`, `sum`, `count`, `collect`.
Combining the Select and Group options will result in the following output:

    $ ./query.py -s TITLE,REV:sum,STB:collect -g TITLE
    the matrix,8.00,[stb1,stb3]
    the hobbit,8.00,[stb2]
    unbreakable,6.00,[stb1]

Finally, there is an advanced Filter option:
* `-f compound_filter` -- apply multiple Filters to the output, e.g., `-f 'STB="stb1" AND TITLE="the hobbit" OR TITLE="unbreakable"'`

Using this option will result in the following output:

    $ ./query.py -s TITLE,REV -f 'TITLE="the hobbit" OR TITLE="the matrix"'
    the matrix,4.00
    the hobbit,8.00
    the matrix,4.00

## The datastore

The data that was imported is stored in three text files and a binary file in the `datastore/` directory:
* `datastore/stbs` contains a list of unique STB values, one per line
* `datastore/titles` contains a list of unique TITLE values, one per line
* `datastore/providers` contains a list of unique PROVIDER values, one per line
* `datastore/keys` contains a binary representation of each row in the data:
    - `stb`: unsigned integer as an index into `datastore/stbs`
    - `title`: unsigned integer as an index into `datastore/titles`
    - `provider`: unsigned integer as an index into `datastore/providers`
    - `date`: unsigned integer of the date as a number (2014-04-01 is stored as 20140401)
    - `rev`: unsigned small integer of the revenue as a number (4.00 is stored as 400, up to a maximum of 65535))
    - `view_time`: unsigned small integer of the view time as a number (1:30 is stored as 90, up to a maximum of 65535))

`datastore/keys` stores the above fields in this order: stb,title,date,provider,rev,view_time so that the first three are used as a unique (primary) key.  This prevents duplicate rows with the same key.

The resulting size of `datastore/keys` is just 18 bytes per line, or 72 bytes for the four rows shown in the example data above.  The other files only grow when new STB, TITLE or PROVIDER values are imported.

## Code features

`import.py` reads the input file line by line, compresses the data into 18-byte key/value pairs to remove duplicates, and writes the resulting files to the datastore.  This makes for a fast import process.

`query.py` processes the command-line options to handle all the Select, Order, Filter and Group options listed above.

Then it reads the data from the datastore one row at a time and writes the selected data to stdout.  Or, if the Group option was selected, the data is grouped by that column and the other columns are aggregated, and after all the data has been processed then the grouped data is written to stdout.

If the Order option was selected, the data is written to a file named `output` which is then sorted using the Unix `sort` command and the output is written to stdout.

This allows for processing very large datasets, because the data is grouped or written out immediately before processing the next row of data.

## To Do

There was no mention of error handling in the coding challenge, whether to use exit codes or stderr messages or other notification methods.  As a result, no error handling is performed on the data and the programs will simply crash if given bad data/options.