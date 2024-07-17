import os
import subprocess

directory = os.getcwd()

# Iterate over all files in the directory
for filename in os.listdir(directory):
    # Check if the file has a .ui extension
    if filename.endswith('.ui'):
        # Construct full file paths
        ui_file = os.path.join(directory, filename)
        py_file = os.path.join(directory, filename.replace('.ui', '.py'))

        # Construct the command to convert the .ui file to .py
        command = ['pyuic5', ui_file, '-o', py_file]

        try:
            # Run the command
            subprocess.run(command, check=True)
            print(f"Converted {ui_file} to {py_file}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to convert {ui_file}: {e}")