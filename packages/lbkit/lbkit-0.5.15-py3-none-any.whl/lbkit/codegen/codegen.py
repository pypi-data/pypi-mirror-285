"""
    DBus接口代码自动生成
"""
import os
import sys
import json
import yaml
import argparse
from lbkit.codegen.idf_interface import IdfInterface

from mako.lookup import TemplateLookup
from lbkit.log import Logger
from lbkit.helper import Helper
from lbkit.errors import ArgException
from lbkit.misc import SmartFormatter

lb_cwd = os.path.split(os.path.realpath(__file__))[0]
log = Logger("codegen")

__version__=2

class CodeGen(object):
    def __init__(self, args):
        self.args = args
        pass

    def _gen(self, idf_file, directory="."):
        directory = os.path.realpath(directory)
        os.makedirs(os.path.join(directory, "public"), exist_ok=True)
        os.makedirs(os.path.join(directory, "server"), exist_ok=True)
        os.makedirs(os.path.join(directory, "client"), exist_ok=True)
        lookup = TemplateLookup(directories=os.path.join(lb_cwd, "template"))
        interface = IdfInterface(lookup, idf_file)
        out_file = os.path.join(directory, "public", interface.name + ".xml")
        interface.render_dbus_xml("interface.introspect.xml.mako", out_file)
        for code_type in ["server", "client", "public"]:
            out_file = os.path.join(directory, code_type, interface.name + ".h")
            interface.render_c_source(code_type + ".h.mako", out_file)
            out_file = os.path.join(directory, code_type, interface.name + ".c")
            interface.render_c_source(code_type + ".c.mako", out_file)
        json_file = os.path.join(directory, "package.yml")
        data = {
            "version": interface.version,
            "name": interface.name
        }
        with open(json_file, "w", encoding="utf-8") as fp:
            yaml.dump(data, fp, encoding='utf-8', allow_unicode=True)

        # 生成接口schema文件
        odf_file = os.path.join(directory, "server", "schema", f"{interface.name}.json")
        os.makedirs(os.path.dirname(odf_file), exist_ok=True)
        odf_data = interface.odf_schema
        with open(odf_file, "w", encoding="utf-8") as fp:
            json.dump(odf_data, fp, sort_keys=False, indent=4)


    def run(self, package_yml=None):
        """
        代码自动生成.

        支持自动生成服务端和客户端C代码
        """
        if package_yml is not None and os.path.isfile(package_yml):
            configs = Helper.read_yaml(package_yml, "codegen", [])
            for cfg in configs:
                file = cfg.get("file")
                if file is None:
                    log.error("%s的自动代码生成配置不正确, 缺少file元素指定描述文件", package_yml)
                    sys.exit(-1)
                if not file.endswith(".yaml") :
                    log.error("%s的自动代码生成配置不正确, %s的文件名不是以.yaml结束", package_yml, file)
                    sys.exit(-1)
                if not os.path.isfile(file):
                    log.error("%s的自动代码生成配置不正确, %s不是一个文件", package_yml, file)
                    sys.exit(-1)
                outdir = cfg.get("outdir", os.getcwd())
                self._gen(file, outdir)
            return

        parser = argparse.ArgumentParser(description=self.run.__doc__,
                                         prog="lbkit gen",
                                         formatter_class=SmartFormatter)
        parser.add_argument("-i", "--input", help='A IDF file to be processed e.g.: com.litebmc.Upgrade.xml', required=True)
        parser.add_argument("-d", "--directory", help='generate code directory', default=".")

        args = parser.parse_args(self.args)
        intf_file = args.input
        out_dir = os.path.join(os.getcwd(), args.directory)
        if not intf_file.endswith(".yaml"):
            raise ArgException(f"The IDF file ({intf_file}) not endswith .yaml")
        if  not os.path.isfile(intf_file):
            raise ArgException(f"The IDF file ({intf_file}) not exist")
        if not os.path.isdir(out_dir):
            log.warning(f"Directory {args.directory} not exist, try create")
            os.makedirs(out_dir)
        self._gen(intf_file, out_dir)

if __name__ == "__main__":
    gen = CodeGen(None)
    gen._gen("com.litebmc.test.xml", ".")
