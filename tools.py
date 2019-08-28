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

class CollectionAnnotation:
    
    def __init__(self, path):
        dirs, filename = os.path.split(path)
        name, extension = filename.split(".")
        self.json_file = name + '.json'
        if filename.endswith(".xml"):
            self._loadAsXML(path)
        else:
            self.loadAsJson(path, self.json_file)
    
    def getJson(self):
        with open(self.json_file, 'r') as f:
            collection = json.load(f)
        return collection
    
    def _loadAsJson(self, path, json_file):
        with open(path) as fd:
            doc = xmltodict.parse(fd.read())
        
        json_data = json.dumps(doc, sort_keys=True, indent=2)
        json_data_processed = re.sub('."@', '"', json_data) 

        output_file = open(json_file, 'w')
        output_file.write(json_data_processed)
        
    
    def _loadAsXML(self, path):
        dirs, filename = os.path.split(path)
        name, extension = filename.split(".")
        if filename.endswith(".xml"):
            tree = ET.parse(path)
            self.root = tree.getroot()

    def getBBoxes(self, i):
        bboxes = []
        for frames in self.root.iter('frame'):
           frame_idx = int(frames.get('num'))
           if (frame_idx == i):
               #print('frame:', frame_idx)
               for targets in frames.iter('target'):
                   id = int(targets.get('id'))
                   car_attrib = targets[1].attrib
                   for e in targets.iter('box'):
                       #print(e.attrib)
                       bboxes.append([frame_idx, id, car_attrib['vehicle_type'], car_attrib['color'], e.attrib])
               
        return bboxes
    
if __name__ == '__main__':

    # initiate the parser
    parser = argparse.ArgumentParser(prog='XML_2_JSON', usage='%(prog)s [options]', description='Convert a xml file to a json file.')
    parser.add_argument("--annotation", help="path to xml file", default='./dataset/annotations/MVI_20011.xml')
    args = parser.parse_args()
# =============================================================================
#     jsonObj = XML_2_JSON(args.annotation)
#     a = jsonObj.getJson()
#     with open('./dataset/annotations/MVI_20011_v3.xml') as fd:
#          doc = xmltodict.parse(fd.read())
# =============================================================================
    jsonObj = CollectionAnnotation(args.annotation)
    a = jsonObj.getBBoxes(1)
    
    