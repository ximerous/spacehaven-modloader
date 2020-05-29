
import os

import loader.assets.library
import loader.assets.explode
import loader.assets.annotate

import ui.log

def extract(jarPath, corePath):
    """Extract and annotate game assets"""

    ui.log.log("Running extract & annotate")

    ui.log.updateBackgroundState("Extracting game files")
    loader.assets.library.extract(jarPath, corePath)

    ui.log.updateBackgroundState("Unpacking textures")
    loader.assets.explode.explode(corePath)
    
    ui.log.updateBackgroundState("Annotating XML")
    loader.assets.annotate.annotate(corePath)
