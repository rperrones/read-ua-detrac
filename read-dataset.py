# include standard modules
import argparse
import os

# initiate the parser
parser = argparse.ArgumentParser(prog='read-au-detrac', usage='%(prog)s [options]', description='Shows each annotated image at au-detrac data set.')
#parser.add_argument("-V", "--version", help="show program version", action="store_true")
parser.add_argument("--dataset", help="dataset directory", default='./dataset/images')
parser.add_argument("--annotation", help="annotation directory", default='./dataset/annotations')
parser.add_argument('--version', action='version', version='%(prog)s 0.1')

# read arguments from the command line
args = parser.parse_args()

# check for --version or -V
#if args.version:
#    print("This is the version 0.1 of the read-au-detrac program.")
images = []
annotations = []
videos = []
def getFiles(entry):
    files = os.scandir(entry)
    for file in files:
            if file.is_file(): 
                f = file.name.lower()
                if f.endswith('.jpg'):
                    images.append(file.name)
                elif f.endswith('.txt'):
                    annotations.append(file.name)
                print(file.name)

def getDirs(path):
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_dir(follow_symlinks=False):
                getFiles(entry)
                videos.append([entry.name,images])
            print(entry.name)    

dataset_path = args.dataset
annotation_path = args.annotation
getDirs(dataset_path)
getDirs(annotation_path)