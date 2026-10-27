"""Process 07: structural XML/JSON interchange.

ElementTree representation preserves child/tail ordering, attributes and expanded
namespace names, but NOT comments, processing instructions, original prefixes,
DOCTYPE or byte-for-byte serialization. Those need a richer parser if required.
"""
import xml.etree.ElementTree as ET
import json

def _encode(element):
    return {"tag": element.tag, "attributes": dict(element.attrib),
            "text": element.text, "tail": element.tail,
            "children": [_encode(child) for child in element]}

def _decode(node):
    element = ET.Element(node["tag"], node.get("attributes", {}))
    element.text, element.tail = node.get("text"), node.get("tail")
    for child in node.get("children", []):
        element.append(_decode(child))
    return element

def xml_to_json(xml):
    return json.dumps(_encode(ET.fromstring(xml)), ensure_ascii=False, indent=2)

def json_to_xml(payload):
    return ET.tostring(_decode(json.loads(payload)), encoding="unicode")
