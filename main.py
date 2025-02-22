# Import the necessary libraries
import cv_algorithms
import cv2
import numpy as np
from zhang_suen_node_detection import zhang_suen_node_detection
from breadth_first_edge_detection import breadth_first_edge_detection
from draw import draw_graph
import sys
from dijkstra_usage import dijkstra_shortest_path

img_path = sys.argv[1] if len(sys.argv) > 1 else None
# check if the image path is valid else skip to use image_orig from cv2.imread
if img_path:
    image_orig = cv2.imread(img_path)
else:
    print("Image path is not provided or invalid. Using images from ./z-input/")
    # Load any of the Google Maps screenshot
    # image_orig = cv2.imread("./z-input/kirba.png")
    image_orig = cv2.imread("./z-input/city-flyover.png")

# # Load the Google Maps screenshot
# image_orig = cv2.imread("./z-input/kirba.png")
# image_orig = cv2.imread("./z-input/city-flyover.png")
# image_orig = cv2.imread("./.research-dump/0-test3.png")

# preserve the original image for using as background when drawing the graph
# use this copy for image processing
image = image_orig.copy()

# detect highway roads and display them in white color
# take a HSV color space
lower_color = np.array([146, 200, 200])
upper_color = np.array([147, 255, 255])

mask = cv2.inRange(image, lower_color, upper_color)

# remove not long enough lines (dots of small area)
contours, _ = cv2.findContours(
    mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
for cnt in contours:
    if cv2.contourArea(cnt) < 5:
        cv2.drawContours(mask, [cnt], 0, (0, 0, 0), -1)

# using the mask image, replace the highway road color with white color
image[mask > 0] = (255, 255, 255)

# Threshold the image to get the roads(ROI) apart from non-white areas (like water bodies and other non-road areas)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)

# make the lines thicker to remove line breaks in between maps leafs
kernel = np.ones((2, 2), np.uint8)
dilated_img = cv2.dilate(thresh, kernel, iterations=1)

# add padding to get nodes from the image borders which start from white color
pad = 3
padded_dil = cv2.copyMakeBorder(
    dilated_img, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=[0, 0, 0])

# Perform thinning using Zhang-Suen algorithm
skeleton = cv_algorithms.zhang_suen(dilated_img)

# Or, Perform thinning using Zhang-suen thinning algorithm
# skeleton = cv_algorithms.guo_hall(padded_dil)

cv2.imwrite("./z-output/skeleton.png", skeleton)


# detect nodes
graph = zhang_suen_node_detection(skeleton)
# detect edges
graph = breadth_first_edge_detection(skeleton, graph)
# draw the graph

# add padding to the original image to draw the graph plots on it
image_orig = cv2.copyMakeBorder(
    image_orig, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=[0, 0, 0])
skeleton = cv2.cvtColor(skeleton, cv2.COLOR_GRAY2BGR)
graph_img = draw_graph(image_orig, graph)
# remove the padding
graph_img = graph_img[pad:-pad, pad:-pad]

# save the graph image
cv2.imwrite("./z-output/graph.png", graph_img)
print("Output image path: ./z-output/graph.png")

# Use the graph data to find the shortest path between two nodes using dijkstra's algorithm and draw the path on the original image
# print("Graph nodes: ", graph.nodes())
start_node = (53, 667)
end_node = (758, 1024)
dijkstra_output = dijkstra_shortest_path(graph, image_orig, start_node, end_node)
cv2.imwrite("./z-output/dijkstra.png", dijkstra_output)
