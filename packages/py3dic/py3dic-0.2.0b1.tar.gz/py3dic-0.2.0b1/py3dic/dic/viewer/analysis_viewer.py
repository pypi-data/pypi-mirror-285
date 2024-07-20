#%% 
# Analysis viewer
# this is a viewer for the DIC analysis results
#
# it aims to create a class that acts as a container for the DIC analysis results
# and provides methods to visualize the results

#%%
import pathlib
from datetime import datetime
import json

import tkinter as tk
from tkinter import filedialog

import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.tri as tri

from py3dic.dic.core.dic_result_loader import DICResultFileContainer
from py3dic.dic.core.core_calcs import compute_disp_and_remove_rigid_transform, compute_displacement
from py3dic.dic import DICGrid
from py3dic.dic.io_utils import get_file_list 

import logging
# logging.basicConfig(level = logging.DEBUG)
logging.basicConfig(level = logging.WARNING)
#%%
class DICAnalysisResultContainer:
    def __init__(self, analysis_json_fname:str, img_extension:str = 'png') -> None:
        """Initializes the DICAnalysisResultContainer object.

        Args:
            analysis_json (str): The path to the analysis json file.
            img_extension (str, optional): The image file extension. Defaults to 'png'.
        """
        # load the analysis json file	
        self.analysis_json = analysis_json_fname
        self._load_analysis_json()

        # initialise the grid data container
        self.grid_data_container = DICResultFileContainer.from_result_dic(str(self.pp_DISPL_ANALYSIS_OUTPUT))

        # load image file list:
        
        # or 'png', 'bmp', etc.
        self.image_flist = get_file_list(self.pp_IMG_DIR.absolute(), img_extension)

        # load all the csv files from the result folder
        self.csv_flist = get_file_list(str(self.pp_ANALYSIS_RES_FOLDER/"result"),
                             file_extension='csv')
        # self._load_analysis_results()

    def _load_analysis_json(self):
        """Loads and parses the analysis json file 
        and stores the data in the object's attributes.

        """
        # Read the contents of the JSON file
        with open(self.analysis_json, 'r', encoding='utf-8') as file:
            self.analysis_data = json.load(file)

        # print("Contents of the file:", self.analysis_data)
        self.pp_json = pathlib.Path(self.analysis_json)
        self.pp_IMG_DIR = pathlib.Path(self.analysis_data.get('Image Folder',None))
        self.pp_ANALYSIS_RES_FOLDER = self.pp_json.parent
        self.pp_DISPL_ANALYSIS_OUTPUT = self.pp_ANALYSIS_RES_FOLDER /'result.dic'

        # add analysis configuration parameters
        self.roi_window = self.analysis_data.get('ROI Selection',None)
        self.window_size = self.analysis_data.get('correl_window_size',None)
        self.grid_size = self.analysis_data.get('correl_grid_size',None)
        self.interpolation = self.analysis_data.get('interpolation',None)
        self.strain_type = self.analysis_data.get('strain type',None)
        self.remove_rigid_translation = self.analysis_data.get('remove translation',True)

    def print_analysis_data(self):
        """Prints the analysis data.

        """	
        for k,v in self.analysis_data.items():
            print(f"{k:25s} : {v:}")
        print(f"================ Config Parameters ================")
        print(f"image dir    : {self.pp_IMG_DIR}")
        print(f"analysis dir : {self.pp_ANALYSIS_RES_FOLDER}")
        print(f"analysis file: {self.pp_json}")
        print(f"ROI          : {self.roi_window}")
        print(f"window size  : {self.window_size}")
        print(f"grid size    : {self.grid_size}")
        print(f"remove rigid : {self.remove_rigid_translation}")
        print(f"interpolation: {self.interpolation}")
        print(f"strain type  : {self.strain_type}")

    @property
    def point_list(self)   -> list:
        """Returns the list for all frames with for the XY coordinate for all grid points.

        e.g. point_list[0] returns the XY coordinates for the first frame
        """ 
        return self.grid_data_container.pointlist

    def get_grid(self, frame_id:int) -> DICGrid:
        """Returns the grid points in the test imagelist.

        Args:
            frame_id (int): The frame id (keep in mind that it starts with 1).
        Returns:
            np.ndarray: The grid points.
        """
        assert frame_id >=1 and isinstance(frame_id, int), "frame_id must be an integer >=1"
        mygrid = DICGrid.from_gridsize(self.grid_data_container.gs)

        zb_fr_id = frame_id - 1

        logging.info("compute displacement and strain field of %s ...", self.image_flist[zb_fr_id])
        mygrid.process_grid_data(reference_image=self.image_flist[0],
                                 image=self.image_flist[zb_fr_id],
                                 reference_points=self.point_list[0],
                                 current_points=self.point_list[zb_fr_id],
                                 interpolation_method=self.interpolation,
                                 strain_type=self.strain_type,
                                 remove_rigid_transform= self.remove_rigid_translation)
        
        return mygrid
    

    
    def create_strain_map(self,
            frame_id:int, 
            output_folder:pathlib.Path = None,
            strain_dir:str='strain_xx',
            zlim = (-0.1, 0.1),
            save_memory:bool=True,
            *args, **kwargs
            ):
        """
        Create and save a strain map for a given frame.

        Args:
            frame_id (int): The index of the frame to process.
            analysis_results (object): Object containing analysis results (like grid_points_ref and pointlist).
            image_list (list): List of image file paths.
            csv_files (list): List of CSV file paths containing strain data.
            output_folder (Path): output folder to save the strain map images.
            strain_dir (str):   strain direction/type. Default is 'strain_xx' (or strain_yy, strain_xy).
            zlim (tuple): Tuple containing the minimum and maximum values for the colorbar. Default is (-0.1, 0.1).
        """
        # gdc:GridDataContainer = data_analysis_res_container.grid_data_container
        # image_list:list = data_analysis_res_container.image_flist
        # csv_files:list = data_analysis_res_container.csv_flist
        assert strain_dir in ['strain_xx', 'strain_yy', 'strain_xy'], "Invalid strain direction. Choose from 'strain_xx', 'strain_yy', 'strain_xy'."
        
        if output_folder is None:
            output_folder = self.pp_ANALYSIS_RES_FOLDER 
            
        # Extract initial and final coordinates, and strain values
        # initial_coordinates = analysis_results.grid_points_ref
        final_coordinates = self.grid_data_container.pointlist[frame_id]
        df_result_tmp = pd.read_csv(self.csv_flist[frame_id])
        strain_values = df_result_tmp[strain_dir].values

        # Create triangulation for plotting
        x_final, y_final = final_coordinates[:, 0], final_coordinates[:, 1]
        triangulation = tri.Triangulation(x_final, y_final)

        # Read the current frame image
        curr_frame = plt.imread(self.image_flist[frame_id])
        try:
            # get the shape of an RGB image
            (_Ypx, _Xpx, _COLS) = curr_frame.shape
        except ValueError:
            # get the shape of an Grayscale
            (_Ypx, _Xpx) = curr_frame.shape

        # Create the figure
        fig = plt.figure(figsize=(8, 2*(8*(_Ypx/_Xpx))))
        ax = fig.add_subplot(111)
        ax.imshow(curr_frame, cmap=plt.cm.binary, aspect='equal')

        # Create the contour plot
        # Option 1: tricontour generates contour lines
        # contour_levels = np.linspace(start=-0.1, stop=0.1, num=11)
        # tricontour = ax.tricontour(triangulation, strain_values,
        #     levels=contour_levels, linewidths=0.5, colors='k', alpha=0.4)

        # Option 2: Create the tripcolor plot
        tpc = ax.tripcolor(triangulation, strain_values, shading='flat',
                        alpha=kwargs.get('alpha',0.6),
                        vmin=zlim[0], vmax=zlim[1])
        ax.set_xlabel('')
        ax.set_ylabel('')

        # Add colorbar
        cbar = plt.colorbar(tpc, label='Strain', orientation='horizontal',
                shrink=0.8, aspect=40, pad=0.05)
        ax.set_xticks([])
        ax.set_yticks([])

        # Save the figure
        output_path = output_folder /f"{strain_dir}" /f"cam-{frame_id:05d}-{strain_dir}.png"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        if save_memory:
            plt.close(fig)  # Close the figure to free memory

# %%

