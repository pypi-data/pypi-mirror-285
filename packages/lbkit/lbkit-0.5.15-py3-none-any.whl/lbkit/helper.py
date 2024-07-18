import os
import yaml
from xml.dom import minidom, Node

class Helper():
    @staticmethod
    def get_node_value(dom: Node, name, default=None):
        node: minidom.Attr = dom.attributes.get(name)
        if node is None:
            if default is None:
                raise Exception("Parse node failed, abort")
            return default
        return node.childNodes[0].nodeValue.strip()

    def read_yaml(file: str, key, default=None):
        if not os.path.isfile(file):
            return default
        fd = open(file, "r");
        try:
            data = yaml.load(fd, Loader=yaml.FullLoader)
            for split in key.split("/", -1):
                data = data.get(split)
                if data is None:
                    return default
            return data
        except:
            return default
