"""完成rootfs镜像打包."""
import os
import shutil
import tarfile
from lbkit.integration.config import Config
from lbkit.integration.task import Task
from lbkit.log import Logger
from lbkit import errors

log = Logger("build_rootfs")

src_cwd = os.path.split(os.path.realpath(__file__))[0]
IMG_FILE = "rootfs.img"

class BuildRootfs(Task):
    """构建rootfs镜像"""
    def do_permission(self, per_file: str):
        """完成组件制品赋权"""
        if not os.path.isfile(per_file):
            return
        log.info("Do permission, file: %s", per_file)
        with open(per_file, "r", encoding="utf-8") as fp:
            for line in fp:
                line = line.strip()
                if line.startswith("#") or len(line) == 0:
                    continue
                log.debug("Permission line: %s", line)
                chunk = line.split()
                if len(chunk) < 5:
                    raise errors.PermissionFormatError(f"Permission format with error, line: {line}")
                if not chunk[0].startswith("/"):
                    raise errors.PermissionFormatError(f"Permission file error, must begin with \"/\", get: {chunk[0]}")
                if not chunk[3].isnumeric() or not chunk[4].isnumeric():
                    raise errors.PermissionFormatError(f"Permission uid or gid error, must is numeric, uid({chunk[3]}), gid({chunk[4]})")
                chunk[0] = chunk[0].lstrip("/")
                if chunk[1] != "f" and chunk[1] != "d" and chunk[1] != "s" and chunk[1] != "r":
                    raise errors.PermissionFormatError(f"Permission type error, only support 'f' 's' 'd' 'r', get({chunk[1]}), ignore")
                if chunk[1] == "d" and not os.path.isdir(chunk[0]):
                    log.error("Permission error, %s is not directory", chunk[0])
                if chunk[1] == "s" and not os.path.islink(chunk[0]):
                    log.error("Permission error, %s is not directory", chunk[0])
                uid = int(chunk[3])
                gid = int(chunk[4])
                pri = chunk[2]
                if (chunk[1] == "f" and os.path.isdir(chunk[0])) or chunk[1] == "r":
                    for subf in os.listdir(chunk[0]):
                        file_path = os.path.join(chunk[0], subf)
                        if not os.path.isfile(file_path):
                            continue
                        log.debug("chmod %s", file_path)
                        cmd = f"chmod {pri} {file_path}"
                        self.exec(cmd)
                        cmd = f"chown {uid}:{gid} {file_path}"
                        self.exec(cmd)
                else:
                    cmd = f"chmod {pri} {chunk[0]}"
                    self.exec(cmd)
                    cmd = f"chown {uid}:{gid} {chunk[0]}"
                    self.exec(cmd)

    def download_rootfs(self, rootfs_img):
        """下载rootfs基础镜像"""
        os.chdir(self.config.download_path)
        rootfs_tar = "rootfs.tar.gz"

        url = self.get_manifest_config("components/rootfs/url")
        sha256 = None
        if not self.config.not_check_download_sha:
            sha256 = self.get_manifest_config("components/rootfs/sha256")
        self.tools.download(url, rootfs_tar, sha256)
        tar = tarfile.open(rootfs_tar)
        members = tar.getmembers()
        for member in members:
            if not member.isfile():
                continue
            if member.name != "rootfs.img" and member.name != "rootfs.ext4" and member.name != "rootfs.ext2":
                continue
            io = tar.extractfile(member)
            fp = open(rootfs_img, "wb+")
            while True:
                buf = io.read(65536)
                if len(buf) == 0:
                    break
                fp.write(buf)
            fp.close()
            return
        raise errors.ExtractRootfsTarFileError("Extract failed, the rootfs.img can't be found in rootfs.tar")

    def merge_rootfs(self, rootfs_img):
        """将产品依赖的所有组件安装到rootfs镜像中"""
        mnt_path = self.config.mnt_path
        self.exec("umount " + mnt_path, ignore_error=True)
        shutil.rmtree(mnt_path, ignore_errors=True)
        os.makedirs(mnt_path)
        # 按manifest配置的大小调整rootfs
        rootfs_size = self.get_manifest_config("metadata/rootfs_size")
        self.exec(f"resize2fs {rootfs_img} {rootfs_size}")
        # 挂载rootfs镜像
        self.exec(f"fuse2fs {rootfs_img} {mnt_path} -o fakeroot")
        # 切换到rootfs挂载目录
        os.chdir(mnt_path)
        log.info("Copy customization rootfs......")
        for src_dir in self.config.conan_install:
            log.info("copy %s to %s", src_dir, mnt_path)
            cmd = f"rsync -aHK {src_dir}/ {mnt_path}"
            self.exec(cmd)
            per_file = os.path.join(src_dir, "permissions")
            self.do_permission(per_file)

        # copy product self-owned rootfs
        product_rootfs = os.path.join(self.config.work_dir, "rootfs")
        if os.path.isdir(product_rootfs):
            cmd = f"rsync -aKH {product_rootfs}/ {mnt_path}"
            self.exec(cmd)
            per_file = os.path.join(product_rootfs, "permissions")
            self.do_permission(per_file)

        # 执行rootfs定制化脚本
        os.chdir(self.config.work_dir)
        hook_name = "hook.post_rootfs"
        self.do_hook(hook_name)

        # 清理冗余文件
        inc_dir = os.path.join(self.config.mnt_path, "include")
        if os.path.isdir(inc_dir):
            cmd = "rm -rf " + inc_dir
            self.exec(cmd)
        cmd = "rm " + os.path.join(self.config.mnt_path, "permissions")
        self.exec(cmd)

        # 清理冗余静态文件
        cmds = ["find " + self.config.mnt_path + " -name *.a -type f", "xargs -i{} rm {} -f"]
        self.pipe(cmds)

        # 按manifest配置的大小调整rootfs
        strip = self.get_manifest_config("metadata/strip")
        if strip:
            log.info("Start strip files")
            file_list = os.path.join(self.config.temp_path, "strip.filelist")
            unstrip_regex = [
                "*.yaml$",
                "*.mo$",
                "*.target$",
                "*.service$",
                "*.md$",
                "*.html$",
                "*usr/share/",
                "*.py$",
                "*.pc$",
                "*.mc$",
                "*.in$",
                "*.ini$",
                "*.rules$",
                "*.conf$"]
            cmds = ["find " + self.config.mnt_path + " -type f"]
            for unstrip in unstrip_regex:
                cmds.append(f"grep -vE {unstrip}")
            self.pipe(cmds, out_file=file_list)

            cmds = [f"cat {file_list}", "xargs file", "grep 'not stripped'", "awk -F':' '{{print $1}}'"]
            cmds.append(f"xargs -i{{}} {self.config.strip} -s {{}}")
            self.pipe(cmds)

        log.info("remove static libraries")
        cmds = [f"find {self.config.mnt_path} -name *.a", "xargs -i{} rm {}"]
        self.pipe(cmds)
        log.info("remove all .fuse_hiddeng* files")
        cmds = [f"find {self.config.mnt_path} -name .fuse_hidden*", "xargs -i{} rm {}"]
        self.pipe(cmds)
        self.exec("umount " + mnt_path)

    def run(self):
        rootfs_img = os.path.join(self.config.download_path, IMG_FILE)
        if os.path.isfile(rootfs_img):
            os.unlink(rootfs_img)
        # 任务入口
        self.download_rootfs(rootfs_img)
        self.merge_rootfs(rootfs_img)
        os.rename(rootfs_img, self.config.rootfs_img)
        log.success(f"Create image {self.config.rootfs_img} successfully")

if __name__ == "__main__":
    config = Config()
    build = BuildRootfs(config)
    build.run()