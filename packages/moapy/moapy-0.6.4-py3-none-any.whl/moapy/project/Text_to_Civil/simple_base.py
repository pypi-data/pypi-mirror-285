from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
import numpy as np
import json
from dataclasses import dataclass, field as dataclass_field

@dataclass
class PrintColor:
    """
    The color of the RGB, [0~255, 0~255, 0~255]
    """
    r: int = dataclass_field(default=0, metadata={"description": "The red component of the color"})
    g: int = dataclass_field(default=0, metadata={"description": "The green component of the color"})
    b: int = dataclass_field(default=0, metadata={"description": "The blue component of the color"})