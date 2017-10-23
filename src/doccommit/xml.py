"""
Contains helper classes and functions for DocBook XML
"""

def get_source_xml_ids(xml_source_ids):
    """
    Get all XML IDs from DocBook source. This can be executed in a thread.
    The parameter is a pointer to variable that stores the result.
    """
    import os
    from lxml import etree
    path = str(os.getcwd())+"/xml/"
    for file in os.listdir(path):
        if str(file).startswith("MAIN") and str(file).endswith(".xml"):
            print(path+str(file))
            xml = etree.parse(path+str(file))
            xml.xinclude()
            for i in xml.xpath("//*[@xml:id]", namespaces={'d': "http://docbook.org/ns/docbook"}):
                xml_source_ids[i.attrib['{http://www.w3.org/XML/1998/namespace}id']] = \
                i.findtext('d:title', namespaces={'d': "http://docbook.org/ns/docbook"})
