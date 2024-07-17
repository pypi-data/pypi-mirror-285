#!/usr/bin/env python3
"""
Utilities relating to eaf transcription files.
"""
from lxml import etree
from pathlib import Path
import base58, uuid, hashlib




def eaf_iterator(tx_dir="mmep-corpus/transcribed-audio", start=None, end=None):
    """
    Returns an iterator of transcription file paths.

    kwargs:
    - `tx_dir`: root directory of trannscriptions
    - `start`: from yyyymm
    - `end`: to (incl) yyyymm
    """
    txs = Path(tx_dir)
    for tx in sorted(txs.glob("**/*.eaf")):
        assert (start==None) == (end==None), "Provide both start and end year or neither"
        if start is not None and end is not None:
            txyyyymm = str(tx).split('_')[-3][:6]
            if start <= int(txyyyymm) <= end:
                yield str(tx.relative_to("."))
        else:
            yield str(tx.relative_to("."))




def get_decoration(eaf):
    """
    Takes the last two pieces of information exclusive to the .eaf from the
    Header and Property.
    With this all information can now be extracted from the .eaf.
    """
    return [eaf.attrib['DATE'], eaf.find("HEADER").find('PROPERTY').text]




def get_media_descriptors(eaf):
    """
    Take an eaf tree object and return <MEDIA_DESCRIPTOR> elements.
    """
    return eaf.find("HEADER").findall("MEDIA_DESCRIPTOR")




def get_tiers(eaf, tx_only=False, language=None):
    """
    Return Tier elems from eaf tree.

    kwargs:
    - `tx_only`: return only transcription tiers
    - `language`: return tier of language (not implemented)
    """
    if tx_only:
        return eaf.findall("TIER[@LINGUISTIC_TYPE_REF='default-lt']")
    else:
        return eaf.findall("TIER")




def get_time_slots(eaf):
    """
    Return time_slot elems from eaf tree.

    Input: lxml.etree._Element from get.root(); as delivered by parse_eaf() in this module
    Output: [lxml.etree._Element], Elements with tag TIME_SLOT
    """
    return eaf.findall('TIME_ORDER/TIME_SLOT')




def make_tier_dictionary(tierlist):
    """
    Takes a list of tiers and returns a dictionary containing their IDs as keys and
    the original tier as value.
    This is very helpful for editing multiple, but not all tiers.

    Input: [lxml.etree._Element] with tag TIER and attributes 'TIER_ID'
    OUTPUT:  {'ID': value}
        Keys are strings
        Values are lxml.etree._Element
    """
    return {tier.attrib['TIER_ID']: tier for tier in tierlist}




def make_time_slot_dictionary(time_slot_list):
    """
    Takes a list of time slots and returns a dictionary containing their IDs as keys and
    time values in milliseconds as values.

    Input: [lxml.etree._Element] with tag TIME_SLOT and attributes 'TIME_SLOT_ID' and
    'TIME_VALUE'; as delivered by get_time_slots() in this module
    Output: {'ID': Value}
        Keys are strings
        Values are ints
    """
    return {time_slot.attrib['TIME_SLOT_ID']: int(time_slot.attrib['TIME_VALUE']) for time_slot in time_slot_list}




def parse_eaf(eaf_path):
    """
    Returns eaf etree object from the eaf_path.
    """
    parser = etree.XMLParser(remove_blank_text=True)
    return etree.parse(eaf_path, parser).getroot()




def extract_eaf(path):
    """
    Takes the path of an eaf and extracts all information using this module's functions.

    First calls parse_eaf() on the path to receive the tree.
    From the tree it extracts and returns 
    the {time slot information}, the {tier information}, the [date, first property text].

    Input: path to eaf
    Output: (path, {dictionary of time slots}, {dictionary of tiers}, 
             [list of date, first property text information])
    """
    tree = parse_eaf(path)
    return (path, 
            make_time_slot_dictionary(get_time_slots(tree)), 
            make_tier_dictionary(get_tiers(tree)), 
            get_decoration(tree))




def write_eaf(eaf, eaf_path):
    """
    Writes eaf tree (`eaf`) to file (`eaf_path`).
    """
    b = etree.tostring(
        eaf, pretty_print=True, encoding="utf-8", xml_declaration=True
    )
    f = open(eaf_path, "wb")
    f.write(b)




#def xml_formatted_uuid(seed=None):
#    """
#    Generate a UUID and return it prepended with "i-" and formatted as a string
#    so it can be used as an annotation ID (valid xml)
#    """
#    if seed is None:
#        x = uuid.uuid4()
#    else:
#        m = hashlib.md5()
#        m.update(seed.encode('utf-8'))
#        x = uuid.UUID(m.hexdigest())
#    return f"i-{str(base58.b58encode(x.bytes), 'UTF8')}"
