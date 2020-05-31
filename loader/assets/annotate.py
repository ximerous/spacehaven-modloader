
import os
from xml.etree import ElementTree
from lxml.etree import XMLParser

import ui.log

def annotate(corePath):
    """Generate an annotated Space Haven library"""

    texture_names = {}
    local_texture_names = ElementTree.parse("textures_annotations.xml", parser=XMLParser(recover=True))
    for region in local_texture_names.findall(".//re[@n]"):
        if not region.get("_annotation"):
            continue
        texture_names[region.get('n')] = region.get("_annotation")
    
    animations = ElementTree.parse(os.path.join(corePath, "library", "animations"), parser=XMLParser(recover=True))
    for assetPos in animations.findall('.//assetPos[@a]'):
        asset_id = assetPos.get('a')
        if not asset_id in texture_names:
            continue
        assetPos.set('_annotation', texture_names[asset_id])
    
    annotatedPath = os.path.join(corePath, "library", "animations_annotated.xml")
    animations.write(annotatedPath)
    ui.log.log("    Wrote annotated annimations to {}".format(annotatedPath))
    
    haven = ElementTree.parse(os.path.join(corePath, "library", "haven"), parser=XMLParser(recover=True))
    texts = ElementTree.parse(os.path.join(corePath, "library", "texts"), parser=XMLParser(recover=True))
        
    tids = {}
    # Load texts
    for text in texts.getroot():
        tids[text.get("id")] = text.find("EN").text
    
    def nameOf(element):
        name = element.find("name")
        if name is None:
            return ""

        tid = name.get("tid")
        if tid is None:
            return ""

        return tids[tid]
    
    ElementRoot = haven.find("Element")
    # Annotate Elements
    for element in ElementRoot:
        mid = element.get("mid")

        objectInfo = element.find("objectInfo")
        if objectInfo is not None:
            element.set("_annotation", nameOf(objectInfo))
    
    # Annotate basic products
    # first pass also builds the names cache
    elementNames = {}
    ProductRoot = haven.find("Product")
    for element in ProductRoot:
        name = nameOf(element) or element.get("elementType") or ""
        
        if name:
            element.set("_annotation", name)
        elementNames[element.get("eid")] = name
    
    for item in haven.find("Item"):
        name = nameOf(item) or item.get("elementType") or ""
        
        if name:
            item.set("_annotation", name)
        elementNames[item.get("mid")] = name
    
    # small helped to annotate a node
    def _annotate_elt(element, attr = None):
        if attr:
            name = elementNames[element.get(attr)]
        else:
            name = elementNames[element.get("element", element.get("elementId"))]
        if name:
            element.set("_annotation", name)
        return name
    
    # construction blocks for the build menu
    for me in ElementRoot:
        for customPrice in me.findall(".//customPrice"):
            for sub_l in customPrice:
                _annotate_elt(sub_l)
    
    # specific processes for the crops
    for element in []: #ProductRoot:
        if element.get('type', None) != 'Crop':
            continue
        for need in element.findall(".//needs"):
            for sub_l in need:
                _annotate_elt(sub_l)
        
        for product in element.findall(".//products"):
            for sub_l in product:
                _annotate_elt(sub_l)
    
    # Annotate facility processes, now that we know the names of all the products involved
    for element in ProductRoot:
        processName = []
        needs = element.find("needs") or []
        for need in needs:
            name = _annotate_elt(need)
            processName.append(name)

        processName.append("to")

        products = element.find("products") or []
        for product in products:
            name = _annotate_elt(product)
            processName.append(name)

        processName = " ".join(processName)
        if len(processName) > 2 and not element.get("_annotation"):
            elementNames[element.get("eid")] = processName
            element.set("_annotation", processName)
    
    #generic rule should work for all remaining nodes ?
    for sub_element in haven.findall(".//*[@consumeEvery]"):
        try:
            _annotate_elt(sub_element)
        except:
            # error on 446, weird stuff
            print(sub_element.tag)
            print(sub_element.attrib)
    
    # iterate again once we have built all the process names
    for element in ProductRoot:
        processes = element.find("list")
        if not processes:
            continue
        for process in processes.find("processes"):
            process.set("_annotation", elementNames[process.get("process")])
    
    for trade in haven.find('TradingValues').findall('.//t'):
        try:
            _annotate_elt(trade, attr = 'eid')
        except:
            print(trade.tag)
            print(trade.attrib)
    
    annotatedHavenPath = os.path.join(corePath, "library", "haven_annotated.xml")
    haven.write(annotatedHavenPath)
    ui.log.log("    Wrote annotated spacehaven library to {}".format(annotatedHavenPath))
