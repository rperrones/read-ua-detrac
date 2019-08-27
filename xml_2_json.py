#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 19:32:22 2019

@author: Ricardo Perrone

"""
import xmltodict, json
import os
import pandas as pd
import re

class XML_2_JSON:
    
    def __init__(self, filename):
        if filename.endswith(".xml"):
            with open(filename) as fd:
                self.doc = xmltodict.parse(fd.read())
            
            json_data = json.dumps(self.doc, sort_keys=True, indent=4)
            print(json_data)
            output_file = open('teste.json', 'w')
            output_file.write(json_data)

        else:
            print('file extesion is not supported!')

            
if __name__ == '__main__':
    teste = XML2DataFrame('./dataset/annotations/MVI_20011_v3.xml')
    