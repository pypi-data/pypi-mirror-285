#%% [markdown]
# # _pydic_support.py
#
# This script is a support module for a Digital Image Correlation (DIC) project.
#
# ## Functions
#
# - `compute_displacement(point, pointf)`: 
#
#   Given two arrays of points, this function calculates the displacement between corresponding points. 
#   Input arrays should be the same length. Returns an array of (x,y) displacement vectors.
#
# - `compute_disp_and_remove_rigid_transform(p1, p2)`: 
#
#   Given two sets of 2D points (in the form of numpy arrays), this function computes the optimal rotation 
#   and translation between the two sets using Singular Value Decomposition (SVD). It then removes the rigid 
#   transform and returns the displacement between the two point sets.
#
# - `remove_point_outside(points, area, *args, **kwargs)`: 
#
#   This function removes points from a list that are outside a specified rectangular area.
#
# ## Classes
#
# - `AreaSelector`: 
#
#   This class allows for the selection of an area of interest in an image using OpenCV. The area can be selected 
#   by left-clicking and dragging the mouse, and pressing the 'c' key to confirm the selection.
#
#   - `pick_area_of_interest()`: 
#
#     This method opens a window with the image and allows the user to select an area of interest. The method 
#     returns the coordinates of the selected area.
#
#   - `click_and_crop(event, x, y, flags, param)`: 
#
#     This method handles the mouse events for selecting the area of interest.
#%%
import numpy as np

def compute_displacement(point, pointf)->np.array:
    """Given two arrays of points, this function calculates the displacement between corresponding points. 
    
    #TODO change the output to numpy array

    Input arrays should be the same length. Returns an array of (x,y) displacement vectors.
    
    Args:
        point (_type_): coordinates of points initially
        pointf (_type_): coordinates of points finally 

    Returns:
        _type_: displacement between points
    """    
    assert len(point)==len(pointf)
    lst_disp_xy_tuples = []
    for i, pt0 in enumerate(point):
        pt1 = pointf[i]
        lst_disp_xy_tuples.append((pt1[0]-pt0[0], pt1[1]-pt0[1]))
    return np.array(lst_disp_xy_tuples)


def compute_disp_and_remove_rigid_transform(new_points, old_points)->np.array:
    """Computes the displacement between two point sets and removes rigid transform.

    #TODO change the output to numpy array
    
    This function computes the optimal rotation and translation between two sets of 
    points (p1 and p2) using Singular Value Decomposition (SVD). The function also 
    removes the rigid transform between the point sets and returns the displacement 
    between them.

    Args:
        p1 (numpy.array): An Nx2 numpy array representing the first set of 2D points.
        p2 (numpy.array): An Nx2 numpy array representing the second set of 2D points.

    Returns:
        numpy.array: An Nx2 numpy array representing the displacement between the two 
                        point sets after removing the rigid transform.

    Raises:
        AssertionError: If the lengths of the input point sets do not match.
    """ 
    A = []
    B = []
    removed_indices = []
    for i in range(len(new_points)):
        if np.isnan(new_points[i][0]):
            assert np.isnan(new_points[i][0]) and np.isnan(new_points[i][1]) and np.isnan(old_points[i][0]) and np.isnan(old_points[i][1])
            removed_indices.append(i)
        else:
            A.append(new_points[i])
            B.append(old_points[i])
        
    A = np.matrix(A)
    B =  np.matrix(B)
    assert len(A) == len(B)
    N = A.shape[0]; # total points
    
    centroid_A = np.mean(A, axis=0)
    centroid_B = np.mean(B, axis=0)

    # centre the points
    AA = np.matrix(A - np.tile(centroid_A, (N, 1)))
    BB = np.matrix(B - np.tile(centroid_B, (N, 1)))

    # dot is matrix multiplication for array
    H = np.transpose(AA) * BB
    U, S, Vt = np.linalg.svd(H)
    R = Vt.T * U.T

    # special reflection case
    if np.linalg.det(R) < 0:
        print("Reflection detected")
        Vt[2,:] *= -1
        R = Vt.T * U.T

    n = len(A)
    T = -R*centroid_A.T + centroid_B.T
    A2 = (R*A.T) + np.tile(T, (1, n))
    A2 = np.array(A2.T)
    out = []
    j = 0
    for i in range(len(new_points)):
        if np.isnan(new_points[i][0]):
            out.append(new_points[i])
        else:
            out.append(A2[j])
            j = j + 1
    out = np.array(out)
    return compute_displacement(old_points, out)

def remove_point_outside(points, area, *args, **kwargs):
    """Removes points that are outside the specified rectangular area.

    Args:
        points (List[Tuple[float, float]]): A list of points, each point represented as a tuple (x, y).
        area (List[Tuple[float, float]]): The area of interest, represented as two tuples
            [(top_left_x, top_left_y), (bottom_right_x, bottom_right_y)].
        *args: Additional arguments (not used in this function).
        **kwargs: Additional keyword arguments. Accepts 'shape' keyword (not used in this function).

    Returns:
        np.array: A NumPy array containing the filtered points that are inside the specified area.
    """
    # shape = 'box' if 'shape' not in kwargs else kwargs['shape']
    xmin = area[0][0]
    xmax = area[1][0]
    ymin = area[0][1]
    ymax = area[1][1]
    res = []
    for p in points:
        x = p[0]
        y = p[1]
        if (x >= xmin) and (x <= xmax) and (y >= ymin) and (y <= ymax):
            res.append(p)
    return np.array(res)

#%%

# %%
