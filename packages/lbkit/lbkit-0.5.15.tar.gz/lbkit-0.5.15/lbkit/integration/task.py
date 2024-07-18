"""任务基础类"""
import shutil
import importlib
import os
import hashlib
import requests
import yaml
from multiprocessing import Process
from lbkit.log import Logger
from lbkit.tools import Tools
from lbkit.misc import load_yml_with_json_schema_validate

from lbkit.integration.config import Config

class ManifestValidateError(OSError):
    """Raised when validation manifest.yml failed."""

class Task(Process):
    """任务基础类，提供run和install默认实现以及其它基础该当"""
    def __init__(self, config: Config, name: str):
        super().__init__()
        self.log: Logger = Logger("task")
        self.tools: Tools = Tools(name)
        self.config: Config = config

    def install(self):
        """安装任务"""
        self.log.info("install...........")

    def exec(self, cmd: str, verbose=False, ignore_error = False, sensitive=False, log_prefix=""):
        return self.tools.exec(cmd, verbose, ignore_error, sensitive, log_prefix)

    def pipe(self, cmds: list[str], ignore_error=False, out_file = None):
        self.tools.pipe(cmds, ignore_error, out_file)

    def run(self, cmd, ignore_error=False):
        return self.tools.run(cmd, ignore_error)

    def do_hook(self, path):
        """执行任务钓子，用于定制化"""
        try:
            module = importlib.import_module(path)
        except TypeError:
            self.log.info("Load module(%s) failed, skip", path)
            return
        self.log.info(module)
        hook = module.TaskHook(self.config, "do_hook")
        hook.run()

    def get_manifest_config(self, key: str):
        """从manifest中读取配置"""
        with open(self.config.manifest, "r", encoding="utf-8") as fp:
            manifest = yaml.load(fp, yaml.FullLoader)
        keys = key.split("/")
        for k in keys:
            manifest = manifest.get(k, None)
            if manifest is None:
                return None
        return manifest

    def load_manifest(self):
        """加载manifest.yml并验证schema文件"""
        return load_yml_with_json_schema_validate(self.config.manifest, "/usr/share/litebmc/schema/pdf.v1.json")
