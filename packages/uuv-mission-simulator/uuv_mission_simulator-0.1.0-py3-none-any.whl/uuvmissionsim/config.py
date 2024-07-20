import os


# Base directory of the package
base_dir = os.path.dirname(os.path.abspath(__file__))

U_PATH = "/data/u.nc"
V_PATH = "/data/v.nc"
W_PATH = "/data/w.nc"
CTD_DATA_PATHS = ['/data/salt.nc',
 '/data/rho.nc',
 '/data/temp.nc']

# Data Paths
# U_PATH = os.path.join(base_dir, 'data', 'u.nc')
# V_PATH = os.path.join(base_dir, 'data', 'v.nc')
# W_PATH = os.path.join(base_dir, 'data', 'w.nc')
# CTD_DATA_PATHS = [
#     os.path.join(base_dir, 'data', 'salt.nc'),
#     os.path.join(base_dir, 'data', 'temp.nc'),
#     os.path.join(base_dir, 'data', 'rho.nc')
# ]

# Sensor Frequency
ADCP_FREQUENCY = int(os.getenv('ADCP_FREQUENCY', 2))  # Hz
CTD_FREQUENCY = int(os.getenv('CTD_FREQUENCY', 16))  # Hz

# ADCP Settings
VERTICAL_SPACING = float(os.getenv('VERTICAL_SPACING', 0.25))  # Spacing between z points
Z_ABOVE_PATH = float(os.getenv('Z_ABOVE_PATH', 4))  # Maximum depth above the original path
Z_BELOW_PATH = float(os.getenv('Z_BELOW_PATH', -4))  # Maximum depth below the original path
BLANKING_DISTANCE = float(os.getenv('BLANKING_DISTANCE', 0.75)) # Blanking distance around UUV

def update_config(**kwargs):
    global U_PATH, V_PATH, W_PATH, CTD_DATA_PATHS, ADCP_FREQUENCY, CTD_FREQUENCY, VERTICAL_SPACING, Z_ABOVE_PATH, Z_BELOW_PATH, BLANKING_DISTANCE
    for key, value in kwargs.items():
        if key in globals():
            globals()[key] = value
        else:
            raise KeyError(f"Key '{key}' not found in the configuration")