
import os
import copy
import lxml.etree

import loader.assets.library
from .explode import Texture

import ui.log


def mods(corePath, modPaths):
    # Load the core library files
    coreLibrary = {}
    for filename in loader.assets.library.PATCHABLE_XML_FILES:
        with open(os.path.join(corePath, filename), 'rb') as f:
            coreLibrary[filename] = lxml.etree.parse(f, parser=lxml.etree.XMLParser(recover=True))
    
    modded_textures = {}
    # Merge in modded files
    for mod in modPaths:
        ui.log.log("  Loading mod {}...".format(mod))
        
        # Load the mod's library
        modLibrary = {}
        for filename in loader.assets.library.PATCHABLE_XML_FILES:
            modLibraryFilePath = os.path.join(mod, filename.replace('/', os.sep))
            if os.path.exists(modLibraryFilePath):
                with open(modLibraryFilePath) as f:
                    modLibrary[filename] = lxml.etree.parse(f, parser=lxml.etree.XMLParser(remove_comments=True))

        # Do an element-wise merge (replacing conflicts)
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/Randomizer", idAttribute="id")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/GOAPAction", idAttribute="id")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/BackPack", idAttribute="mid")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/Element", idAttribute="mid")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/Product", idAttribute="eid")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/DataLogFragment", idAttribute="id")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/RandomShip", idAttribute="id")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/IsoFX", idAttribute="id")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/Item", idAttribute="mid")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/SubCat", idAttribute="id")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/Monster", idAttribute="cid")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/PersonalitySettings", idAttribute="id")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/Encounter", idAttribute="id")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/CostGroup", idAttribute="id")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/CharacterSet", idAttribute="cid")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/Room", idAttribute="rid")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/ObjectiveCollection", idAttribute="nid")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/Notes", idAttribute="id")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/DialogChoice", idAttribute="id")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/Faction", idAttribute="id")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/CelestialObject", idAttribute="id")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/Character", idAttribute="cid")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/Craft", idAttribute="cid")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/Sector", idAttribute="id")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/DataLog", idAttribute="id")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/Plan", idAttribute="id")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/BackStory", idAttribute="id")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/DefaultStuff", idAttribute="id")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/TradingValues", idAttribute="id")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/CharacterTrait", idAttribute="id")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/Effect", idAttribute="id")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/CharacterCondition", idAttribute="id")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/Ship", idAttribute="rid")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/IdleAnim", idAttribute="id")
        mergeDefinitions(coreLibrary, modLibrary, file="library/haven", xpath="/data/MainCat", idAttribute="id")

        mergeDefinitions(coreLibrary, modLibrary, file="library/texts", xpath="/t", idAttribute="id")
        mergeDefinitions(coreLibrary, modLibrary, file="library/animations", xpath="/AllAnimations/animations", idAttribute="id")
        
        textures_path = os.path.join(mod, 'textures')
        if not os.path.isdir(textures_path):
            continue
        
        for filename in os.listdir(textures_path):
            if not filename.endswith('.png'):
                continue
            try:
                int(filename.split('.')[0])
            except:
                continue
            ui.log.log("  Found {}...".format(filename))
            # this way the last mod loaded will overwrite previous textures
            # FIXME detect and print conflicts
            modded_textures[filename] = os.path.join(textures_path, filename)            
        


    # Write out the new base library
    for filename in loader.assets.library.PATCHABLE_XML_FILES:        
        with open(os.path.join(corePath, filename.replace('/', os.sep)), "wb") as f:
            f.write(lxml.etree.tostring(coreLibrary[filename], pretty_print=True, encoding="UTF-8"))
    
    # add or patch textures from mods (only patching currently)
    textures = lxml.etree.parse(os.path.join(corePath, "library", "textures"), parser=lxml.etree.XMLParser(recover=True))
    cims = {}
    reexport_cims = {}
    
    regions = textures.xpath("//re[@n]")
    
    for region in regions:
        name = region.get("n")
        png_filename = name + ".png"
        if png_filename not in modded_textures:
            continue
        
        page = region.get("t")
        if not page in cims:
            cims[page] = Texture(os.path.join(corePath, 'library', '{}.cim'.format(page)))
                
            reexport_cims[page] = set()
        
        # write back the cim file as png for debugging
        reexport_cims[page].add(os.path.dirname(modded_textures[png_filename]))
        
        x = int(region.get("x"))
        y = int(region.get("y"))
        
        ui.log.log("  Patching {}.cim...".format(page))
        cims[page].pack_png(modded_textures[png_filename], x, y)
        # FIXME check w/h vs png file!
        w = int(region.get("w"))
        h = int(region.get("h"))
    
    # cims contains only the textures files that have actually been modified
    for page in cims:
        ui.log.log("  Writing {}.cim...".format(page))
        cims[page].export_cim(os.path.join(corePath, 'library', '{}.cim'.format(page)))
        for path in reexport_cims[page]:
            cims[page].export_png(os.path.join(path, 'cim_{}.png'.format(page)))



def mergeDefinitions(baseLibrary, modLibrary, file, xpath, idAttribute):
    if not file in modLibrary:
        ui.log.log("    {}: Not present".format(file))
        return

    try:
        modRoot = modLibrary[file].xpath(xpath)[0]
        baseRoot = baseLibrary[file].xpath(xpath)[0]
    except IndexError:
        # ui.log.log("    {}: Nothing at {}".format(file, xpath))
        return

    for element in list(modRoot):
        conflicts = baseRoot.xpath("*[@{}='{}']".format(idAttribute, element.get(idAttribute)))

        for conflict in conflicts:
            baseRoot.remove(conflict)

        baseRoot.append(copy.deepcopy(element))

    ui.log.log("    {}: Merged {} elements into {}".format(file, len(list(modRoot)), xpath))
