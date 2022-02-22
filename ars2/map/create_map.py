import numpy as np
from matplotlib import pyplot as plt
from roipoly import MultiRoi
import json

import sys

if len(sys.argv)<2:
    print("Provide a file name for the map!")
    sys.exit()

map_name = sys.argv[1]

# Create image
img = np.zeros((100, 100))

# Show the image
fig = plt.figure()
plt.imshow(img, interpolation='nearest', cmap="Greys")
plt.title("Click on the button to add a new ROI")

# Draw multiple ROIs
multiroi_named = MultiRoi(roi_names=['My first ROI', 'My second ROI'])


with open(map_name, mode='wt', encoding='utf-8') as myfile:

    for name,roi in multiroi_named.rois.items():
        roi_coordinates = roi.get_roi_coordinates()
        json_string = json.dumps(roi_coordinates)
        myfile.write(json_string)
        myfile.write("\n")