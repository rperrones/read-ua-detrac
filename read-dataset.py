# include standard modules
import xml.etree.ElementTree as ET
from tools import CollectionAnnotation, bboxBar

from skimage.viewer import ImageViewer, CollectionViewer
from skimage.viewer.plugins.lineprofile import LineProfile
from skimage.viewer.widgets import Slider
from skimage.io.collection import alphanumeric_key
from skimage.viewer.canvastools import RectangleTool
from skimage.draw import line
from skimage.draw import set_color


import numpy as np
import skimage.io as io
import argparse
import os


# initiate the parser
parser = argparse.ArgumentParser(prog='read-au-detrac', usage='%(prog)s [options]', description='Shows each annotated image at au-detrac data set.')
parser.add_argument("--dataset", help="dataset directory", default='./dataset/images')
parser.add_argument("--annotation", help="annotation directory", default='./dataset/annotations')
parser.add_argument('--version', action='version', version='%(prog)s 0.1')

# read arguments from the command line
args = parser.parse_args()
SUFFIX_ANNOTATION = '_v3.xml'
PATH_ANNOTATIONS = args.annotation
PATH_DATASET = args.dataset
YELLOW_COLOR = [255, 255, 35]
RED_COLOR    = [255, 0, 17]


# check for --version or -V
#if args.version:
#    print("This is the version 0.1 of the read-au-detrac program.")
images = []
full_annotations = []
def getFiles(files):
    for file in files:
            if file.is_file(): 
                f = file.name.lower()
                if f.endswith('.jpg'):
                    images.append(file.name)

def getDirs(pathDataset):
    annotations = 0
    num_images = 0
    with os.scandir(pathDataset) as entries:
        entries = sorted(entries, key=lambda e: e.name)
        for entry in entries:
            if entry.is_dir(follow_symlinks=False):
                files = os.scandir(entry)
                getFiles(files)
                images_ordered = sorted(images, key=alphanumeric_key)
                full_annotations.append([entry.name + '.xml',images_ordered.copy(), len(images_ordered)])
                #print(entry.name, len(images_ordered))
                num_images = num_images + len(images_ordered)
                images.clear()
        annotations = len(full_annotations)
    return annotations, num_images



               
            
class detracCollectionViewer(CollectionViewer):
    def __init__(self, full_annotations, update_on='move'):
        self.filename = full_annotations[20][0] # get file name
        name, extension = self.filename.split(".")
        self.image_collection = io.ImageCollection(PATH_DATASET + '/' + name +  '/img*.jpg')
        self.num_images = len(self.image_collection)
        self.index = 0

        first_image = self.image_collection[0]
        super(CollectionViewer, self).__init__(first_image)
        #self.xmlObj = self._loadAnnotation(self.filename)
        self.xmlObj = CollectionAnnotation(PATH_ANNOTATIONS + '/' + self.filename)
        print(self.filename)
        self._plotAnnotation(self.index + 1)
        self.loadIgnoredRegions()
        self._plotIgnoredRegions()

        slider_kws = dict(value=1, low=1, high=self.num_images)
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
        index = max(index, 1)
        index = min(index, self.num_images)

        self.index = index
        self.slider.val = index
        self.update_image(self.image_collection[index -1])
        self._plotAnnotation(index)
        self._plotIgnoredRegions()
       

    
    def _plotAnnotation(self, idx):
        boxes = self.xmlObj.getBBoxes(idx)
        if len(boxes) > 0:
            self._bboxes = []
            self.box = []
            for b in boxes:
                frame_id = b[0]
                box_id = b[1]
                car_type = b[2]
                car_color = b[3]
                x1 = b[4]['left']
                y1 = b[4]['top']
                x2 = b[4]['width']
                y2 = b[4]['height']
    
                self.box = (x1, y1, x2, y2)
                xmin, xmax = sorted([x1, x1 + x2])
                ymin, ymax = sorted([y1, y1 + y2])
                coord = (xmin, xmax, ymin, ymax)
                self._bboxes.append([frame_id, box_id, car_type, car_color, [x1,y1,x2,y2]])
                self.plot_rect(coord)
    
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
    
    def plot_rect(self, extents, color=YELLOW_COLOR):
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
        #print(extents) #x1
        
    def plotBBoxes(self,coord):
        return 0
        
if __name__ == '__main__':
    #app = QApplication(sys.argv)
    #ex = Example()
    
    total_annotation, total_images = getDirs(PATH_DATASET)
    print('Total of video annotations: {}'.format(total_annotation))
    print('Total of images in dataset: {}'.format(total_images))
    #your path 
    #img_dir = './dataset/images/MVI_20011' 

    #creating a collection with the available images
    #images = io.ImageCollection(img_dir + '/img*.jpg')
    #viewer = ImageViewer(images)
    #viewer = CollectionViewer(images)
    #viewer = detracCollectionViewer(images)
    viewer = detracCollectionViewer(full_annotations)
    viewer.update_index
    rect_tool = RectangleTool(viewer, on_enter=viewer.plot_rect)
    print(rect_tool.geometry)
    viewer.show()
    #print(rect_tool._extents_on_press)
    #viewer += LineProfile(viewer)
    #overlay, data = viewer.show()[0]
   # sys.exit(viewer.exec_())
    #xml_data = 'dataset/annotations/MVI_20011.xml'
    #xmlObj = CollectionAnnotation(xml_data)
    #bboxes = xmlObj.getBBoxes(1)
    #print(bboxes[0][4]['height'])
    #print(bboxes)
    

