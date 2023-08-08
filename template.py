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

    # Calculate the size of the bounding box
    size_x = max_bound[0] - min_bound[0]
    size_y = max_bound[1] - min_bound[1]

    # Calculate the aspect ratio
    aspect_ratio = size_x / size_y

    # Extract points and colors
    points = np.asarray(merged_pcd.points)
    colors = np.asarray(merged_pcd.colors)

    # Handle situation where no color data is available.
    if len(colors) == 0:
        # Extract z-coordinates
        z_coords = points[:, 2]

        # Normalize z-coordinates to range 0-1
        normalized_z = (z_coords - np.min(z_coords)) / (np.max(z_coords) - np.min(z_coords))

        # Generate a colormap
        cmap = plt.get_cmap('jet')  # 'jet' is a commonly used colormap for heightmaps

        # Assign colors based on normalized z-coordinates
        colors = cmap(normalized_z)

        # Ignore alpha channel
        colors = colors[:, :3]

    # Determine the max image size
    scale_factor = 1
    max_image_size = max(size_x, size_y) * scale_factor

    # Set the width and height based on the scale factor and the aspect ratio
    if aspect_ratio >= 1:
        width = int(max_image_size / np.sqrt(aspect_ratio))
        height = int(max_image_size / np.sqrt(aspect_ratio))
    else:
        width = int(max_image_size * np.sqrt(aspect_ratio))
        height = int(max_image_size * np.sqrt(aspect_ratio))

    # Transform points to pixel coordinates
    x_pixels = np.floor(((points[:, 0] - min_bound[0]) / (max_bound[0] - min_bound[0])) * (width - 1)).astype(int)
    y_pixels = np.floor(((points[:, 1] - min_bound[1]) / (max_bound[1] - min_bound[1])) * (height - 1)).astype(int)

    # Create blank image
    image = np.zeros((height, width, 3), dtype=np.uint8)

    print(f"Colors size: {len(colors)}")
    print(f"X_pixels size: {len(x_pixels)}")
    print(f"Y_pixels size: {len(y_pixels)}")

    # Assign colors to pixels
    for i in range(len(points)):
        image[int(y_pixels[i]), int(x_pixels[i])] = (colors[i] * 255).astype(np.uint8)

    # Save image
    output_file = "./combined_view.png"
    plt.imsave(output_file, image)

    print(f"Image saved to {output_file}")

# --------------------------------------------------
if __name__ == '__main__':
    main()
