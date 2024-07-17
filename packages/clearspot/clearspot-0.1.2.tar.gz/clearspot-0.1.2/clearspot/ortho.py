import os
import subprocess

def run_nodeodm():
    # Start NodeODM in the background using Docker
    try:
        subprocess.Popen(['docker', 'run', '-ti', '-p', '3000:3000', 'opendronemap/nodeodm'])
    except Exception as e:
        raise RuntimeError(f"Failed to start Engine: {e}")

def process_images(input_dir, output_dir):
    # Ensure NodeODM is running
    run_nodeodm()

    # Import required modules
    from pyodm import Node

    # Set up the Node
    n = Node('localhost', 3000)

    # Collect all image paths in the input directory
    image_paths = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.jpg') or f.endswith('.jpeg') or f.endswith('.png')]

    # Create and process the task
    task = n.create_task(image_paths, {'orthophoto-resolution': 2, 'dsm': True})
    task.wait_for_completion()

    # Download the orthophoto TIFF file to the output directory
    result_dir = task.download_assets(output_dir)

    # Rename the orthophoto file to 'clearspot_map.tif'
    orthophoto_path = os.path.join(result_dir, 'odm_orthophoto', 'odm_orthophoto.tif')
    output_path = os.path.join(output_dir, 'clearspot_map.tif')
    os.rename(orthophoto_path, output_path)

    print(f"Orthophoto saved to: {output_path}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Process images with clearspot.')
    parser.add_argument('input_dir', help='Path to the input directory containing images')
    parser.add_argument('output_dir', help='Path to the output directory for the orthophoto TIFF file')
    args = parser.parse_args()

    process_images(args.input_dir, args.output_dir)

if __name__ == '__main__':
    main()
