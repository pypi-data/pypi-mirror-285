import pathlib
import numpy as np
import logging
import cv2
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.tri as tri
from py3dic.dic import DICGrid


class DIC_Grid_plots:
    """This class is an attempt to replace the draw_opencv_v2 function in pydicGrid.
    
    NOTE: It is not yet complete  #TODO
    
    Each grid needs to plot:
    - grid (to current image)
    - markers (to current image)
    - displacement (to ref image)
    - strain map (to ref / current image)

    The idea for this class is to have a factory of plots and the following steps are performed:
    - create a plotter object
    - once the plotter object is created
        - set the grid
        - set the image (ref or current)
        - plot the desired plot
    - rinse and repeat
    """
    _grid:DICGrid = None

    gr_color:tuple=(1.,1.,1.) # grid color
    t_color=(1.,1.,1.) # Text color
    p_color=(1.,1.,0.) # marker color
    l_color=(255, 120, 255)

    def __init__(self):
        self._grid = None

    def set_grid(self, grid: DICGrid):
        """Set the DIC grid for the DIC_GridPlots object.

        Args:
            grid (DIC_Grid): The DIC grid to be set.

        Raises:
            ValueError: If the provided grid is not an instance of DIC_Grid.
        """
        assert isinstance(grid, DICGrid), ValueError('grid is not DIC_Grid')
        self._grid = grid

    
    def set_ref_image(self, ref_image: np.ndarray):
        """ Set the reference image for the DIC grid plots.

        Parameters:
            ref_image (np.ndarray): The reference image to be set.

        Returns:
            None
        """
        assert isinstance(ref_image, np.ndarray), ValueError('ref_image is not a numpy array')  
        self.ref_image = ref_image

    def plot_markers(self,image_cv2:np.ndarray|int,
                p_color:tuple[float]=(1,1,0),
                text:str = None, t_color=(1,1,1)):
        """plots markers on the image
        # TODO THere seems to be a problem when the displacement is large( towards the end of the experiment)

        Args:
            image_cv2 (np.ndarray|int): array with image GRAYSCALE data (in opencv format?)
            p_color (tuple[float], optional): marker color. Defaults to (1,1,0).
            text(str, optional) , annotation text. 
            t_color(tuple[float], optional): Text color. Defaults to (1,1,1)):
        """  
        image_data = self._validate_image(image_cv2)
        frame_rgb = cv2.cvtColor(image_data, cv2.COLOR_GRAY2RGB)

        fig, ax = plt.subplots()
        ax.imshow(frame_rgb, aspect='equal')
        points_xy = self._grid.correlated_point
        if points_xy is not None:
            for pt_xy in points_xy:
                # print(pt_xy)
                if not np.isnan(pt_xy[0]) and not np.isnan(pt_xy[1]):
                    x, y = int(pt_xy[0]), int(pt_xy[1])
                    circ = plt.Circle((x, y), 4, color=p_color)
                    ax.add_patch(circ)

        if text is not None:
            ax.text(50, 50, text, fontsize=12, color=t_color)

    def _validate_image(self, image:np.ndarray|int) -> np.ndarray:
        """Validate the image input.	
        If the image is not a numpy array, then it must be either 0 or 1.
        0 for the reference image, 1 for the current image.
        If the image is a numpy array, then it must be a grayscale image.
        """
        if not isinstance(image, np.ndarray):
            logging.info("Falling back to DIC_grid image")
            assert image in [0, 1], ValueError('if image is not a numpy array then it must be 0 or 1. 0 for reference image, 1 for current image.')
            if image == 0:
                image = cv2.imread(str(self._grid.reference_image), cv2.IMREAD_GRAYSCALE)
            elif image == 1:
                image = cv2.imread(str(self._grid.image), cv2.IMREAD_GRAYSCALE)
        return image

    def plot_grid(self,
                  image: np.ndarray|int, 
                  text: str = None,
                  scale: float = 1,
                  gr_color: tuple = (1, 1, 1),
                  filename: str = None,
                  *args, **kwargs):
        """Plot the original grid on top of the input image.

        Args:
            image (np.ndarray): The input image, normally an array (if not then if 0 then reference image, if 1 a current image). Defaults to None.
            text (str, optional): Additional text to be displayed on the plot. Defaults to None.
            scale (float, optional): Scaling factor for the grid. Defaults to 1.
            gr_color (tuple, optional): Color of the grid lines. Defaults to (1, 1, 1).
            filename (str, optional): File path to save the plot. Defaults to None.
            *args, **kwargs: Additional arguments to be passed to the plot function.

        Returns:
            None
        """
        
        image_data = self._validate_image(image)

        frame_rgb = cv2.cvtColor(image_data, cv2.COLOR_GRAY2RGB)
        
        fig, ax = plt.subplots(nrows=1, ncols=1)
        
        ax.imshow(image_data, cmap='gray', aspect='equal')

        if self._grid is not None:
            dic_grid = self._grid
            for i in range(dic_grid.size_x):
                for j in range(dic_grid.size_y):
                    if dic_grid.is_valid_number(i, j):
                        x = int(dic_grid.grid_x[i, j]) - int(dic_grid.disp_x[i, j] * scale)
                        y = int(dic_grid.grid_y[i, j]) - int(dic_grid.disp_y[i, j] * scale)

                        if i < (dic_grid.size_x - 1) and dic_grid.is_valid_number(i + 1, j):
                            x1 = int(dic_grid.grid_x[i + 1, j]) - int(dic_grid.disp_x[i + 1, j] * scale)
                            y1 = int(dic_grid.grid_y[i + 1, j]) - int(dic_grid.disp_y[i + 1, j] * scale)
                            ax.plot([x, x1], [y, y1], color=gr_color, linewidth=2)

                        if j < (dic_grid.size_y - 1) and dic_grid.is_valid_number(i, j + 1):
                            x1 = int(dic_grid.grid_x[i, j + 1]) - int(dic_grid.disp_x[i, j + 1] * scale)
                            y1 = int(dic_grid.grid_y[i, j + 1]) - int(dic_grid.disp_y[i, j + 1] * scale)
                            ax.plot([x, x1], [y, y1], color=gr_color, linewidth=2)

        if text is not None:
            ax.text(50, 50, text, fontsize=12, color=(1, 1, 1))

        if filename is not None:
            plt.savefig(filename)
        else:
            pass
            # plt.show()


    # def plot_disp(image, # TODO argumenttakes either an image or a filename. This should be broken up
    #     text: str = None, 
    #     # point=None, 
    #     # pointf=None, 
    #     scale: float = 1, 
    #     p_color: tuple = (0, 1, 1), 
    #     l_color: tuple = (1, 120/255,1 ), 
    #     filename=None,
    #     *args, **kwargs):
    #     """A generic function used to draw matplotlib image. Depending on the arguments it plots 

    #     - markers
    #     - grid
    #     - lines
    #     - displacement

    #     Args:
    #         image (str|np.ndarray): _description_
    #         grid (DIC_Grid): DIC_grid object
    #         text (str, optional): _description_. Defaults to None.
    #         # point (_type_, optional): arg must be an array of (x,y) point. Defaults to None.
    #         # pointf (_type_, optional): to draw lines between point and pointf, pointf  (must be an array of same lenght than the point array). Defaults to None.
    #         scale (int, optional): scaling parameter. Defaults to 1.
    #         p_color (tuple, optional): arg to choose the color of point in (r,g,b) format. Defaults to (0, 255, 255).
    #         l_color (tuple, optional): color of lines in (RGB). Defaults to (255, 120, 255).
    #         gr_color (tuple, optional): color of grid in (RGB). Defaults to (255, 255, 255).
    #         filename (_type_, optional): _description_. Defaults to None.
    #     """ 
    #     if isinstance(image, str):
    #         image = plt.imread(image, 0)

    #     fig, ax = plt.subplots()
    #     ax.imshow(image, cmap='gray')

    #     point = mgridi.reference_point.copy()
    #     if point is not None:
    #         for pt in point:
    #             if not np.isnan(pt[0]) and not np.isnan(pt[1]):
    #                 x, y = pt[0], pt[1]
    #                 ax.scatter(x, y, s=4, color=p_color, marker='o')

    #     pointf = mgridi.correlated_point.copy()
    #     if pointf is not None and point is not None:
    #         assert len(point) == len(pointf), 'size between initial  point and final point does not match.'
    #         for pt0, pt1 in zip(point, pointf):
    #             if not np.isnan(pt0[0]) and not np.isnan(pt0[1]) and not np.isnan(pt1[0]) and not np.isnan(pt1[1]):
    #                 disp_x, disp_y = (pt1[0] - pt0[0]) * scale, (pt1[1] - pt0[1]) * scale
    #                 ax.plot([pt0[0], pt1[0]], [pt0[1], pt1[1]], 
    #                         color=l_color, linewidth=1)

    #     if filename is not None:
    #         plt.savefig(filename, bbox_inches='tight')
    #         return
    #     if text is not None:
    #         plt.text(50, 50, text)
    #     #  plt.show()          


    def create_strain_map(self,
            output_folder:pathlib.Path = None,
            strain_dir:str='strain_xx',
            zlim = (-0.1, 0.1),
            save_memory:bool=True,
            *args, **kwargs
            ):
        """
        Create and save a strain map from this grid.
         
        ORiginally this function was developed for the viewer, then moved to DICAnalysisResultContainer and finally moved here.
        

        Args:
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
        assert output_folder is not None, "Output folder is not defined."
        
        _this_grid:DICGrid = self._grid
        # Extract initial and final coordinates, and strain values
        # initial_coordinates = analysis_results.grid_points_ref
        final_coordinates = _this_grid.correlated_point

        df_result_tmp = pd.DataFrame({
            "strain_xx": _this_grid.strain_xx.flatten(),
            "strain_yy": _this_grid.strain_yy.flatten(),
            "strain_xy": _this_grid.strain_xy.flatten()})
        strain_values = df_result_tmp[strain_dir].values

        # Create triangulation for plotting
        x_final, y_final = final_coordinates[:, 0], final_coordinates[:, 1]
        triangulation = tri.Triangulation(x_final, y_final)

        # Read the current frame image
        curr_frame = plt.imread(_this_grid.image)
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
        output_path = output_folder /f"{strain_dir}" /f"{_this_grid.image.stem}-{strain_dir}.png"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        logging.info("Saving strain map to %s",str(output_path))
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        if save_memory:
            plt.close(fig)  # Close the figure to free memory