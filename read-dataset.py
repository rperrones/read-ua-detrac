# include standard modules
from skimage.viewer import ImageViewer, CollectionViewer
from skimage.viewer.plugins.lineprofile import LineProfile
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
PATTERN_ANNOTATION = '_Det_R-CNN.txt'

# check for --version or -V
#if args.version:
#    print("This is the version 0.1 of the read-au-detrac program.")
images = []
videos = []
def getFiles(files):
    for file in files:
            if file.is_file(): 
                f = file.name.lower()
                if f.endswith('.jpg'):
                    images.append(file.name)

def getDirs(path):
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_dir(follow_symlinks=False):
                files = os.scandir(entry)
                getFiles(files)
                videos.append([entry.name + PATTERN_ANNOTATION,images.copy()])
                images.clear()
              
            print(entry.name)    

dataset_path = args.dataset
getDirs(dataset_path)

#your path 
img_dir = './dataset/images/MVI_20011'

#creating a collection with the available images
images = io.ImageCollection(img_dir + '/img*.jpg')
#viewer = ImageViewer(images[0])
viewer = CollectionViewer(images)
viewer.show()
#viewer += LineProfile(viewer)
#overlay, data = viewer.show()[0]

