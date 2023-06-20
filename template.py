import argparse
import os
import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt

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

    # Check if any point cloud files were found
    if not point_cloud_files:
        print(f"No point cloud files found in directory {point_cloud_dir}")
        return

    # Initialize an empty list to store the point clouds
    point_clouds = []

    # Load each point cloud and add it to the list
    for file in point_cloud_files:
        pcd = o3d.io.read_point_cloud(file)
        point_clouds.append(pcd)

    # Merge the point clouds into a single point cloud
    merged_pcd = o3d.geometry.PointCloud()
    for pcd in point_clouds:
        merged_pcd += pcd

    # Check if the merged point cloud is empty
    if merged_pcd.is_empty():
        print("Merged point cloud is empty")
        return

    # Find the bounding box of the merged point cloud
    min_bound = merged_pcd.get_min_bound()
    max_bound = merged_pcd.get_max_bound()

    # Extract points and colors
    points = np.asarray(merged_pcd.points)
    colors = np.asarray(merged_pcd.colors)

    # Transform points to pixel coordinates
    x_pixels = np.floor(((points[:, 0] - min_bound[0]) / (max_bound[0] - min_bound[0])) * (args.width - 1)).astype(int)
    y_pixels = np.floor(((points[:, 1] - min_bound[1]) / (max_bound[1] - min_bound[1])) * (args.height - 1)).astype(int)

    # Create blank image
    image = np.zeros((args.height, args.width, 3), dtype=np.uint8)

    # Assign colors to pixels
    for i in range(len(points)):
        image[int(y_pixels[i]), int(x_pixels[i])] = colors[i] * 255

    # Save image
    output_file = "/Users/sheraliozodov/phyto_oracle/3d_orthomosaic_generator/combined_view.png"
    plt.imsave(output_file, image)

    print(f"Image saved to {output_file}")

# --------------------------------------------------
if __name__ == '__main__':
    main()
