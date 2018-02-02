"""
parse_config.py
===================

Parses config file for nappy.

"""

# Standard library imports
import ConfigParser
import os


# Global variables

# Defaults are always loaded from <nappy-egg>/nappy/config/nappy.ini
_here = os.path.dirname(__file__)
base_dir = os.path.join(_here, '../config')

config_file = os.path.join(base_dir, "nappy.ini")
config_dict = None
annotations_config_dict = None
attributes_config_dict = None

class MyCasePreservingConfigParser(ConfigParser.ConfigParser):
    optionxform = str

def makeConfigDict(cf=config_file):
    """
    Parses config file and returns dictionary of sub-dictionaries
    for each section holding Keyword-Value pairs.
    """
    d = {}
    conf = MyCasePreservingConfigParser()
    conf.read(cf)

    # get all sections and content 
    for section in conf.sections():
        d[section] = {}
        for item in conf.options(section):
            value = conf.get(section, item)
            if value.find("__space__") > -1:
                value = value.replace("__space__", " ")

            if item.find("&") > -1:
                item = tuple(item.split("&"))
            if value.find("&") > -1:
                value = tuple(value.split("&"))
            d[section][item] = value

    return d


def getConfigDict(cf=config_file):
    "Checks if already made and only makes if required."
    global config_dict
    if config_dict == None:
        config_dict = makeConfigDict(cf)
    return config_dict


def makeAnnotationsConfigDict(af):
    """
    Parses annotations config file and returns dictionary of annotations.
    """
    ad = {}
    conf = MyCasePreservingConfigParser()
    conf.read(af)

    # Load up dict
    for item in conf.options("annotations"):
        value = conf.get("annotations", item)
        ad[item] = value

    return ad


def getAnnotationsConfigDict():
    "Checks if already made and only makes if required."
    config_dict = getConfigDict()

    annotations_config_file = os.environ.get("NAPPY_ANNOTATIONS", None) or \
                              os.path.join(base_dir, config_dict["main"]["annotations_file"])

    global annotations_config_dict

    if annotations_config_dict == None:
        annotations_config_dict = makeAnnotationsConfigDict(annotations_config_file)

    return annotations_config_dict


def makeLocalAttributesConfigDict(laf):
    """
    Parses local attributes config file and returns dictionary.
    """
    lad = {}
    conf = MyCasePreservingConfigParser()
    conf.read(laf)

    # Load up dict
    for sect in ("nc_attributes", "na_attributes"):
        lad[sect] = {}
        for item in conf.options(sect):
            value = conf.get(sect, item)
            lad[sect][item] = value

    return lad


def getLocalAttributesConfigDict():
    "Checks if already made and only makes if required."
    config_dict = getConfigDict()

    local_attributes_config_file = os.environ.get("NAPPY_LOCAL_ATTRIBUTES", None) or \
                                   os.path.join(base_dir, config_dict["main"]["local_attributes_file"])
    
    global attributes_config_dict

    if attributes_config_dict == None:
        attributes_config_dict = makeLocalAttributesConfigDict(local_attributes_config_file)
    return attributes_config_dict



if __name__=="__main__":

    print getConfigDict()
    print getAnnotationsConfigDict()
    print getLocalAttributesConfigDict()

