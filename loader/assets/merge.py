
import os
import copy
import lxml.etree

import loader.assets.library
from .library import PATCHABLE_XML_FILES, PATCHABLE_CIM_FILES
from .explode import Texture

import ui.log

def _detect_textures(coreLibrary, modLibrary, mod):
    textures_path = os.path.join(mod, 'textures')
    if not os.path.isdir(textures_path):
        return {}
    
    mapping_n_region = {}
    modded_textures = {}
    seen_textures = set()
    
    def _add_texture(region_id):
        filename = region_id + '.png'
        if filename in seen_textures:
            return
        
        path = os.path.join(textures_path, filename)
        if not os.path.isfile(path):
            ui.log.log("  ERROR MISSING {}...".format(filename))
            ui.log.log("  ERROR MISSING {}...".format(filename))
            ui.log.log("  ERROR MISSING {}...".format(filename))
            return
        
        ui.log.log("  Found {}...".format(filename))
        if int(region_id) > coreLibrary['_last_core_region_id']:
            # adding a new texture, this gets tricky as they have to have consecutive numbers. 
            core_region_id = str(coreLibrary['_next_region_id'])
            mapping_n_region[region_id] = core_region_id
            coreLibrary['_next_region_id'] += 1
        else:
            core_region_id = region_id
        
        seen_textures.add(filename)
        modded_textures[core_region_id] = {
            'mapped_from_id' : region_id,
            'filename' : filename,
            'path' : path, 
            }
    
    for filename in os.listdir(textures_path):
        # also scan the directory for overwriting existing core textures
        if not filename.endswith('.png'):
            continue
        try:
            int(filename.split('.')[0])
        except:
            # wrong format
            continue
        _add_texture(filename.split('.')[0])
    
    if 'library/textures' not in modLibrary:
        # no textures.xml file, we're done
        return modded_textures
    
    for texture_pack in modLibrary['library/textures'].xpath("//t[@i]"):
        cim_id = texture_pack.get('i')
        coreLibrary['_custom_textures_cim'][cim_id] = texture_pack.attrib
    
    for region in modLibrary['library/textures'].xpath("//re[@n]"):
        region_id = region.get('n')
        _add_texture(region_id)
    
    if not mapping_n_region:
        # no custom mod textures, no need to remap ids 
        return modded_textures
    
    for asset in modLibrary['library/animations'].xpath("//assetPos[@a]"):
        mod_local_id = asset.get('a')
        if mod_local_id not in mapping_n_region:
            continue
        new_id = mapping_n_region[mod_local_id]
        ui.log.log("  Mapping animation 'assetPos' {} to {}...".format(mod_local_id, new_id))
        asset.set('a', new_id)
    
    for asset in modLibrary['library/textures'].xpath("//re[@n]"):
        mod_local_id = asset.get('n')
        if mod_local_id not in mapping_n_region:
            continue
        new_id = mapping_n_region[mod_local_id]
        ui.log.log("  Mapping texture 're' {} to {}...".format(mod_local_id, new_id))
        asset.set('n', new_id)
    
    return modded_textures


def mods(corePath, modPaths):
    # Load the core library files
    coreLibrary = {}
    def _core_path(filename):
        return os.path.join(corePath, filename.replace('/', os.sep))
    
    for filename in PATCHABLE_XML_FILES:
        with open(_core_path(filename), 'rb') as f:
            coreLibrary[filename] = lxml.etree.parse(f, parser=lxml.etree.XMLParser(recover=True))
    
    # find the last region in the texture file and remember its index
    # we will need this to add mod textures with consecutive indexes...
    coreLibrary['_last_core_region_id'] = int(coreLibrary['library/textures'].find("//re[@n][last()]").get('n'))
    coreLibrary['_next_region_id'] = coreLibrary['_last_core_region_id'] + 1
    coreLibrary['_all_modded_textures'] = {}
    coreLibrary['_custom_textures_cim'] = {}
    
    # Merge in modded files
    for mod in modPaths:
        ui.log.updateLaunchState("Installing {}".format(os.path.basename(mod)))
        
        ui.log.log("  Loading mod {}...".format(mod))
        
        # Load the mod's library
        modLibrary = {}
        def _mod_path(filename):
            return os.path.join(mod, filename.replace('/', os.sep))
        
        for filename in PATCHABLE_XML_FILES:
            mod_file = _mod_path(filename)
            if not os.path.exists(mod_file):
                # try again with the extension ?
                mod_file += '.xml'
                if not os.path.exists(mod_file):
                    continue
            with open(mod_file) as f:
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
        
        # do that before merging animations and textures because references might have to be remapped!
        coreLibrary['_all_modded_textures'].update(_detect_textures(coreLibrary, modLibrary, mod))
        
        # this way the last mod loaded will overwrite previous textures
        #FIXME reimplement this test
        #                if region_id in all_modded_textures:
        #            ui.log.log("  ERROR CONFLICT {}...".format(filename))
        #            ui.log.log("  ERROR CONFLICT {}...".format(filename))
        #            ui.log.log("  ERROR CONFLICT {}...".format(filename))
        #            continue
        
        mergeDefinitions(coreLibrary, modLibrary, file="library/animations", xpath="/AllAnimations/animations", idAttribute="n")
        mergeDefinitions(coreLibrary, modLibrary, file="library/textures", xpath="/AllTexturesAndRegions/textures", idAttribute="i")
        mergeDefinitions(coreLibrary, modLibrary, file="library/textures", xpath="/AllTexturesAndRegions/regions", idAttribute="n")
        

    ui.log.updateLaunchState("Updating XML")
    
    # Write out the new base library
    for filename in PATCHABLE_XML_FILES:        
        with open(_core_path(filename), "wb") as f:
            f.write(lxml.etree.tostring(coreLibrary[filename], pretty_print=True, encoding="UTF-8"))
    
    ui.log.updateLaunchState("Packing textures".format(mod))
    # add or overwrite textures from mods. This is done after all the XML has been merged into the core "textures" file
    cims = {}
    reexport_cims = {}
    extra_assets = []
    
    for region in coreLibrary['library/textures'].xpath("//re[@n]"):
        name = region.get("n")
        
        if name not in coreLibrary['_all_modded_textures']:
            continue
        
        png_file = coreLibrary['_all_modded_textures'][name]['path']
        
        page = region.get("t")
        if not page in cims:
            cim_name = '{}.cim'.format(page)
            kwargs = {'create': False}
            # TODO better cross checking of texture packs
            if 'library/' + cim_name not in PATCHABLE_CIM_FILES:
                kwargs['create'] = True
                kwargs['width'] = coreLibrary['_custom_textures_cim'][page]['w']
                kwargs['height'] = coreLibrary['_custom_textures_cim'][page]['h']
                extra_assets.append('library/' + cim_name)
            cims[page] = Texture(os.path.join(corePath, 'library', cim_name), **kwargs)
                
            reexport_cims[page] = set()
        
        # write back the cim file as png for debugging
        reexport_cims[page].add(os.path.dirname(png_file))
        
        x = int(region.get("x"))
        y = int(region.get("y"))
        w = int(region.get("w"))
        h = int(region.get("h"))
        
        ui.log.log("  Patching {}.cim...".format(page))
        cims[page].pack_png(png_file, x, y, w, h)
    
    # cims contains only the textures files that have actually been modified
    for page in cims:
        ui.log.log("  Writing {}.cim...".format(page))
        cims[page].export_cim(os.path.join(corePath, 'library', '{}.cim'.format(page)))
        for path in reexport_cims[page]:
            cims[page].export_png(os.path.join(path, 'modded_cim_{}.png'.format(page)))
    
    return extra_assets


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
