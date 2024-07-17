import pydicom
import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
import imutils

def plot_measurments(maskname, savename = '', radius=40, plot=False, cmap='jet', modefied=True, imname='',alpha=1, mode=0):
    plt.figure(dpi=200)
    dicom = True
    try:
        pydicom.dcmread(maskname)
    except:
        dicom = False
    # Get target pixels
    if dicom:
        ds = pydicom.dcmread(maskname)
        pixel_spacings = ds.ImagerPixelSpacing # 0.16mm
        assert pixel_spacings[0] == pixel_spacings[1], "Pixel spacings are not equal."
        mask = ((ds.pixel_array/ds.pixel_array.max())*255).astype(np.uint8)
    else:
        mask = cv.imread(maskname, cv.IMREAD_GRAYSCALE)
    left_contour, right_contour = get_left_and_right_contours(mask)
    all_contours = []
    all_contours.extend(left_contour)
    all_contours.extend(right_contour)
    all_contours = np.array(all_contours)
    l,r = get_target_points_final(left_contour, right_contour, modefied = modefied)
    left_lung_apex, left_lung_base, left_mid_point, left_highest_point, left_centroid,left_width_point,left_width_base_point, left_base_modified =l 
    right_lung_apex, right_lung_base, right_mid_point, right_highest_point, right_centroid,right_width_point,right_width_base_point, right_base_modified = r
    if mode == 1:
        left_lung_apex = left_highest_point
        right_lung_apex= right_highest_point
    im_points   = np.zeros(mask.shape).astype(np.float32) ; color_points   = 0
    im_lines    = np.zeros(mask.shape).astype(np.float32) ; color_lines    = 1
    im_contours = np.zeros(mask.shape).astype(np.float32) ; color_contours = 0
    im_center   = np.zeros(mask.shape).astype(np.float32) ; color_center   = 0
    # Contours 
    cv.drawContours(im_contours, [right_contour], -1, color_contours, thickness = int(radius*0.6));
    cv.drawContours(im_contours, [left_contour], -1, color_contours, thickness = int(radius*0.6));
    # centers
    cv.circle(im_center, right_centroid, radius, color=color_center, thickness=-1)
    cv.circle(im_center, left_centroid, radius, color=color_center, thickness=-1)
    # Circles
    cv.circle(im_points, right_mid_point, radius, color_points, thickness=-1)
    cv.circle(im_points, right_lung_apex, radius, color_points, -1);
    cv.circle(im_points, right_width_point, radius, color_points, -1);
    # cv.circle(im_points, right_width_base_point, radius, color_points, -1);
    cv.circle(im_points, right_base_modified, radius, color_points, -1);
    # 
    cv.circle(im_points, left_lung_apex, radius, color_points, -1);
    cv.circle(im_points, left_mid_point, radius, color=color_points, thickness=-1)
    cv.circle(im_points, left_width_point, radius, color_points, -1);
    # cv.circle(im_points, left_width_base_point, radius, color_points, -1);
    cv.circle(im_points, left_base_modified, radius, color_points, -1);
    # lines
    cv.line(im_lines, right_lung_apex, right_lung_base, color_lines, thickness = radius//2)
    cv.line(im_lines, right_lung_apex, right_mid_point, color_lines, thickness = radius//2)
    cv.line(im_lines, left_lung_apex, left_lung_base, color_lines, thickness = radius//2)
    cv.line(im_lines, left_lung_apex, left_mid_point, color_lines, thickness = radius//2)
    cv.line(im_lines, left_width_point, right_width_point, color_lines, thickness = radius//2)
    cv.line(im_lines, left_base_modified, right_base_modified, color_lines, thickness= radius//2)
    # Make nans
    im_contours[im_contours==0] = np.nan
    im_lines[im_lines==0] = np.nan
    im_points[im_points==0] = np.nan
    im_center[im_center==0] = np.nan
    if plot: 
        if imname != '': 
            ds = pydicom.dcmread(imname)
            # im = ((ds.pixel_array/ds.pixel_array.max())*255).astype(np.uint8)
            im = ds.pixel_array
            if im[0,0]/ im.max() > 0.5: 
                plt.imshow(im*-1, cmap = 'gray')
            else:
                plt.imshow(im, cmap = 'gray')
        plt.imshow(im_contours, cmap=cmap, alpha=alpha, vmin=0, vmax=300); 
        plt.imshow(im_lines, cmap=cmap, alpha=alpha, vmin=0, vmax=300); 
        plt.imshow(im_points, cmap=cmap, alpha=alpha, vmin=0, vmax=300); 
        plt.imshow(im_center, cmap=cmap, alpha=alpha, vmin=0, vmax=300); 
        plt.axis('off');
    if savename != '': 
        if imname != '': 
            ds = pydicom.dcmread(imname)
            # im = ((ds.pixel_array/ds.pixel_array.max())*255).astype(np.uint8)
            im = ds.pixel_array
            plt.imshow(im, cmap = 'gray');
        plt.imshow(im_contours, cmap=cmap, alpha=alpha, vmin=0, vmax=300); 
        plt.imshow(im_lines, cmap=cmap, alpha=alpha, vmin=0, vmax=300); 
        plt.imshow(im_points, cmap=cmap, alpha=alpha, vmin=0, vmax=300); 
        plt.imshow(im_center, cmap=cmap, alpha=alpha, vmin=0, vmax=300); 
        plt.axis('off');
        plt.savefig(savename)
        plt.close()
        
        
def get_target_points_final(left_contour, right_contour, modefied = True):
    l = get_target_points(left_contour,modefied=modefied, left=True, other_contour_points = right_contour)
    r = get_target_points(right_contour,modefied=modefied, left=False, other_contour_points = left_contour)
    left_lung_apex, left_lung_base, left_mid_point, left_highest_point, left_centroid,left_width_point,left_width_base_point = l 
    right_lung_apex, right_lung_base, right_mid_point, right_highest_point, right_centroid,right_width_point,right_width_base_point = r 
    # Find the shorter lung 
    left_contour = left_contour.squeeze()
    right_contour = right_contour.squeeze()
    if right_width_base_point[1] < left_width_base_point[1]:
        # Right is the shorter  = work on the left lung 
        lateral_points = left_contour[left_contour[:, 0] > left_centroid[0]]
        matching_points = [point for point in lateral_points if point[1] == right_width_base_point[1]]
        left_width_base_point_modified = max(matching_points, key=lambda point: np.linalg.norm(point - left_centroid))
        right_width_base_point_modified = right_width_base_point
    else:
        lateral_points = right_contour[right_contour[:, 0] < right_centroid[0]]
        matching_points = [point for point in lateral_points if point[1] == left_width_base_point[1]]
        right_width_base_point_modified = max(matching_points, key=lambda point: np.linalg.norm(point - right_centroid))
        left_width_base_point_modified  = left_width_base_point
    
    l = [left_lung_apex, left_width_base_point, left_mid_point, left_highest_point, 
         left_centroid,left_width_point,left_width_base_point, left_width_base_point_modified]
    r = [right_lung_apex, right_width_base_point, right_mid_point, right_highest_point, right_centroid,
         right_width_point,right_width_base_point, right_width_base_point_modified]
    return l , r


def get_target_points(contour_points, modefied = True, left=False, other_contour_points = None):    
    contour_points = contour_points.squeeze()
    centroid = np.mean(contour_points, axis=0).astype(int)
    lower_points = contour_points[contour_points[:, 1] > centroid[1]]
    upper_points = contour_points[contour_points[:, 1] <= centroid[1]]
    left_points = contour_points[contour_points[:, 0] > centroid[0]]
    right_points = contour_points[contour_points[:, 0] < centroid[0]]
    c_points = left_points if left else right_points
    if modefied: 
        upper_points = contour_points[contour_points[:, 1] <= np.percentile(contour_points[:,1],20)] # Get upper 20% 
        if left:
            lower_points = contour_points[(contour_points[:, 1] > centroid[1])&(contour_points[:, 0] > centroid[0])]
        else:
            lower_points = contour_points[(contour_points[:, 1] > centroid[1])&(contour_points[:, 0] < centroid[0])]
    
    if other_contour_points is not None:
        other_contour_points = other_contour_points.squeeze()
        centroid2 = np.mean(other_contour_points, axis=0).astype(int)
        centroid = np.array([ centroid[0] , (centroid[1]+centroid2[1])/2]).astype(int)
    
    # Get Apex
    distances = np.linalg.norm(upper_points - centroid, axis=1).squeeze()
    sorted_indices = np.argsort(distances)[::-1]
    sorted_contour_points = upper_points[sorted_indices].squeeze()
    # lung_apex = sorted_contour_points[0]  # Old 
    
    matching_points = [point for point in upper_points if point[0] == upper_points[:,0].mean().astype(np.int16)] # Matching y - horizontal
    lung_apex = max(matching_points, key=lambda point: np.linalg.norm(point - centroid))
    
    
    if modefied:
        lung_apex = np.array([upper_points[:,0].mean(), 
                              upper_points[:,1].min()]).astype(np.int16) # Highest y, mean x

    # Get Base
    distances = np.linalg.norm(lower_points - centroid, axis=1).squeeze()
    sorted_indices = np.argsort(distances)[::-1]
    sorted_contour_points = lower_points[sorted_indices].squeeze()
    lung_base = sorted_contour_points[0]
    
    # Get mid point 
    lower_points = contour_points[contour_points[:, 1] > centroid[1]]
    x = int(centroid[0])
    matching_points = [point for point in lower_points if point[0] == x]
    mid_point = min(matching_points, key=lambda point: np.linalg.norm(point - centroid))
    
    # Get highest point
    highest_y_index = np.argmin(contour_points[:, 1])
    highest_point = contour_points[highest_y_index]
    
    # Get width points
    matching_points = [point for point in c_points if point[1] == centroid[1]] # Matching y - horizontal
    lung_width_point = max(matching_points, key=lambda point: np.linalg.norm(point - centroid))
    
    # matching_points = []
    # for i in range(-50,50):
    # matching_points += [point for point in c_points if point[1] == mid_point[1]-i] # Matching y - horizontal
    
    # lung_width_base_point = max(matching_points, key=lambda point: np.linalg.norm(point - mid_point))
    # left_lung_apex, left_lung_base, left_mid_point, left_highest_point, left_centroid
    return lung_apex, lung_base, mid_point, highest_point, centroid, lung_width_point,lung_base

def get_left_and_right_contours(mask):
    # Convert the mask into a binary image
    _, mask = cv.threshold(mask, 127, 255, cv.THRESH_BINARY)
    # Apply morphological operations to clean up the image
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5))
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)

    # Find the contours in the mask
    contours = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    contours = imutils.grab_contours(contours)

    # Get left and right lung contours 
    contour_areas = [cv.contourArea(c) for c in contours]
    largest_contour_idx = np.argmax(contour_areas)
    largest_contour = contours[largest_contour_idx]
    contour_areas[largest_contour_idx] = 0
    second_largest_contour_idx = np.argmax(contour_areas)
    second_largest_contour = contours[second_largest_contour_idx]

    centroid_1 = np.mean(largest_contour, axis=0).squeeze()
    if centroid_1[0] >= mask.shape[1]//2:
        left_contour = largest_contour
        right_contour= second_largest_contour
    else:
        left_contour = second_largest_contour
        right_contour= largest_contour
    return left_contour, right_contour