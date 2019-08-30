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
from skimage.viewer.widgets import Text
from skimage.viewer.qt import QtWidgets, QtCore
from skimage.viewer.canvastools import RectangleTool

class rectangle(RectangleTool):
    def on_key_press(self, event):
        if event.key == 'enter':
            self.callback_on_enter(self.geometry, newBox=True)
            self.set_visible(False)
            self.manager.redraw()
            print('coordenadas: ', type(self._extents_on_press))
    
# =============================================================================
#     def on_move(self, event):
#         if self.eventpress is None or not self.ax.in_axes(event):
#             return
# 
#         if self.active_handle is None:
#             # New rectangle
#             x1 = self.eventpress.xdata
#             y1 = self.eventpress.ydata
#             x2, y2 = event.xdata, event.ydata
#         else:
#             x1, x2, y1, y2 = self._extents_on_press
#             if self.active_handle in ['E', 'W'] + self._corner_order:
#                 x2 = event.xdata
#             if self.active_handle in ['N', 'S'] + self._corner_order:
#                 y2 = event.ydata
#         self.extents = (x1, x2, y1, y2)
#         self.callback_on_move(self.geometry)    
# =============================================================================


class bboxBar(Text):
    def __init__(self, name=None, text=''):
        super(Text, self).__init__(name)
        self._label = QtWidgets.QLabel('X')
        #self.text = '0.0'
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self._label)

        _labelx1_value = QtWidgets.QLabel()
        _labelx1_value.setText('0.0')
        self.layout.addWidget(_labelx1_value)
        
        
        _labely1 = QtWidgets.QLabel()
        _labely1.setText('Y')
        self.layout.addWidget(_labely1)
        
        _labely1_value = QtWidgets.QLabel()
        _labely1_value.setText('0.0')
        self.layout.addWidget(_labely1_value)

        _labelw = QtWidgets.QLabel()
        _labelw.setText('width')
        self.layout.addWidget(_labelw)
        
        _labelw_value = QtWidgets.QLabel()
        _labelw_value.setText('0.0')
        self.layout.addWidget(_labelw_value)        
        
        _labelh = QtWidgets.QLabel()
        _labelh.setText('H')
        self.layout.addWidget(_labelh)        

        _labelh_value = QtWidgets.QLabel()
        _labelh_value.setText('0.0')
        self.layout.addWidget(_labelh_value)        
        

        self.layout.setAlignment(QtCore.Qt.AlignLeft)


class CollectionAnnotation:
    
    def __init__(self, path):
        self.path = path
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
            self.tree = ET.parse(path)
            self.root = self.tree.getroot()

# =============================================================================
#     def getBBoxes(self, i):
#         bboxes = []
#         for frames in self.root.iter('frame'):
#            frame_idx = int(frames.get('num'))
#            if (frame_idx == i):
#                #print('frame:', frame_idx)
#                for targets in frames.iter('target'):
#                    id = int(targets.get('id'))
#                    print(targets)
#                    car_attrib = targets[1].attrib
#                    for e in targets.iter('box'):
#                        height_value = float(e.attrib['height'])
#                        #print(type(int(float(height_value))))
#                        left_value = float(e.attrib['left'])
#                        top_value = float(e.attrib['top'])
#                        width_value  = float(e.attrib['width'])
#                        bboxes.append([frame_idx, id, car_attrib['vehicle_type'], car_attrib['color'], {'height': height_value, 'left': left_value, 'top': top_value, 'width': width_value}])
# 
#         return bboxes
# =============================================================================
    
    def getBBoxes(self, frm_id):
        bboxes = []
        target_list = self.root.findall('./frame[@num="{}"]/target_list/target/...'.format(frm_id))
        for target in target_list[0]:
            target_id = int(target.get('id'))
            for element in target:
                color = ''
                orientation = ''
                speed = ''
                trajectory_length = ''
                truncation_ratio = ''
                vehicle_type = ''
                if element.tag == 'box':
                    left_value  = float(element.get('left'))
                    width_value = float(element.get('width'))
                    top_value   = float(element.get('top'))
                    height_value= float(element.get('height'))
                elif element.tag == 'attribute':
                    color = '{}'.format(element.get('color'))
                    orientation = '{}'.format(float(element.get('orientation')))
                    speed = '{}'.format(float(element.get('speed')))
                    trajectory_length = '{}'.format(element.get('trajectory_length'))
                    truncation_ratio = '{}'.format(float(element.get('truncation_ratio')))
                    vehicle_type = '{}'.format(element.get('vehicle_type'))
                
                bboxes.append([frm_id, target_id, vehicle_type, color, {'height': height_value, 'left': left_value, 'top': top_value, 'width': width_value}, {'color': color, 'orientation': orientation, 'speed': speed, 'trajectory_length': trajectory_length, 'truncation_ratio': truncation_ratio, 'vehicle_type': vehicle_type}])           
        return bboxes    
    
    def getIgnoredRegion(self):
        ignoredRegions = []
        for igs in self.root.iter('ignored_region'):
            for e in igs.iter('box'):
                height_value = float(e.attrib['height'])
                left_value = float(e.attrib['left'])
                top_value = float(e.attrib['top'])
                width_value  = float(e.attrib['width'])
                ignoredRegions.append({'height': height_value, 'left': left_value, 'top': top_value, 'width': width_value})

        return ignoredRegions
    
    def saveNewBBox(self, frm_id, bbox):
        '''  (x1, x2, y1, y2) = bbox '''
        obj_target_parent = self.root.find('./frame[@num="{}"]/target_list/target/...'.format(frm_id))
        #print(type(obj_target_parent))
        #print(len(obj_target_parent))
        target = ET.SubElement(obj_target_parent, 'target')
        target_id = len(obj_target_parent)
        target.attrib["id"] = '{}'.format(target_id)
        target.text = "\n\t" #break down line
        #print(len(obj_target_parent))
        
        obj_target_inserted = self.root.find('./frame[@num="{}"]/target_list/target[@id="{}"]'.format(frm_id,target_id))
        #print(type(obj_target_inserted))

        box = ET.SubElement(obj_target_inserted, 'box')

        box.attrib["height"] = '{}'.format(bbox[3] - bbox[2])
        box.attrib["left"] = '{}'.format(bbox[0])
        box.attrib["top"] = '{}'.format(bbox[2])
        box.attrib["width"] = '{}'.format(bbox[1] - bbox[0])
        #box.text = "\n\t" #break down line
        box.tail = "\n\t"
      
        attribute = ET.SubElement(obj_target_inserted, 'attribute')
        attribute.attrib["color"] = '{}'.format("Silver")
        attribute.attrib["orientation"] = '{}'.format("0.0")
        attribute.attrib["speed"] = '{}'.format("0.0")
        attribute.attrib["trajectory_length"] = '{}'.format("0.0")
        attribute.attrib["truncation_ratio"] = '{}'.format("0.0")
        attribute.attrib["vehicle_type"] = '{}'.format("0.0")
        attribute.tail = "\n\t"

      
        obj_target_parent = self.root.find('./frame[@num="{}"]/target_list/...'.format(frm_id))
        obj_target_parent.attrib["density"] = '{}'.format(target_id)
        print(obj_target_parent.attrib["density"])
      
        #print(ET.tostring(self.root, encoding='utf8').decode('utf8'))
        self.__saveXML()
                  
    def __saveXML(self):
        self.tree.write(self.path)
    
if __name__ == '__main__':

    # initiate the parser
    parser = argparse.ArgumentParser(prog='XML_2_JSON', usage='%(prog)s [options]', description='Convert a xml file to a json file.')
    parser.add_argument("--annotation", help="path to xml file", default='./teste.xml')
    args = parser.parse_args()
# =============================================================================
#     jsonObj = XML_2_JSON(args.annotation)
#     a = jsonObj.getJson()
#     with open('./dataset/annotations/MVI_20011_v3.xml') as fd:
#          doc = xmltodict.parse(fd.read())
# =============================================================================
    jsonObj = CollectionAnnotation(args.annotation)
    a = jsonObj.getBBoxes(1)
    #a = jsonObj.getIgnoredRegion()
    #jsonObj.saveNewBBox(1,1)
    
  

    #print(a[0][4]['height'])
    #print(a[0]['height'])
    
    
    
    
    