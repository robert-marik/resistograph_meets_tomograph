# This file is part of the resistograph_meets_tomograph project.
# © 2025 Robert Mařík, Valentino Cristini
# Licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0)
# See LICENSE file or https://creativecommons.org/licenses/by/4.0/

"""
Author:
Robert Mařík and Valentino Cristini

The file provides a function to apply an affine transformation to draw a bitmap image on a matplotlib axis. 
The transformation aligns two specific source points in the image with corresponding target points, 
allowing for rotation, scaling, and translation.
Functions:
transform_image(overlay, ax, A_img, B_img, A_target, B_target, alpha=1, zorder=500, plot_image=True)
    Applies an affine transformation to align an image with specified target points and optionally 
    plots the transformed image on a matplotlib axis.    
"""

import numpy as np
from matplotlib.transforms import Affine2D
 
def transform_image(overlay, ax, A_img, B_img, A_target, B_target, alpha=1, zorder=500, plot_image=True):
    """
    Applies an affine transformation to overlay an image on a matplotlib axis so that two specific 
    source points (A_img, B_img) align with corresponding target points (A_target, B_target).

    Parameters:
    ----------
    overlay : np.ndarray
        The image array to be transformed and optionally plotted (typically an RGBA image).
    
    ax : matplotlib.axes.Axes
        The matplotlib Axes object where the transformed image will be plotted.
    
    A_img : array-like, shape (2,)
        The first reference point in the source image (x, y).
    
    B_img : array-like, shape (2,)
        The second reference point in the source image (x, y). Used to define orientation and scale.
    
    A_target : array-like, shape (2,)
        The target location for the transformed A_img point (x, y).
    
    B_target : array-like, shape (2,)
        The target location for the transformed B_img point (x, y). Defines desired orientation and scale.
    
    alpha : float, optional (default=1)
        Transparency level for the overlay image (0 = fully transparent, 1 = fully opaque).
    
    zorder : int, optional (default=500)
        Drawing priority of the overlay image within the plot. Higher values are drawn above lower ones.
    
    plot_image : bool, optional (default=True)
        If True, plots the transformed image onto the given axis. If False, only returns the transformation.

    Returns:
    -------
    trans : matplotlib.transforms.Affine2D
        The transformation object applied to align the overlay image to the desired target configuration.
    """
    A_img = np.asarray(A_img)
    B_img = np.asarray(B_img)
    A_target = np.asarray(A_target)
    B_target = np.asarray(B_target)

    # Vectors
    v_img = B_img - A_img
    v_target = B_target - A_target

    # Rotation
    angle_img = np.arctan2(v_img[1], v_img[0])
    angle_target = np.arctan2(v_target[1], v_target[0])
    rotation_angle = angle_target - angle_img

    # Scaling
    scale = np.linalg.norm(v_target) / np.linalg.norm(v_img)

    # Transfomation
    trans = (
        Affine2D()
        .translate(-A_img[0], -A_img[1])     # 1. shift A_img to (0, 0)
        .rotate(rotation_angle)              # 2. rotate
        .scale(-scale, scale)                # 3. scale
        .translate(*A_target)                # 4. shift to final position
    )

    if plot_image:
        # draw the picture
        ax.imshow(overlay, transform=trans + ax.transData, alpha=alpha, zorder=zorder)

    return trans