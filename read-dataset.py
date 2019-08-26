# include standard modules
from skimage.viewer import ImageViewer, CollectionViewer
from skimage.viewer.plugins.lineprofile import LineProfile
from skimage.viewer.widgets import Slider
from skimage.io.collection import alphanumeric_key
from skimage.viewer.canvastools import RectangleTool
from skimage.draw import line
from skimage.draw import set_color

import pandas as pd
import numpy as np
import skimage.io as io
import argparse
import os
import sys

# initiate the parser
parser = argparse.ArgumentParser(prog='read-au-detrac', usage='%(prog)s [options]', description='Shows each annotated image at au-detrac data set.')
parser.add_argument("--dataset", help="dataset directory", default='./dataset/images')
parser.add_argument("--annotation", help="annotation directory", default='./dataset/annotations')
parser.add_argument('--version', action='version', version='%(prog)s 0.1')

# read arguments from the command line
args = parser.parse_args()
PATTERN_ANNOTATION = '_Det_R-CNN.txt'
PATH_ANNOTATIONS = args.annotation
PATH_DATASET = args.dataset

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

def getDirs(path):
    annotations = 0
    num_images = 0
    with os.scandir(path) as entries:
        entries = sorted(entries, key=lambda e: e.name)
        for entry in entries:
            if entry.is_dir(follow_symlinks=False):
                files = os.scandir(entry)
                getFiles(files)
                images_ordered = sorted(images, key=alphanumeric_key)
                full_annotations.append([entry.name,images_ordered.copy(), len(images_ordered)])
                num_images = num_images + len(images_ordered)
                images.clear()
        annotations = len(full_annotations)
    return annotations, num_images

               
            
class detracCollectionViewer(CollectionViewer):
    def __init__(self, full_annotations, update_on='move'):
        self.annotation_file_name = full_annotations[0][0]
        self.image_collection = io.ImageCollection(PATH_DATASET + '/' + self.annotation_file_name +  '/img*.jpg')
        self.num_images = len(self.image_collection[0])
        self.index = 0

        first_image = self.image_collection[0]
        self.annotation_pointer = self.loadAnnotation(self.annotation_file_name)
        #self.frame_annotation = self.getAnnotation(self.index + 1)
        #print(boxes_coord.to_string(index=False))
        #print(boxes_coord)
        
        super(CollectionViewer, self).__init__(first_image)
        #self.plotBoxes(self.frame_annotation)

        slider_kws = dict(value=0, low=0, high=self.num_images - 1)
        slider_kws['update_on'] = update_on
        slider_kws['callback'] = self.update_index
        slider_kws['value_type'] = 'int'
        self.slider = Slider('frame', **slider_kws)
        self.layout.addWidget(self.slider)

    def update_index(self, name, index):
        """Select image on display using index into image collection."""
        index = int(round(index))

        if index == self.index:
            return

        # clip index value to collection limits
        index = max(index, 0)
        index = min(index, self.num_images - 1)

        self.index = index
        self.slider.val = index
        self.update_image(self.image_collection[index])
        self.frame_annotation = self.getAnnotation(index + 1)
        self.plotBoxes(self.frame_annotation)
    
    def loadAnnotation(self, name):
        file_name = PATH_ANNOTATIONS + '/' + name + PATTERN_ANNOTATION
        return pd.read_table(file_name, delimiter=',', header=None, names=['Frame','Class','x1','y1','x2','y2','None'])
    
    def getAnnotation(self, idx):
        bboxes = (self.annotation_pointer[self.annotation_pointer['Frame'] == idx])[['x1','y1','x2','y2']]
        #df[df['CLASS']==1]['CONTENT'] 
        #a = self.annotation_pointer['x1','y1','x2','y2'] #[(self.annotation_pointer['Frame'] == idx)]
        return bboxes
    
    def plotBoxes(self, bboxes):
        for index, row in bboxes.iterrows():
            '''(xmin, xmax, ymin, ymax)'''
            xmin, xmax = sorted([row['x1'], row['x1'] + row['x2']])
            ymin, ymax = sorted([row['y1'], row['y1']+ row['y2']])
            
            coord = (xmin, xmax, ymin, ymax)
            self.plot_rect(coord)
            
    
    def plot_rect(self, extents):
        im = self.image
        coord = np.int64(extents)
        [rr1, cc1] = line(coord[2],coord[0],coord[2],coord[1])
        [rr2, cc2] = line(coord[2],coord[1],coord[3],coord[1])
        [rr3, cc3] = line(coord[3],coord[1],coord[3],coord[0])
        [rr4, cc4] = line(coord[3],coord[0],coord[2],coord[0])
        set_color(im, (rr1, cc1), [255, 255, 35])
        set_color(im, (rr2, cc2), [255, 255, 35])
        set_color(im, (rr3, cc3), [255, 255, 35])
        set_color(im, (rr4, cc4), [255, 255, 35])
        #viewer.image=im
        self.update_image(im)
        #print(extents) #x1
        

        
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
    viewer.show()
    #viewer += LineProfile(viewer)
    #overlay, data = viewer.show()[0]
    sys.exit(viewer.exec_())
