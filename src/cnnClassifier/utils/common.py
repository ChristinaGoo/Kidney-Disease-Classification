# Shared utility functions used across all pipeline components (e.g. read yaml, save json, load/save models).
# @ensure_annotations enforces type hints at runtime on each function, catching wrong argument types early.


import os
from box.exceptions import BoxValueError
import yaml
from cnnClassifier import logger
import json
import joblib
from ensure import ensure_annotations
from box import ConfigBox
from pathlib import Path
from typing import Any
import base64


@ensure_annotations
def read_yaml(path_to_yaml: Path) -> ConfigBox:
    """Reads a yaml file and returns

    Args:
        path_to_yaml (str): Path like input
        
    Raises:
        ValueError: If yaml file is empty
        e: empty file
    Returns:
        ConfigBox: ConfigBox type
    """
    
    try:
        with open(path_to_yaml) as yaml_file:
            content = yaml.safe_load(yaml_file)
            logger.info(f"yaml file: {path_to_yaml} loaded successfully")
            return ConfigBox(content)
    except BoxValueError:
        raise ValueError("yaml file is empty")
    except Exception as e:
        raise e
    
    
    
@ensure_annotations
def create_directories(path_to_directories: list, verbose=True):
    """Creates list of directories

    Args:
        path_to_directories (list): list of path of directories
        verbose (bool, optional): log directory creation. Defaults to True.
    """
    for path in path_to_directories:
        os.makedirs(path, exist_ok=True)
        if verbose:
            logger.info(f"created directory at: {path}")
            

@ensure_annotations
def save_json(path: Path, data: dict):
    """Saves json data to file

    Args:
        path (Path): path to json file
        data (dict): data to be saved in json file
    """
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    logger.info(f"json file saved at: {path}")
 
 
    
@ensure_annotations
def load_json(path: Path) -> ConfigBox:
    """Loads json file and returns as ConfigBox

    Args:
        path (Path): path to json file

    Returns:
        ConfigBox: ConfigBox type
    """
    with open(path, "r") as f:
        content = json.load(f)
        
    logger.info(f"json file loaded successfully from: {path}")
    return ConfigBox(content)


@ensure_annotations
def save_bin(data: Any, path: Path):
    """Saves binary data to file

    Args:
        data (Any): data to be saved in binary file
        path (Path): path to binary file
    """
    joblib.dump(value=data, filename=path)
    logger.info(f"binary file saved at: {path}")
    
    
    

@ensure_annotations
def load_bin(path: Path) -> Any:
    """Loads binary file and returns data

    Args:
        path (Path): path to binary file

    Returns:
        Any: data loaded from binary file
    """
    data = joblib.load(path)
    logger.info(f"binary file loaded from: {path}")
    return data


@ensure_annotations
def get_size(path: Path) -> str:
    """Returns size of file in KB

    Args:
        path (Path): path to file

    Returns:
        str: size of file in KB
    """
    size_in_kb = round(os.path.getsize(path)/1024)
    logger.info(f"file size for path: {path} is: {size_in_kb} KB")
    return f"~ {size_in_kb} KB"

def decodeImage(imgstring, fileName):
    """Decodes a base64 image string and saves it to a file.

    Args:
        imgstring (str): Base64 encoded image string.
        fileName (str): Path where the decoded image will be saved.
    """
    imgdata = base64.b64decode(imgstring)
    with open(fileName, "wb") as f:
        f.write(imgdata)
        
                
def encodeImageIntoBase64(croppedImagePath):
    """Encodes an image file into a base64 string.

    Args:
        croppedImagePath (str): Path to the image file to be encoded.

    Returns:
        str: Base64 encoded string of the image.
    """
    with open(croppedImagePath, "rb") as f:
        imgdata = f.read()
        return base64.b64encode(imgdata).decode("utf-8")