
import os
from xml.etree import ElementTree
from lxml.etree import XMLParser

import ui.log


def annotate(corePath):
    """Generate an annotated Space Haven library"""

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
            element.set("_element_name_0", nameOf(objectInfo))
    
    # Annotate basic products
    # first pass also builds the names cache
    elementNames = {}
    ProductRoot = haven.find("Product")
    for element in ProductRoot:
        name = nameOf(element) or element.get("elementType") or ""
        
        if name:
            element.set("_annotated_name", name)
        elementNames[element.get("eid")] = name
    
    for item in haven.find("Item"):
        name = nameOf(element) or element.get("elementType") or ""
        
        if name:
            element.set("_annotated_name", name)
        elementNames[element.get("mid")] = name
    
    # small helped to annotate a node
    def _annotate_elt(element, attr = None):
        if attr:
            name = elementNames[element.get(attr)]
        else:
            name = elementNames[element.get("element", element.get("elementId"))]
        if name:
            element.set("_annotated_name", name)
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
        # FIXME different attribute now
        if len(processName) > 2 and not element.get("_annotated_name"):
            elementNames[element.get("eid")] = processName
            element.set("_annotated_process", processName)
    
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
            process.set("_process_name", elementNames[process.get("process")])
    
    for trade in haven.find('TradingValues').findall('.//t'):
        try:
            _annotate_elt(trade, attr = 'eid')
        except:
            print(trade.tag)
            print(trade.attrib)
    
    #FIXME log all tids as well
    annotatedHavenPath = os.path.join(corePath, "library", "haven.annotated.xml")
    haven.write(annotatedHavenPath)
    ui.log.log("    Wrote annotated spacehaven library to {}".format(annotatedHavenPath))
