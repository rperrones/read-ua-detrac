# include standard modules
from tools import rectangle, detracCollectionViewer


#from skimage.viewer.plugins.lineprofile import LineProfile

from skimage.io.collection import alphanumeric_key
#from skimage.viewer.canvastools import RectangleTool



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
    viewer = detracCollectionViewer(full_annotations, PATH_DATASET, PATH_ANNOTATIONS)
    #viewer.update_index
    rect_tool = rectangle(viewer, on_enter=viewer.plot_rect, on_move=viewer.detectBBox)

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
    

