"""应用构建任务"""
import os
import shutil
import json
from mako.lookup import TemplateLookup
from lbkit.integration.config import Config
from lbkit.integration.task import Task
from lbkit.log import Logger

log = Logger("product_build")


class ManifestValidateError(OSError):
    """Raised when validation manifest.yml failed."""

src_cwd = os.path.split(os.path.realpath(__file__))[0]

class BuildManifest(Task):
    """根据产品配置构建所有app,记录待安装应用路径到self.config.conan_install路径"""
    def __init__(self, cfg: Config, name: str):
        super().__init__(cfg, name)
        self.conan_build = os.path.join(self.config.temp_path, "conan")
        if os.path.isdir(self.conan_build):
            shutil.rmtree(self.conan_build)
        os.makedirs(self.conan_build)
        if self.config.build_debug:
            self.conan_settings = " -s build_type=Debug"
        else:
            self.conan_settings = " -s build_type=Release"
        self.common_args = "-r " + self.config.remote
        self.common_args += " -pr:b {} -pr:h {}".format(self.config.profile_build, self.config.profile_host)
        self.common_args += " -o */*:test=False"

    def deploy(self):
        cmd = f"conan graph info . {self.common_args} --build=missing -f json --filter=ref --filter=package_id"
        cmd += f" --filter=context"
        res = self.tools.run(cmd).stdout.strip()
        graph = json.loads(res)
        nodes = graph.get("graph", {}).get("nodes", {})
        for id, info in nodes.items():
            ref = info.get("ref")
            id = info.get("package_id")
            context = info.get("context")
            if context != "host":
                continue
            cmd = f"conan cache path {ref}:{id}"
            package_folder = self.tools.run(cmd).stdout.strip()
            self.config.conan_install.append(package_folder)

    def build_litebmc(self):
        """构建产品conan包"""
        log.info("build litebmc")

        manifest = self.load_manifest()
        hook_name = "hook.prepare_manifest"
        self.do_hook(hook_name)
        # 使用模板生成litebmc组件的配置
        lookup = TemplateLookup(directories=os.path.join(src_cwd, "template"))
        template = lookup.get_template("conanfile.py.mako")
        conanfile = template.render(lookup=lookup, pkg=manifest)

        recipe = os.path.join(self.conan_build, "litebmc")
        os.makedirs(recipe, exist_ok=True)
        os.chdir(recipe)
        fp = open("conanfile.py", "w", encoding="utf-8")
        fp.write(conanfile)
        fp.close()

        # 安装所有应用
        if self.config.from_source:
            cmd = "conan install . --build=\"*\" " + self.common_args
        else:
            cmd = "conan install . --build=missing " + self.common_args
        cmd = cmd + self.conan_settings
        self.exec(cmd, verbose=True)

        cmd = "conan create . {} -tf=".format(self.common_args)
        cmd = cmd + self.conan_settings
        self.exec(cmd, verbose=True)
        # 部署应用到self.config.conan_install
        self.deploy()

    def run(self):
        """任务入口"""
        self.build_litebmc()

if __name__ == "__main__":
    config = Config()
    build = BuildManifest(config)
    build.run()
