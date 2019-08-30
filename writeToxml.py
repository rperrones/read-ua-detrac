import xml.etree.ElementTree as ET
from xml.dom import minidom

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    #return reparsed.toprettyxml(indent=" ")
    return reparsed.toxml()


tree = ET.parse('teste.xml')
xmlRoot = tree.getroot()


for frames in xmlRoot.iter('frame'):
   frame_idx = int(frames.get('num'))
   if (frame_idx == 1):
          obj_target_parent = frames.find('./target_list/target/...')
          
          target = ET.SubElement(obj_target_parent, 'target')
          target_id = len(obj_target_parent)
          target.attrib["id"] = '{}'.format(target_id)
          target.text = "\n\t" #break down line
          
          obj_target_inserted = frames.find('./target_list/target[@id="{}"]'.format(target_id))


          box = ET.SubElement(obj_target_inserted, 'box')

          box.attrib["height"] = '{}'.format('0.0')
          box.attrib["left"] = '{}'.format('0.0')
          box.attrib["top"] = '{}'.format('0.0')
          box.attrib["width"] = '{}'.format('0.0')
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

          
          frames.attrib["density"] = '{}'.format(len(obj_target_parent))
# =============================================================================
#            height_value = float(e.attrib['height'])
#            #print(type(int(float(height_value))))
#            left_value = float(e.attrib['left'])
#            top_value = float(e.attrib['top'])
#            width_value  = float(e.attrib['width'])
#            #bboxes.append([frame_idx, id, car_attrib['vehicle_type'], car_attrib['color'], {'height': height_value, 'left': left_value, 'top': top_value, 'width': width_value}])
#            
# =============================================================================






#child = ET.Element("NewNode")
#child = ET.SubElement(xmlRoot, 'child')
#child.text = 'This child contains text.'

#xmlRoot.append(child)
doc = ET.tostring(xmlRoot, encoding='utf8').decode('utf8')
print(doc)
tree.write('output.xml')
