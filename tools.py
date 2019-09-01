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
from matplotlib.widgets import RectangleSelector
import numpy as np

class rectangle(RectangleTool):
    def on_key_press(self, event):
        if event.key == 'enter':
            self.callback_on_enter(self.geometry, newBox=True)
            self.set_visible(False)
            self.manager.redraw()
            print('coordenadas: ', type(self._extents_on_press))
    
    def on_mouse_press(self, event):
        #if event.button != 1 or not self.ax.in_axes(event):
        #    return
        #if event.button == 0:
        print('botao:', event.button)
        print('is_in_axs:', self.ax.in_axes(event))
        x, y = event.xdata, event.ydata
        print('[{},{}]'.format(x,y))

        self._set_active_handle(event)
        if self.active_handle is None:
            # Clear previous rectangle before drawing new rectangle.
            print('limpouuuuu')
            self.set_visible(False)
            self.redraw()
        self.set_visible(True)
        RectangleSelector.press(self, event)
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

    def getBBoxes(self, frm_id):
        target_list = self.root.findall('./frame[@num="{}"]/target_list/target/...'.format(frm_id))
        size = len(target_list[0])
        bbox = np.ndarray((size, 12), dtype=np.object) # lines refer to the quantity of boxes and columns to attributes
        for i, target in enumerate(target_list[0], start=0):
            target_id = int(target.get('id'))
            bbox[i,0] = int(frm_id)
            bbox[i,1] = target_id
            for element in target:
                if element.tag == 'box':
                    bbox[i,2] = float(element.get('height'))
                    bbox[i,3] = float(element.get('left'))
                    bbox[i,4] = float(element.get('top'))
                    bbox[i,5] = float(element.get('width'))
                elif element.tag == 'attribute':
                    bbox[i,6] = np.str(element.get('color'))
                    bbox[i,7] = np.float(element.get('orientation'))
                    bbox[i,8] = np.float(element.get('speed'))
                    bbox[i,9] = np.int32(element.get('trajectory_length'))
                    bbox[i,10] = np.float(element.get('truncation_ratio'))
                    bbox[i,11] = np.str(element.get('vehicle_type'))
        return bbox
    
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
        attribute.attrib["vehicle_type"] = '{}'.format("Car")
        attribute.tail = "\n\t"

      
        obj_target_parent = self.root.find('./frame[@num="{}"]/target_list/...'.format(frm_id))
        obj_target_parent.attrib["density"] = '{}'.format(target_id)
        print('quantidade de box atuais:', obj_target_parent.attrib["density"])
      
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
    
    
    
    
    