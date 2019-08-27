#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 19:32:22 2019

@author: Ricardo Perrone

"""
import xmltodict, json
import os
import argparse
import re

class XML_2_JSON:
    
    def __init__(self, path):
        dirs, filename = os.path.split(path)
        name, extension = filename.split(".")

        if filename.endswith(".xml"):
            with open(path) as fd:
                self.doc = xmltodict.parse(fd.read())
            
            json_data = json.dumps(self.doc, sort_keys=True, indent=2)
            json_data_processed = re.sub('."@', '"', json_data) 

            output_file = open(name + '.json', 'w')
            output_file.write(json_data_processed)

        else:
            print('file extesion is not supported!')

            
if __name__ == '__main__':

    # initiate the parser
    parser = argparse.ArgumentParser(prog='XML_2_JSON', usage='%(prog)s [options]', description='Convert a xml file to a json file.')
    parser.add_argument("--annotation", help="path to xml file", default='./dataset/annotations/MVI_20011_v3.xml')
    args = parser.parse_args()
    jsonObj = XML_2_JSON(args.annotation)