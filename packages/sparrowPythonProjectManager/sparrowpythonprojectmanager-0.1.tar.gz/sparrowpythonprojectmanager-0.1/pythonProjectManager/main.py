import importlib.metadata
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pythonProjectManager import MANAGER_XML_CONTENT


class PythonProjectManager:
    def __init__(self, pypi: str = "", save_path: str = ""):
        # 判断manager文件是否存在，存在则下一步，不存在则创建文件并初始化值
        if not os.path.exists("manager.xml"):
            with open("manager.xml", 'w', encoding="utf-8") as f:
                f.write(MANAGER_XML_CONTENT)
                sys.exit()
        else:
            self._pypi_ = []
            self._save_path_ = None
            self._packages_ = []
            self._cmd_ = {}
            self._saved_packages_ = {}
            self._downloaded_packages_ = []
            if pypi != "" and save_path != "":
                self._pypi_.append(pypi)
                self._save_path_ = save_path
            else:
                tree = ET.parse("manager.xml")
                root = tree.getroot()
                if pypi == "" and save_path == "":
                    for pipy_url in root.iter("pypiUrl"):
                        self._pypi_.append(pipy_url.text)
                    for save_path in root.iter("savePath"):
                        self._save_path_ = save_path.text
                        if not os.path.exists(self._save_path_):
                            os.makedirs(self._save_path_)
                else:
                    if save_path == "":
                        for save_path in root.iter("savePath"):
                            self._save_path_ = save_path.text
                        self._pypi_.append(pypi)
                    elif pypi == "":
                        for pipy_url in root.iter("pypiUrl"):
                            self._pypi_.append(pipy_url.text)
                        self._save_path_ = save_path
            self._get_downloaded_packages_()
            self._list_installed_packages_()
            self._get_manager_packages_()
            self._assemble_cmd_()
            for package, cmd in self._cmd_.items():
                self._install_package_(package, cmd)
            self._get_package_dependencies_()

    def _get_downloaded_packages_(self):
        packages = os.listdir(self._save_path_)
        for package in packages:
            self._downloaded_packages_.append(package.split("-")[0] + "==" + package.split("-")[1])

    def _list_installed_packages_(self):
        """列出当前Python环境中已安装的所有包名"""
        packages = {dist.metadata['Name'] for dist in importlib.metadata.distributions()}
        for package in sorted(packages):
            version = importlib.metadata.distribution(package).version
            self._saved_packages_[package] = version

    def _get_manager_packages_(self):
        tree = ET.parse(r'manager.xml')
        root = tree.getroot().find("packages")
        for r in root.findall("package"):
            name = r.find("name").text
            version = r.find("version").text
            if name is not None:
                if version == "latest" or version is None:
                    if name not in self._packages_:
                        self._packages_.append(f"{name}")
                else:
                    if f"{name}=={version}" not in self._packages_:
                        self._packages_.append(f"{name}=={version}")

    def _assemble_cmd_(self):
        for package in self._packages_:
            if "==" in package:
                package_name = package.split("==")[0]
                if package_name in self._saved_packages_:
                    if package.split('==')[1] != self._saved_packages_.get(package_name):
                        for pypi in self._pypi_:
                            download_cmd = f"pip download -i {pypi} {package} -d {self._save_path_}"
                            install_cmd = f"pip install --no-index --find-links={self._save_path_} {package}"
                            uninstall_cmd = f"pip uninstall -y {package}"
                            if package in self._cmd_:
                                self._cmd_[package].append(
                                    {"download": download_cmd, "install": install_cmd, "uninstall": uninstall_cmd})
                            else:
                                self._cmd_[package] = [
                                    {"download": download_cmd, "install": install_cmd, "uninstall": uninstall_cmd}]
                else:
                    for pypi in self._pypi_:
                        download_cmd = f"pip download -i {pypi} {package} -d {self._save_path_}"
                        install_cmd = f"pip install --no-index --find-links={self._save_path_} {package}"
                        uninstall_cmd = ""
                        if package in self._cmd_:
                            self._cmd_[package].append(
                                {"download": download_cmd, "install": install_cmd, "uninstall": uninstall_cmd})
                        else:
                            self._cmd_[package] = [
                                {"download": download_cmd, "install": install_cmd, "uninstall": uninstall_cmd}]
            else:
                package_name = package
                if package_name in self._saved_packages_:
                    for pypi in self._pypi_:
                        download_cmd = f"pip download -i {pypi} {package} -d {self._save_path_}"
                        install_cmd = f"pip install --no-index --find-links={self._save_path_} {package}"
                        uninstall_cmd = f"pip uninstall -y {package}"
                        if package in self._cmd_:
                            self._cmd_[package].append(
                                {"download": download_cmd, "install": install_cmd, "uninstall": uninstall_cmd})
                        else:
                            self._cmd_[package] = [
                                {"download": download_cmd, "install": install_cmd, "uninstall": uninstall_cmd}]
                else:
                    for pypi in self._pypi_:
                        download_cmd = f"pip download -i {pypi} {package} -d {self._save_path_}"
                        install_cmd = f"pip install --no-index --find-links={self._save_path_} {package}"
                        uninstall_cmd = f""
                        if package in self._cmd_:
                            self._cmd_[package].append(
                                {"download": download_cmd, "install": install_cmd, "uninstall": uninstall_cmd})
                        else:
                            self._cmd_[package] = [
                                {"download": download_cmd, "install": install_cmd, "uninstall": uninstall_cmd}]

    def _install_package_(self, package, cmds):
        """
        在当前Python环境中安装指定的包。
        :param cmds: 操作命令
        :param package: 要安装的包名
        """
        for cmd in cmds:
            try:
                if cmd.get("uninstall") == "":
                    if package not in self._downloaded_packages_:
                        print(f"download {package}")
                        subprocess.check_call(cmd.get("download"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print(f"install {package}")
                    subprocess.check_call(cmd.get("install"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    print(f"uninstall {package}")
                    subprocess.check_call(cmd.get("uninstall"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    if package not in self._downloaded_packages_:
                        print(f"download {package}")
                        subprocess.check_call(cmd.get("download"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print(f"install {package}")
                    subprocess.check_call(cmd.get("install"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                break
            except subprocess.CalledProcessError as e:
                print(f"An error occurred while installing package '{package}': {e}")

    def _get_package_dependencies_(self):
        need_package = ["pip", "pythonprojectmanager"]
        for k in self._packages_:
            try:
                if '==' in k:
                    package_name = k.split("==")[0]
                else:
                    package_name = k
                need_package.append(package_name.lower())
                distribution = importlib.metadata.distribution(package_name).requires
                for d in distribution:
                    need_package.append(d.split(' ')[0])
            except Exception as e:
                print(f"Package '' not found")
            finally:
                continue
        for i in self._saved_packages_.keys():
            if i.lower() not in need_package:
                try:
                    subprocess.check_call(f"pip uninstall -y {i}", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception as e:
                    print(e)
