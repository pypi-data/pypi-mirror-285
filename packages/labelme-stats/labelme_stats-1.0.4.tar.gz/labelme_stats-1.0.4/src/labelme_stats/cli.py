#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""comment here"""
import collections
import json
import os
import os.path as osp
import argparse
import sys
    

def entry():
    parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('dir', type=str, help='dir file path as input')
    parser.add_argument('-v', action='store_true')
    args = parser.parse_args()

    counter = collections.Counter()
    file_counter = 0
    for dirpath, dirnames, filenames in os.walk(args.dir):
        for filename in filenames:
            if osp.splitext(filename)[-1] != '.json':
                continue
            filefullname = osp.join(dirpath, filename)
            file_counter += 1

            file_label_counter = collections.Counter()
            with open(filefullname) as f:
                data = json.load(f)
            for shape in data['shapes']:
                counter[shape['label']] += 1
                file_label_counter[shape['label']] += 1

            # print(f"### file: {file_counter}: {filefullname} ###")
            # print(f"total counter: {counter}")
            # print(f"file label counter: {file_label_counter}")

            if args.v:
                file_labels_stat = []
                for label, count in file_label_counter.items():
                    file_labels_stat.append(f'{label}: {count}')                    
                print('{}. {}: [{}]'.format(file_counter, filename, ', '.join(file_labels_stat)))

    print(f'annotated directory `{args.dir}` has {file_counter} json files')
    print('---')

    print('Statistics of Labels')
    total = 0
    for label, count in counter.items():
        print('{:>10}: {}'.format(label, count))
        total += count
    print(f"total labels: {total}")
