import os
import shutil
import subprocess
import threading
import time
import requests
import zipfile
import xml.etree.ElementTree as ET

from aacommpy.dotnetmanagement import copy_nuget_dependencies
from aacommpy.settings import AACOMM_DLL, AACOMMSERVER, AGITO_AACOMM, DEFAULT_NET_FRAMEWORK, NET_FRAMEWORK_CHOICES, NUGET_EXE, NUGET_EXE_PATH, TARGET_FOLDER

def dotnetfw(version: str = DEFAULT_NET_FRAMEWORK) -> None:
    if version not in NET_FRAMEWORK_CHOICES:
        raise ValueError(f".NET framework version {version} is not supported.")
    
    latest_version = aacomm_nuget_version()
    source_dir = os.path.join(TARGET_FOLDER, f"{AGITO_AACOMM}.{latest_version}")
    dest_dir = os.path.dirname(__file__)    
    source_dir = os.path.join(source_dir, 'lib', version)  
    dll_path = os.path.join(source_dir, AACOMM_DLL)
    if not os.path.isfile(dll_path):
        raise FileNotFoundError(f"Could not find {AACOMM_DLL} in {source_dir}.")
    
    shutil.copy2(dll_path, dest_dir)
    print(f"The AAComm .NET target framework is {version}")

    #copy dependencies to the working directory according to the target version
    copy_nuget_dependencies(version, dest_dir)

    return None

def download_nuget_exe() -> None:
    os.makedirs(TARGET_FOLDER, exist_ok=True)  # Create the directory if it doesn't exist

    nuget_path = os.path.join(TARGET_FOLDER, NUGET_EXE)
    if os.path.exists(nuget_path):
        return None
    
    # Start the progress indicator in a separate thread
    progress_thread = threading.Thread(target=show_progress_indicator, args=(nuget_path,))
    progress_thread.start()

    # Perform the download
    print(f'downloading {NUGET_EXE}...')
    url = f'https://dist.nuget.org/win-x86-commandline/latest/{NUGET_EXE}'
    r = requests.get(url)
    with open(nuget_path, 'wb') as f:
        f.write(r.content)

    # Wait for the progress thread to complete
    progress_thread.join()

    print(f'{NUGET_EXE} downloaded successfully.')
    return None


def show_progress_indicator(nuget_path):
    while not os.path.exists(nuget_path):
        print('.', end='', flush=True)
        time.sleep(0.5)
    print('')

def download_aacomm_nuget(version: str = "", update: bool = False) -> None:
    # check if old version is installed and remove it if update is True
    installed = False
    for dirname in os.listdir(TARGET_FOLDER):
        if dirname.startswith(f'{AGITO_AACOMM}.') and os.path.isdir(os.path.join(TARGET_FOLDER, dirname)):
            installed = True
            old_version = dirname.split('.')[2:]
            old_version = '.'.join(old_version)
            break

    if update and installed:
        shutil.rmtree(os.path.join(TARGET_FOLDER, f'{AGITO_AACOMM}.{old_version}'))

    # Download the main package
    download_package(AGITO_AACOMM, version, TARGET_FOLDER, NUGET_EXE_PATH)

    # Extract the .nuspec file from the downloaded package
    aacomm_folder = f'{AGITO_AACOMM}.{aacomm_nuget_version()}'
    package_path = os.path.join(TARGET_FOLDER, aacomm_folder, f"{aacomm_folder}.nupkg")
    nuspec_path = extract_nuspec(package_path, TARGET_FOLDER)

    # Parse the .nuspec file to get the dependencies
    dependencies = parse_nuspec(nuspec_path)

    # Install each dependency with the exact version
    for id, version in dependencies:
        print(f'Installing {id} version {version}...')
        install_dependency(id, version, NUGET_EXE_PATH, TARGET_FOLDER)

    print('All dependencies installed.')

    # Copy the AACommServer.exe and AACommServerAPI.dll to the working directory
    aacs_dir = os.path.join(TARGET_FOLDER, aacomm_folder, 'build', AACOMMSERVER)
    dest_dir = os.path.dirname(__file__)
    shutil.copy2(os.path.join(aacs_dir, f'{AACOMMSERVER}.exe'), dest_dir)
    shutil.copy2(os.path.join(aacs_dir, f'{AACOMMSERVER}API.dll'), dest_dir)

    # copy AAComm.dll + dependencies to the working directory        
    dotnetfw()
    return None

def download_package(package_id, package_version, output_dir, nuget_exe_path):
    nuget_cmd = [
        nuget_exe_path,
        'install',
        package_id,
        '-OutputDirectory', output_dir,
        '-Source', 'https://api.nuget.org/v3/index.json',
    ]

    if package_version != "":
        nuget_cmd.extend(['-Version', package_version])

    subprocess.run(nuget_cmd, check=True)

def extract_nuspec(package_path, output_dir):
    with zipfile.ZipFile(package_path, 'r') as zip_ref:
        nuspec_file = [f for f in zip_ref.namelist() if f.endswith('.nuspec')][0]
        zip_ref.extract(nuspec_file, output_dir)
    return os.path.join(output_dir, nuspec_file)

def parse_nuspec(nuspec_path):
    tree = ET.parse(nuspec_path)
    root = tree.getroot()
    namespace = {'default': 'http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd'}
    dependencies = set()

    for group in root.findall('.//default:dependencies/default:group', namespace):
        for dependency in group.findall('default:dependency', namespace):
            id = dependency.get('id')
            version = dependency.get('version').strip('[]')
            dependencies.add((id, version))
    
    return list(dependencies)

def install_dependency(id, version, nuget_exe_path, output_dir):
    subprocess.run([
        nuget_exe_path,
        'install',
        id,
        '-Version', version,
        '-OutputDirectory', output_dir,
        '-Source', 'https://api.nuget.org/v3/index.json'
    ], check=True)


def aacomm_nuget_version() -> str:
    if not os.path.exists(NUGET_EXE_PATH):
        raise RuntimeError("Nuget executable not found. Please run the 'install' command.")
    
    installed = False
    latest_version = None
    for dirname in os.listdir(TARGET_FOLDER):
        if dirname.startswith(f'{AGITO_AACOMM}.') and os.path.isdir(os.path.join(TARGET_FOLDER, dirname)):
            installed = True
            version = dirname.split('.')[2:]
            latest_version = '.'.join(version)
            print(f"The installed version of {AGITO_AACOMM} is {latest_version}.")
            break

    if not installed:
        raise RuntimeError(f'{AGITO_AACOMM} nuget package is not installed.')
    
    return latest_version
