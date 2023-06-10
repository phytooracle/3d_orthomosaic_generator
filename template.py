#!/usr/bin/env python3
"""
Author : Emmanuel Gonzalez, Jeffrey Demieville, Sherali Ozodov
Date   : 2022-10-02
Purpose: 3D Orthomosaic Generator
"""

import argparse
import os
import open3d as o3d
import numpy as np

# --------------------------------------------------
def get_args():
    """Get command-line arguments"""
    parser = argparse.ArgumentParser(
        description='3D Orthomosaic Generator',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('directory',
                        metavar='directory',
                        help='Directory path to the point clouds')

    parser.add_argument('-w',
                        '--width',
                        help='Image width',
                        metavar='width',
                        type=int,
                        default=800)

    parser.add_argument('-H',
                        '--height',
                        help='Image height',
                        metavar='height',
                        type=int,
                        default=600)

    return parser.parse_args()


# --------------------------------------------------
def main():
    """Make a jazz noise here"""

    args = get_args()

    # Set the directory where the point clouds are stored
    point_cloud_dir = args.directory

    # Initialize an empty list to store the point cloud files
    point_cloud_files = []

    # Recursively search for point cloud files in the specified directory and its subdirectories
    for dirpath, dirnames, filenames in os.walk(point_cloud_dir):
        for file in filenames:
            if file.endswith(".ply"):
                point_cloud_files.append(os.path.join(dirpath, file))

    # Initialize an empty list to store the point clouds
    point_clouds = []

    # Load each point cloud and add it to the list
    for file in point_cloud_files:
        pcd = o3d.io.read_point_cloud(file)
        # Apply offset after opening the point cloud
        x_offset = 409000
        y_offset = 3660000

        np.asarray(pcd.points)[:, 0] -= x_offset
        np.asarray(pcd.points)[:, 1] -= y_offset

        # Append
        point_clouds.append(pcd)

    # Merge the point clouds into a single point cloud
    merged_pcd = o3d.geometry.PointCloud()
    for pcd in point_clouds:
        merged_pcd += pcd

    # Visualize the merged point cloud with real colors
    o3d.visualization.draw_geometries([merged_pcd], point_show_normal=False)

    # Adjust the camera view to show the desired perspective
    view_control = o3d.visualization.Visualizer().get_view_control()
    view_control.set_up([0, 0, -1])  # Set the up direction (negative Z-axis)
    view_control.set_front([0, -1, 0])  # Set the front direction (negative Y-axis)
    view_control.set_lookat([0, 0, 0])  # Set the look-at position

    # Save the current view as an image
    image_width = args.width
    image_height = args.height
    o3d.io.write_image("combined_view.png", o3d.visualization.render_point_cloud_to_image(merged_pcd, width=image_width, height=image_height))


# --------------------------------------------------
if __name__ == '__main__':
    main()
