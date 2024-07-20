# calc_strain_calculator.py
"""
This module provides functions to calculate strain.

"""
import numpy as np
from .grid_size import GridSize

class StrainCalculator:
    """
    A class used to calculate strain in materials.

    Attributes
    ----------
    grid_x : np.array
        The x-coordinates of the grid points.
    grid_y : np.array
        The y-coordinates of the grid points.
    strain_xx : np.array
        The normal strain in the x-direction.
    strain_xy : np.array
        The shear strain.
    strain_yy : np.array
        The normal strain in the y-direction.
    """
    grid_x: np.array = None
    grid_y: np.array = None

    def __init__(self, grid_x, grid_y):
        """
        Constructs all the necessary attributes for the StrainCalculator object.

        Parameters
        ----------
        grid_x : np.array
            The x-coordinates of the grid points.
        grid_y : np.array
            The y-coordinates of the grid points.
        """
        self.grid_x = grid_x
        self.grid_y = grid_y 
        # TODO the disp_x and disp_y should be arguments in the compute_strain method
        self.strain_xx = np.full_like(grid_x, np.NaN)
        self.strain_xy = np.full_like(grid_x, np.NaN)
        self.strain_yy = np.full_like(grid_x, np.NaN)

    def compute_strain_field(self, disp_x: np.array, disp_y:np.array):
        """
        Compute strain field from displacement using numpy.

        Parameters
        ----------
        disp_x : np.array
            Displacement field in the x-direction.
        disp_y : np.array
            Displacement field in the y-direction.

        Returns
        -------
        tuple
            The strain fields (strain_xx, strain_yy, strain_xy).
        """
        #get strain fields
        dx = self.grid_x[1][0] - self.grid_x[0][0]
        dy = self.grid_y[0][1] - self.grid_y[0][0]

        strain_xx, strain_xy = np.gradient(disp_x, dx, dy, edge_order=2)
        strain_yx, strain_yy = np.gradient(disp_y, dx, dy, edge_order=2)

        self.strain_xx = strain_xx + 0.5 * (np.power(strain_xx, 2) + np.power(strain_yy, 2))
        self.strain_yy = strain_yy + 0.5 * (np.power(strain_xx, 2) + np.power(strain_yy, 2))
        # this is the shear strain e_xy (not the engineering shear strain $\gamma_{xy}$
        self.strain_xy = 0.5 * (strain_xy + strain_yx + strain_xx * strain_xy + strain_yx * strain_yy)
        return self.strain_xx, self.strain_yy, self.strain_xy

    def compute_strain_field_DA(self, disp_x: np.array, disp_y:np.array):
        """
        Compute strain field from displacement field using a large strain method (2nd order).

        Parameters
        ----------
        disp_x : np.array
            Displacement field in the x-direction.
        disp_y : np.array
            Displacement field in the y-direction.

        Returns
        -------
        tuple
            The strain fields (strain_xx, strain_yy, strain_xy).
        """
        dx = self.grid_x[1][0] - self.grid_x[0][0]
        dy = self.grid_y[0][1] - self.grid_y[0][0]

        for i in range(self.grid_x.shape[0]):
            for j in range(self.grid_y.shape[1]):
                du_dx = 0.
                dv_dy = 0.
                du_dy = 0.
                dv_dx = 0.

                if i - 1 >= 0 and i + 1 < self.grid_x.shape[0]:
                    du1 = (disp_x[i + 1, j] - disp_x[i - 1, j]) / 2.
                    du_dx = du1 / dx
                    dv2 = (disp_y[i + 1, j] - disp_y[i - 1, j]) / 2.
                    dv_dx = dv2 / dx

                if j - 1 >= 0 and j + 1 < self.grid_y.shape[1]:
                    dv1 = (disp_y[i, j + 1] - disp_y[i, j - 1]) / 2.
                    dv_dy = dv1 / dx
                    du2 = (disp_x[i, j + 1] - disp_x[i, j - 1]) / 2.
                    du_dy = du2 / dy

                self.strain_xx[i, j] = du_dx + 0.5 * (du_dx ** 2 + dv_dx ** 2)
                self.strain_yy[i, j] = dv_dy + 0.5 * (du_dy ** 2 + dv_dy ** 2)
                self.strain_xy[i, j] = 0.5 * (du_dy + dv_dx + du_dx * du_dy + dv_dx * dv_dy)
        return self.strain_xx, self.strain_yy, self.strain_xy

    def compute_strain_field_log(self, disp_x: np.array, disp_y:np.array):
        """
        Compute strain field from displacement field for large strain (logarithmic strain).

        Parameters
        ----------
        disp_x : np.array
            Displacement field in the x-direction.
        disp_y : np.array
            Displacement field in the y-direction.

        Returns
        -------
        tuple
            The strain fields (strain_xx, strain_yy, strain_xy).
        """
        dx = self.grid_x[1][0] - self.grid_x[0][0]
        dy = self.grid_y[0][1] - self.grid_y[0][0]

        for i in range(self.grid_x.shape[0]):
            for j in range(self.grid_y.shape[1]):
                du_dx = 0.
                dv_dy = 0.
                du_dy = 0.
                dv_dx = 0.

                if i - 1 >= 0 and i + 1 < self.grid_x.shape[0]:
                    du1 = (disp_x[i + 1, j] - disp_x[i - 1, j]) / 2.
                    du_dx = du1 / dx
                    dv2 = (disp_y[i + 1, j] - disp_y[i - 1, j]) / 2.
                    dv_dx = dv2 / dx

                if j - 1 >= 0 and j + 1 < self.grid_y.shape[1]:
                    dv1 = (disp_y[i, j + 1] - disp_y[i, j - 1]) / 2.
                    dv_dy = dv1 / dx
                    du2 = (disp_x[i, j + 1] - disp_x[i, j - 1]) / 2.
                    du_dy = du2 / dy
                t11 = 1 + 2. * du_dx + du_dx ** 2 + dv_dx ** 2
                t22 = 1 + 2. * dv_dy + dv_dy ** 2 + du_dy ** 2
                t12 = du_dy + dv_dx + du_dx * du_dy + dv_dx * dv_dy
                deflog = np.log([[t11, t12], [t12, t22]])

                self.strain_xx[i, j] = 0.5 * deflog[0, 0]
                self.strain_yy[i, j] = 0.5 * deflog[1, 1]
                self.strain_xy[i, j] = 0.5 * deflog[0, 1]
            
        return self.strain_xx, self.strain_yy, self.strain_xy

    def compute_strain(self, disp_x: np.array, disp_y:np.array, method:str):
        """
        Compute strain field based on the specified method.

        Parameters
        ----------
        disp_x : np.array
            Displacement field in the x-direction.
        disp_y : np.array
            Displacement field in the y-direction.
        method : str
            Method to compute strain ('cauchy', '2nd_order', or 'log').

        Returns
        -------
        tuple
            The strain fields (strain_xx, strain_yy, strain_xy).
        """
        if method == 'cauchy':
            strain_xx, strain_yy, strain_xy  = self.compute_strain_field(disp_x, disp_y)
        elif method == '2nd_order':
            strain_xx, strain_yy, strain_xy= self.compute_strain_field_DA(disp_x, disp_y)
        elif method == 'log':
            strain_xx, strain_yy, strain_xy= self.compute_strain_field_log(disp_x, disp_y)
        else:
            raise ValueError("Please specify a correct strain_type: 'cauchy', '2nd_order' or 'log'")

        return strain_xx, strain_yy, strain_xy

    @classmethod
    def from_gridsize(cls, grid_size: GridSize):
        """
        Create a StrainCalculator object from a GridSize object.

        Parameters
        ----------
        grid_size : GridSize
            An instance of the GridSize class.

        Returns
        -------
        StrainCalculator
            A StrainCalculator object.
        """
        return cls(grid_size.grid_x, grid_size.grid_y)
        