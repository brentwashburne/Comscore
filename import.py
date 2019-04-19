#! /usr/bin/python

import datastore


data = datastore.data()

count = 0
with open('data.csv') as input:
    next(input)    # skip header line
    for line in input:
        data.add(line.strip().split('|'))
        count += 1

data.write()
print count, 'rows imported'
