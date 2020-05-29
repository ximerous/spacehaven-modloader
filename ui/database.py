
import os
import distutils.version

from xml.etree import ElementTree

import version
import ui.log
import ui.gameinfo


class ModDatabase:
    """Information about a collection of mods"""

    def __init__(self, path, gameInfo):
        self.path = path
        self.gameInfo = gameInfo
        self.locateMods()

    def locateMods(self):
        self.mods = []

        ui.log.log("Locating mods...")
        for modFolder in os.listdir(self.path):
            if modFolder == 'spacehaven':
                continue  # don't need to load core game definitions
            modPath = os.path.join(self.path, modFolder)
            if os.path.isfile(modPath):
                # TODO add support for zip files ? unzip them on the fly ?
                continue  # don't load logs, prefs, etc
            
            info_file = os.path.join(modPath, "info")
            if os.path.isfile(info_file):
                self.mods.append(Mod(info_file, self.gameInfo))
            else:
                info_file += '.xml'
                if os.path.isfile(info_file):
                    self.mods.append(Mod(info_file, self.gameInfo))
        
        self.mods.sort(key=lambda mod: mod.name)

DISABLED_MARKER = "disabled.txt"
class Mod:
    """Details about a specific mod (name, description)"""

    def __init__(self, info_file, gameInfo):
        self.path = os.path.dirname(info_file)
        ui.log.log("  Loading mod at {}...".format(self.path))
        
        self.name = os.path.basename(self.path)

        self.gameInfo = gameInfo
        
        self.enabled = not os.path.isfile(os.path.join(self.path, DISABLED_MARKER))
               
        self.loadInfo(info_file)

    def loadInfo(self, infoFile):
        
        if not os.path.exists(infoFile):
            ui.log.log("    No info file present")
            self.name += " [!]"
            self.description = "Error loading mod: no info file present. Please create one."
            return

        try:
            info = ElementTree.parse(infoFile)
            mod = info.getroot()

            self.name = mod.find("name").text.strip()
            self.description = mod.find("description").text.strip() + "\n\n"
            self.version = ""
            try:
                self.version = mod.find("modVersion").text.strip()
            except:
                pass
            
            self.verifyLoaderVersion(mod)
            self.verifyGameVersion(mod, self.gameInfo)

        except AttributeError as ex:
            print(ex)
            self.name += " [!]"
            self.description = "Error loading mod: error parsing info file."
            ui.log.log("    Failed to parse info file")

        ui.log.log("    Finished loading {}".format(self.name))
    
    def enable(self):
        try:
            os.unlink(os.path.join(self.path, DISABLED_MARKER))
            self.enabled = True
        except:
            pass
    
    def disable(self):
        with open(os.path.join(self.path, DISABLED_MARKER), "w") as marker:
            marker.write("this mod is disabled, remove this file to enable it again (or toggle it via the modloader UI)")
        self.enabled = False
    
    def title(self):
        title = self.name
        if self.version:
            title += " (%s)" % self.version
        return title
    
    def verifyLoaderVersion(self, mod):
        self.minimumLoaderVersion = mod.find("minimumLoaderVersion").text
        if distutils.version.StrictVersion(self.minimumLoaderVersion) > distutils.version.StrictVersion(version.version):
            self.warn("Mod loader version {} is required".format(self.minimumLoaderVersion))

        ui.log.log("    Minimum Loader Version: {}".format(self.minimumLoaderVersion))

    def verifyGameVersion(self, mod, gameInfo):
        # FIXME disabled ATM as this check doesn't work
        return
        self.gameVersions = []

        gameVersionsTag = mod.find("gameVersions")
        if gameVersionsTag is None:
            self.warn("This mod does not declare what game version(s) it supports.")
            return

        for version in list(gameVersionsTag):
            self.gameVersions.append(version.text)

        ui.log.log("    Game Versions: {}".format(", ".join(self.gameVersions)))

        if not gameInfo.version:
            self.warn("Could not determine Space Haven version. You might need to update your loader.")
            return

        if not gameInfo.version in self.gameVersions:
            self.warn("This mod may not support Space Haven {}, it only supports {}.".format(
                self.gameInfo.version,
                ", ".join(self.gameVersions)
            ))



    def warn(self, message):
        ui.log.log("    Warning: {}".format(message))
        self.name += " [!]"
        self.description += "\nWARNING: {}!".format(message)
