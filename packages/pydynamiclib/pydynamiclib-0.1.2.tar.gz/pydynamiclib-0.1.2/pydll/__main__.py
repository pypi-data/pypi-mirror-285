import os
import py_compile
import shutil
import zipfile
import argparse
import logging
import subprocess
import sysconfig
import json

def get_required_packages(source_dir):
    # Use pipreqs to generate requirements.txt
    subprocess.run(['pipreqs', '--force', source_dir], check=True)

    # Read requirements.txt
    with open(os.path.join(source_dir, 'requirements.txt'), 'r') as req_file:
        packages = [line.split('==')[0] for line in req_file if line.strip()]
    
    # Remove the requirements.txt file
    os.remove(os.path.join(source_dir, 'requirements.txt'))
    
    return packages

def get_package_dependencies(packages):
    # Use pipdeptree to get the dependencies
    result = subprocess.run(['pipdeptree', '--json'], capture_output=True, text=True, check=True)
    dependencies = json.loads(result.stdout)

    required_packages = set(packages)
    for package in packages:
        queue = [package]
        while queue:
            current = queue.pop(0)
            for dep in dependencies:
                if dep['package']['key'] == current:
                    for dependency in dep['dependencies']:
                        if dependency['key'] not in required_packages:
                            required_packages.add(dependency['key'])
                            queue.append(dependency['key'])
    
    return required_packages

def copy_required_libraries(packages, lib_dir):
    site_packages = sysconfig.get_paths()["purelib"]
    
    for package in packages:
        package_path = os.path.join(site_packages, package)
        if os.path.isdir(package_path):
            shutil.copytree(package_path, os.path.join(lib_dir, package), ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))
        else:
            shutil.copy2(package_path, lib_dir)
        logging.info(f'Copied library {package_path} to {lib_dir}')

def compile_and_zip(source_dir, output_zip):
    try:
        # Ensure the output directory exists
        build_dir = 'build'
        os.makedirs(build_dir, exist_ok=True)

        # Compile all .py files to .pyc
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    compiled_path = os.path.join(build_dir, os.path.relpath(root, source_dir), file + 'c')
                    os.makedirs(os.path.dirname(compiled_path), exist_ok=True)
                    py_compile.compile(full_path, compiled_path)
                    logging.info(f'Compiled {full_path} to {compiled_path}')

        # Get required packages and their dependencies
        required_packages = get_required_packages(source_dir)
        package_dependencies = get_package_dependencies(required_packages)

        # Copy required libraries to the build directory
        lib_dir = os.path.join(build_dir, 'libs')
        os.makedirs(lib_dir, exist_ok=True)
        copy_required_libraries(package_dependencies, lib_dir)

        # Create a ZIP file
        with zipfile.ZipFile(output_zip, 'w') as z:
            for root, dirs, files in os.walk(build_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, build_dir)
                    z.write(full_path, arcname)
                    logging.info(f'Added {full_path} to package as {arcname}')

        # Clean up the build directory
        shutil.rmtree(build_dir)
        logging.info('Cleaned up build directory')

    except Exception as e:
        logging.error(f'Error: {e}')


def main():
    parser = argparse.ArgumentParser(description='Compile and package Python source and libraries.')
    parser.add_argument('source_directory', type=str, help='The source directory to compile and package')
    parser.add_argument('output_package_file', type=str, help='The output package file name (should end with .pydll)')
    args = parser.parse_args()

    # Ensure output package file has .pydll extension
    output_package_file = args.output_package_file
    if not output_package_file.endswith('.pydll'):
        output_package_file += '.pydll'

    logging.basicConfig(level=logging.INFO)
    
    compile_and_zip(args.source_directory, output_package_file)


if __name__ == '__main__':
    main()
