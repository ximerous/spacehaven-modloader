
import os
import distutils.version

from xml.etree import ElementTree

import version
import ui.log
import ui.gameinfo


class ModDatabase:
    """Information about a collection of mods"""
    __lastInstance = None

    def __init__(self, path_list, gameInfo):
        self.path_list = path_list
        self.gameInfo = gameInfo
        self.locateMods()
        ModDatabase.__lastInstance = self

    def locateMods(self):
        self.mods = []

        ui.log.log("Locating mods...")
        for path in self.path_list:
            for modFolder in os.listdir(path):
                if 'spacehaven' in modFolder:
                    continue  # don't need to load core game definitions
                modPath = os.path.join(path, modFolder)
                if os.path.isfile(modPath):
                    # TODO add support for zip files ? unzip them on the fly ?
                    continue  # don't load logs, prefs, etc
                
                # TODO Pass the mod path to Mod() instead of the info_file and let it handle
                # the info file check. It already does this! Let it do its job!
                info_file = os.path.join(modPath, "info")
                if not os.path.isfile(info_file):
                    info_file += '.xml'
                if not os.path.isfile(info_file):
                    # no info file, don't create a mod.
                    continue

                self.mods.append(Mod(info_file, self.gameInfo))
        
        self.mods.sort(key=lambda mod: mod.name)

    def getInstance():
        """Return the last generated instance of a mod database."""
        if ModDatabase is None:
            raise Exception("Mod Database not ready.")
        return ModDatabase.__lastInstance

DISABLED_MARKER = "disabled.txt"
class Mod:
    """Details about a specific mod (name, description)"""

    def __init__(self, info_file, gameInfo):
        self.path = os.path.dirname(info_file)
        ui.log.log("  Loading mod at {}...".format(self.path))
        
        # TODO add a flag to warn users about savegame compatibility ?
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
        
        def _sanitize(elt):
            return elt.text.strip("\r\n\t ")
        
        def _optional(tag):
            try:
                return _sanitize(mod.find(tag))
            except:
                return ""
        
        try:
            info = ElementTree.parse(infoFile)
            mod = info.getroot()

            self.name = _sanitize(mod.find("name"))
            self.description = _sanitize(mod.find("description"))
            
            self.known_issues = _optional("knownIssues")
            self.version = _optional("version")
            self.author = _optional("author")
            self.website = _optional("website")
            self.updates = _optional("updates")
            
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
    
    def getDescription(self):
        """Build a description from the mod data"""
        description = self.description
        if self.known_issues:
            description += "\n\n" + "KNOWN ISSUES: " + self.known_issues
        if self.author:
            description += "\n\n" + "AUTHOR: " + self.author
        if self.website:
            # FIXME make it a separate textfield, can't select from this one
            description += "\n\n" + "URL: " + self.website
        return description

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
