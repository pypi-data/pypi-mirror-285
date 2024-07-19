"""环境准备"""
import os
import tempfile
import tarfile
import shutil
from lbkit.integration.config import Config
from lbkit.integration.task import Task
from lbkit.log import Logger
from lbkit import errors

log = Logger("build_image")

src_cwd = os.path.split(os.path.realpath(__file__))[0]

class BuildImage(Task):
    def download_uboot(self, img_file):
        tar_file = os.path.join(self.config.download_path, "uboot.tar.gz")

        url = self.get_manifest_config("components/uboot/url")
        sha256 = None
        if not self.config.not_check_download_sha:
            sha256 = self.get_manifest_config("components/uboot/sha256")
        self.tools.download(url, tar_file, sha256)
        tar = tarfile.open(tar_file)
        members = tar.getmembers()
        for member in members:
            if not member.isfile():
                continue
            if member.name != "uboot.bin" and member.name != "u-boot.bin":
                continue
            io = tar.extractfile(member)
            fp = open(img_file, "wb+")
            while True:
                buf = io.read(65536)
                if len(buf) == 0:
                    break
                fp.write(buf)
            fp.close()
            return
        raise errors.ExtractRootfsTarFileError("Extract failed, the u-boot.bin can't be found in " + url)

    def download_kernel(self, img_file):
        tar_file = os.path.join(self.config.download_path, "kernel.tar.gz")

        url = self.get_manifest_config("components/kernel/url")
        sha256 = None
        if not self.config.not_check_download_sha:
            sha256 = self.get_manifest_config("components/kernel/sha256")
        self.tools.download(url, tar_file, sha256)
        tar = tarfile.open(tar_file)
        members = tar.getmembers()
        for member in members:
            if not member.isfile():
                continue
            if member.name != "Image":
                continue
            io = tar.extractfile(member)
            fp = open(img_file, "wb+")
            while True:
                buf = io.read(65536)
                if len(buf) == 0:
                    break
                fp.write(buf)
            fp.close()
            return
        raise errors.ExtractRootfsTarFileError("Extract failed, the Image can't be found in " + url)

    def run(self):
        """任务入口"""
        """检查manifest文件是否满足schema格式描述"""
        os.chdir(self.config.output_path)
        self.download_uboot("u-boot.bin")
        self.download_kernel("Image")
        cmd = "qemu-system-aarch64 -M virt -cpu cortex-a57 -M virt,dumpdtb=virt.dtb"
        self.exec(cmd)

        cmd = 'lbpack_emmc.sh ./Image ./virt.dtb ./rootfs.img ./qemu.img'
        self.exec(cmd)
        cmd = 'cp /usr/share/litebmc/qemu.conf ./qemu.conf'
        self.exec(cmd)
        output_img = os.path.join(self.config.output_path, "litebmc_qemu.tar.gz")
        cmd = f'tar -czf {output_img} -C . qemu.img u-boot.bin qemu.conf'
        self.exec(cmd)
        log.success(f"Create litebmc image {output_img} successfully")

if __name__ == "__main__":
    config = Config()
    build = BuildImage(config)
    build.run()