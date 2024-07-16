import logging
import os
import sys
import subprocess
import warnings
import json
import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_and_install_nvidia_packages():
    flag_file = os.path.join(os.path.dirname(__file__), '.nvidia_setup_complete')
    
    if os.path.exists(flag_file):
        logger.info("NVIDIA setup has already been completed. Skipping check and installation.")
        return

    logger.info("Checking for NVIDIA GPU...")
    try:
        import pynvml
        pynvml.nvmlInit()
        gpu_count = pynvml.nvmlDeviceGetCount()
        if gpu_count > 0 and (os.name == 'nt' or sys.platform.startswith('linux')):
            logger.info(f"Found {gpu_count} NVIDIA GPU(s).")
            try:
                driver_version = pynvml.nvmlSystemGetDriverVersion()
                if isinstance(driver_version, bytes):
                    driver_version = driver_version.decode('utf-8')
                logger.info(f"NVIDIA driver version: {driver_version}")
            except pynvml.NVMLError as e:
                logger.warning(f"Could not get driver version: {e}")

            logger.info("Attempting to install NVIDIA packages...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install",
                    "--extra-index-url=https://pypi.nvidia.com",
                    "cudf-cu12==24.6.*", "dask-cudf-cu12==24.6.*", "cuml-cu12==24.6.*"
                ])
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install",
                    "tensorrt"
                ])
                logger.info("NVIDIA packages installed successfully.")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install NVIDIA packages: {e}")
                logger.info("You may need to install these packages manually.")
        else:
            logger.info("No NVIDIA GPU detected or not on Windows/Linux. Skipping NVIDIA package installation.")
    except ImportError:
        logger.warning("pynvml is not installed. Skipping NVIDIA package check and installation.")
    except pynvml.NVMLError_DriverNotLoaded:
        logger.error("NVIDIA driver is not loaded. Please check your NVIDIA driver installation.")
    except pynvml.NVMLError_LibraryNotFound:
        logger.error("NVIDIA Management Library (NVML) not found. This might indicate an issue with your NVIDIA driver installation.")
    except pynvml.NVMLError as e:
        logger.error(f"An NVML error occurred: {e}")
        logger.info("This might indicate a mismatch between your NVIDIA driver and CUDA versions.")
        logger.info("Please ensure your NVIDIA driver and CUDA toolkit are compatible and up to date.")
    except Exception as e:
        logger.error(f"An unexpected error occurred while checking/installing NVIDIA packages: {e}")

    logger.info("Continuing with package initialization...")

    # Create the flag file to indicate setup completion
    with open(flag_file, 'w') as f:
        json.dump({'setup_completed': True, 'timestamp': str(datetime.datetime.now())}, f)

# Run the check only if it hasn't been run before
check_and_install_nvidia_packages()

# Import main functionality
from .nanosense import *

warnings.filterwarnings("ignore", category=DeprecationWarning)

__version__ = "0.5.17"  # Make sure this matches the version in pyproject.toml and setup.py