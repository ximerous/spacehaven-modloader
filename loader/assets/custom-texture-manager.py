import math
import lxml.etree
import png
import os
import rectpack

class TextureManager:
    _TexFileResolution = 2000
    NEEDED_SIZE_MINIMUM = 0
    REGISTERED_MOD_TEXTURES = []
    REGISTERED_MOD_PATHS = dict()

    Packer = None

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

    @classmethod
    def pack(cls):
        # Should always generate plenty of space for packing.
        sizeEstimateFactor = 1.2
        NeededRegionFiles = math.ceil( cls.NEEDED_SIZE_MINIMUM * sizeEstimateFactor / (cls._TexFileResolution ** 2) )
        packer = rectpack.newPacker(rotation=False)
        cls.Packer = packer

        packer.add_bin(cls._TexFileResolution, cls._TexFileResolution, NeededRegionFiles)

        for rt in cls.REGISTERED_MOD_TEXTURES:
            rt: RegisteredTexture
            packer.add_rect(rt.FileSizeX, rt.FileSizeY, cls.REGISTERED_MOD_TEXTURES.index(rt))

        packer.pack()


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
    # TODO Remove this hard lock to my own mods and make some test files.
    TextureManager.registerNewTexture("../mods/Wiring", "busPanelFloor.png")
    TextureManager.registerNewTexture("../mods/Wiring", "busPanelWallFront.png")
    TextureManager.registerNewTexture("../mods/Wiring", "busPanelWallBack.png")
    TextureManager.registerNewTexture("../mods/Wiring", "wiringpanel.png")
    TextureManager.registerNewTexture("../mods/Wiring", "wiringPanelWallBack.png")
    TextureManager.registerNewTexture("../mods/Wiring", "wiringPanelWallFront.png")
    for rt in TextureManager.REGISTERED_MOD_TEXTURES:
        print(rt)
    TextureManager.pack()
    for rect in TextureManager.Packer.rect_list():
        bin, x, y, w, h, rid = rect
        print(f"[b{bin}, r{rid:>3}] {x:>3}x, {y:>3}y")
    print("CTM compiles.")