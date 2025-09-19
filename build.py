import PyInstaller.__main__
import os

if __name__ == '__main__':
    # Get the absolute path to the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the PyInstaller arguments
    args = [
        'roper.py',
        '--name=roper',
        '--onefile',
        '--windowed',
        # Add any other necessary options here
    ]

    # Run PyInstaller
    PyInstaller.__main__.run(args)
