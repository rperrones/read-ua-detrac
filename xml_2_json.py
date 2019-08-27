#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 19:32:22 2019

@author: Ricardo Perrone

"""
import xmltodict, json
import xml.etree.ElementTree as ET
import os
import argparse
import re

class XML_2_JSON:
    
    def __init__(self, path):
        dirs, filename = os.path.split(path)
        name, extension = filename.split(".")
        self.json_file = name + '.json'
        if filename.endswith(".xml"):
            self.loadAsXML(path)
        else:
            self.loadAsJson(path, self.json_file)
    
    def getJson(self):
        with open(self.json_file, 'r') as f:
            collection = json.load(f)
        return collection
    
    def loadAsJson(self, path, json_file):
        with open(path) as fd:
            doc = xmltodict.parse(fd.read())
        
        json_data = json.dumps(doc, sort_keys=True, indent=2)
        json_data_processed = re.sub('."@', '"', json_data) 

        output_file = open(json_file, 'w')
        output_file.write(json_data_processed)
        
    
    def loadAsXML(self, path):
        dirs, filename = os.path.split(path)
        name, extension = filename.split(".")
        if filename.endswith(".xml"):
            tree = ET.parse(path)
            self.root = tree.getroot()
        
    
if __name__ == '__main__':

    # initiate the parser
    parser = argparse.ArgumentParser(prog='XML_2_JSON', usage='%(prog)s [options]', description='Convert a xml file to a json file.')
    parser.add_argument("--annotation", help="path to xml file", default='./dataset/annotations/MVI_20011_v3.xml')
    args = parser.parse_args()
    jsonObj = XML_2_JSON(args.annotation)
    a = jsonObj.getJson()
    with open('./dataset/annotations/MVI_20011_v3.xml') as fd:
         doc = xmltodict.parse(fd.read())
    