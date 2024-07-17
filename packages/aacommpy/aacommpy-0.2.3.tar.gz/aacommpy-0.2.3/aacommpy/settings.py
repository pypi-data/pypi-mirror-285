import os

# .NET framework versions supported by AAComm nuget package
NET40                   = 'net40'
NET48                   = 'net48'
NET60                   = 'net6.0'
NET80                   = 'net8.0'

NET_FRAMEWORK_CHOICES   = [NET40, NET48, NET60, NET80]
TARGET_FRAMEWORKS       = ["4.0", "4.8", "6.0", "8.0"]
DEFAULT_NET_FRAMEWORK   = NET48

TARGET_FOLDER           = os.path.join(os.path.dirname(__file__), 'aacommpyDownloader-main')
NUGET_EXE               = 'nuget.exe'
NUGET_EXE_PATH          = os.path.join(TARGET_FOLDER, NUGET_EXE)

# nuget dependencies and special case for .NET 4.0
YAML_DOT_NET            = 'YamlDotNet'
YAML_DOT_NET_40_VER     = '4.2.2'
YAML_DOT_NET_40_SRC_VER = 'net35'
YAML_DOT_NET_48_SRC_VER = 'net47'
SYSTEM_IO_PORTS         = 'System.IO.Ports'

AGITO_AACOMM            = 'Agito.AAComm'
AACOMM_DLL              = 'AAComm.dll'
AACOMMSERVER            = 'AACommServer'

# there will be 2 constants add into this file name "AACOMM_DLL_PATH" and "AACOMM_SERVER_EXE_PATH" when run "aacommpy install" and "aacommpy update"
current_dir             = os.path.dirname(__file__)
AACOMM_DLL_PATH         = os.path.join(current_dir, AACOMM_DLL)
AACOMM_SERVER_EXE_PATH  = os.path.join(current_dir, f'{AACOMMSERVER}.exe')