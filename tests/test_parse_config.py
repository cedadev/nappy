from nappy.utils.parse_config import (getConfigDict, getAnnotationsConfigDict, 
                                      getLocalAttributesConfigDict) 


def test_getConfigDict():
    cd = getConfigDict()
    assert cd["main"]["default_float_format"] == "%.10g"


def test_getAnnotationsConfigDict():
    ad = getAnnotationsConfigDict()
    assert ad["AMISS"] == "Missing values for each auxiliary variable"


def test_getLocalAttributesConfigDict():

    lad = getLocalAttributesConfigDict()
    assert lad["na_attributes"]["ORG"] == \
        "Data held at British Atmospheric Data Centre (BADC), Rutherford Appleton Laboratory, UK."


