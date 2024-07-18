"""集成构建配置项"""
import argparse
import os, sys
from lbkit.log import Logger

log = Logger("build_config")


class Config(object):
    """集成构建的配置项"""
    def __init__(self, args = None):
        parser = self.arg_parser()
        args = parser.parse_args(args)

        # 配置项
        self.manifest = os.path.join(os.getcwd(), args.manifest)
        # 配置项目录
        self.work_dir = os.path.dirname(self.manifest)
        sys.path.append(self.work_dir)
        # 是否从源码构建
        self.from_source = args.from_source
        # 是否打印详细信息
        self.verbose = True if os.environ.get("VERBOSE", False) else False
        # 编译类型
        self.build_debug = args.debug
        # conan中心仓
        self.remote = args.remote
        self.not_check_download_sha = args.not_check_download_sha

        if not os.path.isfile(self.manifest):
            raise FileNotFoundError(f"File {args.manifest} not exist")

        # 编译主机配置项
        self.profile_build = args.profile_build
        # 编译目标配置项
        self.profile_host = args.profile

        # 设置并创建构建所需目录
        log.info("Work dir: %s", self.work_dir)
        self.temp_path = os.path.join(os.getcwd(), ".temp")
        self.output_path = os.path.join(self.temp_path, "output")
        self.tool_path = os.path.join(self.temp_path, "tools")
        self.download_path = os.path.join(self.temp_path, "download")
        self.rootfs_path = os.path.join(self.temp_path, "rootfs")
        self.conan_install = []
        self.mnt_path = os.path.join(self.temp_path, "mnt_path")
        self.rootfs_img = os.path.join(self.output_path, "rootfs.img")
        os.makedirs(self.temp_path, exist_ok=True)
        os.makedirs(self.tool_path, exist_ok=True)
        os.makedirs(self.output_path, exist_ok=True)
        os.makedirs(self.download_path, exist_ok=True)
        os.makedirs(self.rootfs_path, exist_ok=True)
        # 制作rootfs时需要strip镜像，所以需要单独指定stip路径
        self.strip = "strip"

    @staticmethod
    def arg_parser():
        """返回配置项支持的参数"""
        parser = argparse.ArgumentParser(description="Build LiteBMC")
        parser.add_argument("-m", "--manifest", help="Specify the manifest.yml ", default="./manifest.yml")
        parser.add_argument("-s", "--from_source", help="Build from source", action="store_true")
        parser.add_argument("-pr", "--profile", help="Apply the specified profile to the host machine", default="litebmc.ini")
        parser.add_argument("-pr:b", "--profile_build", help="Apply the specified profile to the build machine", default="default")
        parser.add_argument("-d", "--debug", help="Set the build type to debug", action="store_false")
        parser.add_argument("--not_check_download_sha", help="don't check sha256 of download file", action="store_true")
        parser.add_argument("-r", "--remote", help="specified conan server", default="litebmc")
        return parser
