import os
from pyodm import Node
import subprocess
import time

def start_nodeodm():
    subprocess.run(['./clearspot/mapping/entrypoint.sh'])

def process_images(input_dir, output_dir):
    # Start NodeODM
    start_nodeodm()
    time.sleep(10)  # Wait for NodeODM to start

    # Get a list of all image file paths in the folder
    image_files = [os.path.join(input_dir, file) for file in os.listdir(input_dir) if file.lower().endswith(('.jpg', '.jpeg', '.png'))]

    # Connect to the NodeODM instance
    n = Node('localhost', 3000)

    # Create a task to process the images with orthophoto generation
    task = n.create_task(image_files, {'orthophoto-resolution': 2, 'dsm': True})

    # Wait for the task to complete
    task.wait_for_completion()

    # Download just the orthophoto and rename it to clearspot_map
    temp_dir = os.path.join(output_dir, "temp_results")
    os.makedirs(temp_dir, exist_ok=True)
    task.download_assets(temp_dir)

    # Move the orthophoto to the final directory and rename it
    orthophoto_path = os.path.join(temp_dir, 'odm_orthophoto', 'odm_orthophoto.tif')
    final_orthophoto_path = os.path.join(output_dir, 'clearspot_map.tif')

    if os.path.exists(orthophoto_path):
        os.rename(orthophoto_path, final_orthophoto_path)
        print(f"Orthophoto has been saved as {final_orthophoto_path}.")
    else:
        print("Orthophoto not found in the results directory.")

    # Clean up the temporary directory
    import shutil
    shutil.rmtree(temp_dir)
