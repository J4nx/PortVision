import numpy as np

'''This script contains functions to create post-process bounding boxes for LAN ports and LAN port stacks. 
Note that the functions are not complete and need to be integrated into the main codebase.'''

# Funktio, joka laskee bounding boxin keskikohdan x-akselilla
def get_center_x(bbox):
    x_min, y_min, x_max, y_max = bbox
    return (x_min + x_max) / 2

# Funktio, joka laskee bounding boxin keskikohdan y-akselilla
def get_center_y(bbox):
    x_min, y_min, x_max, y_max = bbox
    return (y_min + y_max) / 2

# Funktio, joka tarkistaa, onko portin tai kaapelin bounding box stackin sisällä
def is_inside(inner_box, outer_box):
    x1, y1, x2, y2 = map(int, inner_box)
    X1, Y1, X2, Y2 = map(int, outer_box)
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    return X1 <= mid_x <= X2 and Y1 <= mid_y <= Y2

# Funktio, joka ryhmittelee LAN port stackin sisäiset portit kytkimessä
def group_lan_ports_within_stack(stack_bboxes, port_bboxes):
    stacks = []
    for stack_bbox in stack_bboxes:
        stack_ports = []
        for port_bbox in port_bboxes:
            if is_within_stack(stack_bbox, port_bbox):
                stack_ports.append(port_bbox)
        stacks.append((stack_bbox, stack_ports))
    return stacks

# Funktio, joka tarkistaa, onko portin bounding box stackin sisällä
def is_within_stack(stack_bbox, port_bbox):
    stack_x_min, stack_y_min, stack_x_max, stack_y_max = stack_bbox
    port_x_min, port_y_min, port_x_max, port_y_max = port_bbox

    return (stack_x_min <= port_x_min <= stack_x_max and
            stack_x_min <= port_x_max <= stack_x_max and
            stack_y_min <= port_y_min <= stack_y_max)

# Funktio, joka järjestää bounding boxit x-akselilla ja lisää puuttuvat boxit
def process_lan_ports(stacks, ports_per_row=6):
    processed_bboxes = []
    for stack_bbox, port_bboxes in stacks:
        port_bboxes = sorted(port_bboxes, key=lambda bbox: get_center_x(bbox))
        processed_bboxes.extend(port_bboxes)
        
        if len(port_bboxes) < ports_per_row:
            for i in range(len(port_bboxes), ports_per_row):
                new_bbox = create_unlabeled_bbox(stack_bbox, i, ports_per_row)
                processed_bboxes.append(new_bbox)  # Unlabeled box
    
    return processed_bboxes

# Funktio, joka luo "unlabeled" bounding boxin koordinaattien perusteella
def create_unlabeled_bbox(stack_bbox, index, ports_per_row):
    stack_x_min, stack_y_min, stack_x_max, stack_y_max = stack_bbox
    port_width = (stack_x_max - stack_x_min) / ports_per_row
    
    new_x_min = stack_x_min + index * port_width
    new_x_max = new_x_min + port_width
    new_y_min = stack_y_min
    new_y_max = new_y_min + (stack_y_max - stack_y_min) / 2  # Oletus, että portti on yläreunassa
    
    return (new_x_min, new_y_min, new_x_max, new_y_max)
