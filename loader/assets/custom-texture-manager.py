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
    testFileDir = "unit-tests/textures"
    for filename in os.listdir(testFileDir):
        repeat = os.stat(os.path.join(testFileDir, filename)).st_size
        # magic numbers chosen semi-randomly to get a good spread of repeats
        repeat = math.ceil((210 - repeat)/ 9) ** 2
        print(f"{filename:>11} - {repeat:>2}")
        for x in range(repeat):
            TextureManager.registerNewTexture("unit-tests", filename)

    TextureManager.pack()

    for bin in TextureManager.Packer:
        r1str = f"x{bin[ 0].x}, y{bin[ 0].y} ({bin[ 0].rid})"
        r2str = f"x{bin[-1].x}, y{bin[-1].y} ({bin[-1].rid})"
        binstr = f"{len(bin):>3} rects, first {r1str}, last {r2str}"
        print(binstr)
    print("CTM compiles.")