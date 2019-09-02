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
from skimage.viewer.widgets import Text, Slider
from skimage.viewer.qt import QtWidgets, QtCore
from skimage.viewer.canvastools import RectangleTool
from matplotlib.widgets import RectangleSelector
from skimage.viewer import CollectionViewer
from skimage.io import ImageCollection
from skimage.draw import line
from skimage.draw import set_color
from skimage.measure import points_in_poly
import numpy as np

YELLOW_COLOR = [255, 255, 35]
RED_COLOR    = [255, 0, 17]

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
        if not self.ax.in_axes(event):
            return
        else:
            if event.button == 3:
                 self.callback_on_move(x,y)
                 return
            if event.button == 1:
                self._set_active_handle(event)
                if self.active_handle is None:
                    # Clear previous rectangle before drawing new rectangle.
                    print('limpouuuuu')
                    self.set_visible(False)
                    self.redraw()
                self.set_visible(True)
                RectangleSelector.press(self, event)

    

class bboxBar(Text):
    def __init__(self, name=None, text=''):
        super(Text, self).__init__(name)
        self._label = QtWidgets.QLabel('x=0.0 y=0.0 width=0.0 heigth=0.0')
        #self._label.seText = 'X=0.0 Y=0.0'
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self._label)

        self.layout.setAlignment(QtCore.Qt.AlignLeft)


class detracCollectionViewer(CollectionViewer):
    def __init__(self, full_annotations, path_dataset, path_annotations, update_on='move'):
        self.filename = full_annotations[0][0] # get file name
        name, extension = self.filename.split(".")
        self.image_collection = ImageCollection(path_dataset + '/' + name +  '/img*.jpg')
        self.num_images = len(self.image_collection)
        self.index = 0

        first_image = self.image_collection[0]
        super(CollectionViewer, self).__init__(first_image)
        self.xmlObj = CollectionAnnotation(path_annotations + '/' + self.filename)

        self._plotAnnotation(self.index + 1)
        #self.loadIgnoredRegions()
        #self._plotIgnoredRegions()

        slider_kws = dict(value=0, low=0, high=self.num_images - 1)
        slider_kws['update_on'] = update_on
        slider_kws['callback'] = self.update_index
        slider_kws['value_type'] = 'int'
        self.slider = Slider('frame', **slider_kws)
        self.layout.addWidget(self.slider)

        self.box_coord = bboxBar()
        self.layout.addWidget(self.box_coord)
        


    def update_index(self, name, index):
        """Select image on display using index into image collection."""
        if index == self.index:
            return

        # clip index value to collection limits
        index = max(index, 0)
        index = min(index, self.num_images -1)

        self.index = index
        self.slider.val = index
        self.update_image(self.image_collection[index])
        self._plotAnnotation(index + 1)
        #self._plotIgnoredRegions()
       

    
    def _plotAnnotation(self, idx):
        boxes = self.xmlObj.getBBoxes(idx)
        if len(boxes) > 0:
            self._bboxes = []
            self.box = []
            for b in boxes:
                frame_id = b[0]
                box_id = b[1]
                car_type = b[11]
                car_color = b[6]
                x1 = b[3] #left
                y1 = b[4] #top
                x2 = b[5] #width
                y2 = b[2] #heigth
    
                self.box = (x1, y1, x2, y2)
                xmin, xmax = sorted([x1, x1 + x2])
                ymin, ymax = sorted([y1, y1 + y2])
                coord = (xmin, xmax, ymin, ymax)
                self._bboxes.append([frame_id, box_id, car_type, car_color, [xmin,ymin,xmax,ymax]])
                #self._bboxes.append([frame_id, box_id, car_type, car_color, [[xmin,ymin],[xmax, ymin], [xmax, ymax], [xmin, ymax]]])
                
                self.plot_rect(coord)
            print(sorted(self._bboxes))
    
    def loadIgnoredRegions(self):
        ig = self.xmlObj.getIgnoredRegion()
        if len(ig) > 0:
            self._ignoredRegions = []
            self.box = []
            for b in ig:
                x1 = b['left']
                y1 = b['top']
                x2 = b['width']
                y2 = b['height']
    
                self.box = (x1, y1, x2, y2)
                xmin, xmax = sorted([x1, x1 + x2])
                ymin, ymax = sorted([y1, y1 + y2])
                coord = (xmin, xmax, ymin, ymax)
                self._ignoredRegions.append([x1,y1,x2,y2])
                self.plot_rect(coord)        
        
    def _plotIgnoredRegions(self):
        for each in self._ignoredRegions:
            xmin, xmax = sorted([each[0], each[0] + each[2]])
            ymin, ymax = sorted([each[1], each[1] + each[3]])
            coord = (xmin, xmax, ymin, ymax)
            self.plot_rect(coord, RED_COLOR)
    
    def plot_rect(self, extents, color=YELLOW_COLOR, newBox=False):
        im = self.image
        coord = np.int64(extents)
        
        [rr1, cc1] = line(coord[2],coord[0],coord[2],coord[1])
        [rr2, cc2] = line(coord[2],coord[1],coord[3],coord[1])
        [rr3, cc3] = line(coord[3],coord[1],coord[3],coord[0])
        [rr4, cc4] = line(coord[3],coord[0],coord[2],coord[0])
        set_color(im, (rr1, cc1), color)
        set_color(im, (rr2, cc2), color)
        set_color(im, (rr3, cc3), color)
        set_color(im, (rr4, cc4), color)
        #viewer.image=im
        self.update_image(im)
        if newBox:
            self.xmlObj.saveNewBBox(self.index + 1, coord)

    def detectBBox(self, x,y):
        for v in self._bboxes:
            if ((x >= v[4][0]) and (x <= v[4][2]) and (y >= v[4][1] and y <= v[4][3])):
                print('DENTRO: {}'.format(v[4]))
                self.plot_rect((v[4][0], v[4][2], v[4][1], v[4][3]), RED_COLOR)
                return
            
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
        attribute.attrib["trajectory_length"] = '{}'.format("0")
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
    
    
    
    
    