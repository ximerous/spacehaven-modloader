import math
import lxml.etree
import png
import os

class TextureManager:
    _TexFileResolution = 2000
    NEEDED_SIZE_MINIMUM = 0
    REGISTERED_MOD_TEXTURES = []
    REGISTERED_MOD_PATHS = dict()


    @classmethod
    def registerNewTexture(cls, mod: str, texPath: str):
        # TODO Figure out how we'll be getting the correct core region ID
        tmp = RegisteredTexture(mod, texPath, 0)
        cls.REGISTERED_MOD_TEXTURES.append(tmp)
        cls.NEEDED_SIZE_MINIMUM += tmp.FileSizeX * tmp.FileSizeY

    @classmethod
    def getModTexturePath(cls, mod: str, texPath: str):
        if mod not in cls.REGISTERED_MOD_PATHS:
            texFolderPath = os.path.join(mod, "textures")
            if os.path.exists(texFolderPath):
                cls.REGISTERED_MOD_PATHS[mod] = texFolderPath
            else:
                raise FileNotFoundError(f"Couldn't find {texFolderPath}")
        return os.path.join(cls.REGISTERED_MOD_PATHS[mod], texPath)


class RegisteredTexture:
    """All the metadata needed to construct a region node."""
    ParentMod: str
    TexPath: str
    CoreRegionID: int
    FileSizeX: int
    FileSizeY: int

    def __init__(self, mod: str, texPath: str, regionID: int):
        self.ParentMod = mod
        self.TexPath = texPath
        self.CoreRegionID = regionID

        filepath = TextureManager.getModTexturePath(self.ParentMod, self.TexPath)
        (w, h, rows, info) = png.Reader(filepath).asRGBA()

        self.FileSizeX = w
        self.FileSizeY = h
    
    def __str__(self):
        return f"[{self.CoreRegionID:0>5}] {self.ParentMod}: {self.TexPath} - ({self.FileSizeX}, {self.FileSizeY})"


if __name__ == "__main__":
    """Run some basic unit tests."""
    tmp = RegisteredTexture("../mods/Wiring", "wiringpanel.png", 1)
    print(tmp)
    print(repr(tmp))
    print("CTM compiles.")