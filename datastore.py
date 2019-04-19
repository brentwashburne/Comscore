#! /usr/bin/python

import os, struct


datastore_path = 'datastore'
stb_path = datastore_path + '/stbs'
title_path = datastore_path + '/titles'
provider_path = datastore_path + '/providers'
key_path = datastore_path + '/keys'
new_key_path = datastore_path + '/new_keys'
key_format = 'III'    # stb, title, date
value_format = 'HHH'  # provider, rev, view_time


class data(object):
    def __init__(self):
        if not os.path.exists(datastore_path):
            os.mkdir(datastore_path)
        self.data = {}
        self.stbs, self.stb_dict = self.read_list(stb_path)
        self.titles, self.title_dict = self.read_list(title_path)
        self.providers, self.provider_dict = self.read_list(provider_path)

    def write(self):
        self.write_list(stb_path, self.stbs)
        self.write_list(title_path, self.titles)
        self.write_list(provider_path, self.providers)
        self.merge()

    def read_list(self, path):
        lines = []
        if os.path.exists(path):
            with open(path) as f:
                lines = f.read().splitlines()
        lines_dict = dict((line, i) for i, line in enumerate(lines))
        return lines, lines_dict

    def lookup_list(self, list, list_dict, value):
        index = list_dict.get(value, -1)
        if index == -1:
            index = list_dict[value] = len(list)
            list.append(value)
        return index

    def write_list(self, path, list):
        with open(path, 'w') as f:
            f.write('\n'.join(list))

    def add(self, row):
        stb_index = self.lookup_list(self.stbs, self.stb_dict, row[0])
        title_index = self.lookup_list(self.titles, self.title_dict, row[1])
        provider_index = self.lookup_list(self.providers, self.provider_dict, row[2])
        date = int(row[3].replace('-', ''))
        price = row[4].split('.', 2)
        rev = int(price[0]) * 100 + int(price[1])
        time = row[5].split(':', 2)
        view_time = int(time[0]) * 60 + int(time[1])

        key = struct.pack(key_format, stb_index, title_index, date)
        value = struct.pack(value_format, provider_index, rev, view_time)
        self.data[key] = value

    def merge(self):
        key_length = struct.calcsize(key_format)
        value_length = struct.calcsize(value_format)
        with open(new_key_path, 'wb') as f2:
            if os.path.exists(key_path):
                with open(key_path, 'rb') as f1:
                    while True:
                        key = f1.read(key_length)
                        if not key: break
                        value = f1.read(value_length)
                        new_value = self.data.pop(key)
                        f2.write(key)
                        f2.write(new_value if new_value else value)
            for key, value in self.data.iteritems():
                f2.write(key)
                f2.write(value)
        os.rename(new_key_path, key_path)

    def read(self):
        key_length = struct.calcsize(key_format)
        value_length = struct.calcsize(value_format)
        if os.path.exists(key_path):
            with open(key_path, 'rb') as f:
                while True:
                    key = f.read(key_length)
                    if not key: break
                    stb, title, date = struct.unpack(key_format, key)
                    value = f.read(value_length)
                    provider, rev, view_time = struct.unpack(value_format, value)
                    yield [stb, title, provider, date, rev, view_time]

