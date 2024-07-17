import subprocess
import re
import os
import shutil

from aacommpy.settings import NET_FRAMEWORK_CHOICES, TARGET_FRAMEWORKS, TARGET_FOLDER, YAML_DOT_NET, YAML_DOT_NET_40_SRC_VER, YAML_DOT_NET_40_VER, SYSTEM_IO_PORTS, YAML_DOT_NET_48_SRC_VER
from aacommpy.settings import NET40, NET48, NET60, NET80

def check_dotnet_versions():
    target_versions = TARGET_FRAMEWORKS
    dotnet_versions = get_dotnet_versions()
    matching_versions = [dotnetfw_from_dotnet_version(version) for version in target_versions if version in dotnet_versions]

    if not matching_versions:
        print("No supported .NET Framework versions found.")
        print("Please install one of the following .NET Framework runtimes:")
        for version in target_versions:
            print(version)
    else:
        print("Installed .net framework versions which can be used with AAComm:")
        for version in matching_versions:
            print(version)

    return matching_versions

def dotnetfw_from_dotnet_version(dotnet_version):
    # Create the version mapping dynamically using the predefined lists
    version_mapping = dict(zip(TARGET_FRAMEWORKS, NET_FRAMEWORK_CHOICES))
    
    return version_mapping.get(dotnet_version, "default")

#####################
### with GPT help! ##
#####################

def copy_nuget_dependencies(version, dest_dir):
    """
    Main function to copy the necessary DLLs based on the .NET target version.

    :param version: The .NET target framework version.
    :param dest_dir: Destination directory for the DLLs.
    """
    for dir in os.listdir(TARGET_FOLDER):
        if dir.startswith(YAML_DOT_NET) and YAML_DOT_NET_40_VER not in dir:
            YAML_DOT_NET_VER = dir.split('.')[1:]
            YAML_DOT_NET_VER = '.'.join(YAML_DOT_NET_VER)
        elif dir.startswith(SYSTEM_IO_PORTS):
            SYSTEM_IO_PORTS_VERSION = dir.split('.')[3:]
            SYSTEM_IO_PORTS_VERSION = '.'.join(SYSTEM_IO_PORTS_VERSION)

    if version == NET40:
        copy_dll(YAML_DOT_NET   , YAML_DOT_NET_40_VER       , YAML_DOT_NET_40_SRC_VER, dest_dir)
    elif version == NET48:
        copy_dll(YAML_DOT_NET   , YAML_DOT_NET_VER          , YAML_DOT_NET_48_SRC_VER, dest_dir)
    elif version == NET60 or version == NET80:
        copy_dll(YAML_DOT_NET   , YAML_DOT_NET_VER          , version, dest_dir)
        copy_dll(SYSTEM_IO_PORTS, SYSTEM_IO_PORTS_VERSION   , version, dest_dir)
    else:
        raise ValueError(f"Unsupported .NET target framework version: {version}")

def copy_dll(package_name, package_version, framework_version, dest_dir):
    """
    Copy the DLL for the specified package, version, and framework to the destination directory.

    :param package_name: Name of the NuGet package.
    :param package_version: Version of the NuGet package.
    :param framework_version: Target framework version.
    :param dest_dir: Destination directory for the DLL.
    """
    dll_source_dir = os.path.join(TARGET_FOLDER, f"{package_name}.{package_version}", "lib", framework_version)
    dll_path = os.path.join(dll_source_dir, f"{package_name}.dll")

    if not os.path.isfile(dll_path):
        raise FileNotFoundError(f"Could not find {package_name}.dll in {dll_source_dir}.")

    shutil.copy2(dll_path, dest_dir)
    print(f"The {package_name} .NET target framework is {framework_version}")

# check installed .net target frameworks

def query_registry_key(path, value):
    try:
        result = subprocess.run(['reg', 'query', path, '/v', value], capture_output=True, text=True, check=True)
        output_lines = result.stdout.strip().split('\n')
        for line in output_lines:
            if value in line:
                return line.split()[-1]
    except subprocess.CalledProcessError as e:
        print(f"Error querying {value} for key {path}: {e}")
    return None

def get_dotnet_framework_versions():
    try:
        result = subprocess.run(['reg', 'query', 'HKLM\\SOFTWARE\\Microsoft\\NET Framework Setup\\NDP'], capture_output=True, text=True, check=True)
        output_lines = result.stdout.strip().split('\n')
        versions = []
        for line in output_lines:
            if '\\NDP\\v' in line:
                version_key = line.split('\\')[-1]
                if re.match(r'^v\d+(\.\d+)?$', version_key):
                    base_key = f'HKLM\\SOFTWARE\\Microsoft\\NET Framework Setup\\NDP\\{version_key}'
                    # Check for Version in the main key
                    version = query_registry_key(base_key, 'Version')
                    if version:
                        versions.append(version)
                    else:
                        # Check for Version in the Full and Client subkeys
                        for subkey in ['Full', 'Client']:
                            subkey_path = f'{base_key}\\{subkey}'
                            version = query_registry_key(subkey_path, 'Version')
                            if version:
                                versions.append(version)
                                break
                        # Check for Version in locale-specific subkeys (e.g., 1033)
                        subkey_result = subprocess.run(['reg', 'query', base_key], capture_output=True, text=True, check=True)
                        subkey_output_lines = subkey_result.stdout.strip().split('\n')
                        for subkey_line in subkey_output_lines:
                            match = re.search(r'\\(\d+)', subkey_line)
                            if match:
                                locale_subkey = match.group(1)
                                subkey_path = f'{base_key}\\{locale_subkey}'
                                version = query_registry_key(subkey_path, 'Version')
                                if version:
                                    versions.append(version)
                                    break
        return versions
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while retrieving installed .NET Framework runtimes: {e}")
        return []

def get_dotnet_core_versions():
    try:
        result = subprocess.run(['dotnet', '--list-runtimes'], capture_output=True, text=True, check=True)
        output_lines = result.stdout.strip().split('\n')
        versions = []
        for line in output_lines:
            match = re.search(r'\d+\.\d+\.\d+', line)
            if match:
                version = match.group()
                major_minor_version = '.'.join(version.split('.')[:2])  # Keep only major and minor version
                if major_minor_version not in versions:
                    versions.append(major_minor_version)
        return versions
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while retrieving installed .NET runtimes: {e}")
        return []

def get_dotnet_versions():
    framework_versions = get_dotnet_framework_versions()
    core_versions = get_dotnet_core_versions()
    all_versions = framework_versions + core_versions
    unique_versions = sorted(set(all_versions), key=lambda v: [int(part) for part in v.split('.')])

    # Keep only major versions for .NET Framework
    major_versions = []
    for version in unique_versions:
        parts = version.split('.')
        if len(parts) > 1:
            major_minor_version = f"{parts[0]}.{parts[1]}"
        else:
            major_minor_version = parts[0]
        if major_minor_version not in major_versions:
            major_versions.append(major_minor_version)
    
    return major_versions