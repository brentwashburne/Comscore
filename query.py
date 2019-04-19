#! /usr/bin/python

import copy
import os
import re
import sys
import datastore


data = datastore.data()

MIN=1
MAX=2
SUM=3
COUNT=4
COLLECT=5
aggregates = {'min': MIN, 'max': MAX, 'sum': SUM, 'count': COUNT, 'collect': COLLECT}
columns = {'STB': 0, 'TITLE': 1, 'PROVIDER': 2, 'DATE': 3, 'REV': 4, 'VIEW_TIME': 5}
select = []
filter = {}
order = []
group = None
default_group = []
groups = {}


def parse(column, value):
    if column == 0:
        return data.stb_dict[value]
    if column == 1:
        return data.title_dict[value]
    if column == 2:
        return data.provider_dict[value]
    if column == 3:
        return int(value.replace('-', ''))
    if column == 4:
        rev = value.split('.')
        return int(rev[0]) * 100 + int(rev[1])
    if column == 5:
        time = value.split(':')
        return int(time[0]) * 60 + int(time[1])

def format(column, value):
    if column == 0:
        return data.stbs[value]
    if column == 1:
        return data.titles[value]
    if column == 2:
        return data.providers[value]
    if column == 3:
        date = str(value)
        return '%s-%s-%s' % (date[0:4], date[4:6], date[6:8])
    if column == 4:
        return '%d.%02d' % divmod(value, 100)
    if column == 5:
        return '%d:%02d' % divmod(value, 60)


argc = 1
while argc < len(sys.argv):
    option = sys.argv[argc]
    param = sys.argv[argc+1]
    argc += 2
    if option == '-s':
        for field in param.split(','):
            if ':' in field:
                column, aggregate = field.split(':')
                select.append([columns.get(column), aggregates.get(aggregate)])
                default = None
                if aggregate in ['sum', 'count']:
                    default = 0
                elif aggregate == 'collect':
                    default = set()
                default_group.append(default)
            else:
                select.append([columns.get(field), None])
    elif option == '-f':
        filters = re.findall('([A-Z]+)=("[^"]+"|[^ ]+)', param)
        for f in filters:
            column = f[0]
            value = f[1].strip('"')
            c = columns[column]
            values = filter.get(c, [])
            values.append(parse(c, value))
            filter[c] = values
    elif option == '-g':
        group = columns.get(param)
    elif option == '-o':
        order = [columns.get(field) for field in param.split(',')]

# if we need to sort the output, write the results to a file
# otherwise write the results to stdout
output = open('output', 'w') if order else sys.stdout

for row in data.read():
    keep = True
    for column, values in filter.items():
        if row[column] not in values:
            keep = False
            break
    if not keep:
        continue

    if group is not None:
        group_row = groups.get(row[group], copy.deepcopy(default_group))
        for i, s in enumerate(select):
            column, aggregate = s
            if column == group: continue
            value = row[column]
            group_value = group_row[i-1]
            if aggregate == MIN:
                if group_value < value or group_value is None:
                    group_row[i-1] = value
            elif aggregate == MAX:
                if group_value > value or group_value is None:
                    group_row[i-1] = value
            elif aggregate == SUM:
                group_row[i-1] += value
            elif aggregate == COUNT:
                group_row[i-1] += 1
            elif aggregate == COLLECT:
                group_row[i-1].add(value)
        groups[row[group]] = group_row
    else:
        comma = False
        for s in select:
            if comma:
                output.write(',')
            comma = True
            output.write(format(s[0], row[s[0]]))
        output.write('\n')

# Output groups
if group is not None:
    for g, row in groups.iteritems():
        comma = False
        for i, s in enumerate(select):
            if comma:
                output.write(',')
            comma = True
            value = row[i-1]
            column, aggregate = s
            if column == group:
                output.write(format(group, g))
            elif aggregate == COLLECT:
                collect = [format(column, value) for value in row[i-1]]
                output.write('[%s]' % ','.join(collect))
            else:
                output.write(format(column, value))
        output.write('\n')

# to sort the results, close the file and call the sort program
if order:
    output.close()
    sort_options = ['sort', 'output', '-t,']
    for o in order:
        for i, s in enumerate(select):
            if o == s[0]:
                sort_options.append('-k%d,%d' % (i+1, i+1))
                break
    os.system(' '.join(sort_options))
