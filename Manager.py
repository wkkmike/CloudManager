import subprocess

class Manager:
    def __init__(self, etcd, config):
        self.etcd = etcd
        self.container_list = []
        self.config = config

    def __check_service(self):

    def __get_image_number(self):
        return len(self.__etcd_get_prefix("image_")) / 2

    def __etcd_get_prefix(self, prefix):
        return subprocess.run(args=["etcdctl", "--endpoints=" + self.etcd, "get",
                                    "--prefix", prefix],capture_output=True).\
            stdout.decode("utf-8").strip().split()

    def __etcd_get(self, key):
        return subprocess.run(args=["etcdctl", "--endpoints=" + self.etcd, "get", key],
                        capture_output=True).stdout.decode("utf-8").strip()

    def __get_container_list_from_etcd(self):
        return_value = subprocess.run(args=["etcdctl", "--endpoints=" + self.etcd, "get", "--prefix", "''"],
                        capture_output=True)
        container_list_pair = return_value.stdout.decode("utf-8").strip()

    def __image_exist(self, name):
        value = self.__etcd_get("image_" + name).split()
        if len(value) == 0:
            return False
        return True

    def __etcd_put(self, key, value):
        return_value = subprocess.run(args=["etcdctl", "--endpoints=" + self.etcd, "put", "image", ""], capture_output=True)
        if return_value.stdout.strip().decode("utf-8") == "OK":
            return True
        return False

    def get_all_container(self):

    #deprecated
    def create_new_service(self, name, position):
        if self.__image_exist():
            return False
        command = "  " + name + ":\n"
        command += "    image:" + position + "\n"
        command += "    labels:\"- traefik.frontend.rule=Host:whoami.docker.localhost\"\n"
        with open(self.config, "a") as file:
            file.write(command)
        subprocess.run(args=["etcdctl", "--endpoints=" + self.etcd, "put", "image", ""])
        return True;

    def create_service_from_yml(self, name, filename):
        if self.__image_exist(name):
            return False
        command = ""
        with open(filename, "r") as file:
            line = file.readline()
            while line:
                command += "  " + line
                line = file.readline()
            command += "    labels:\"- traefik.frontend.rule=Host:whoami.docker.localhost\"\n"
        if not self.__etcd_put("image_" + name, 0):
            return False

        with open(self.config, "a") as file:
            file.write(command)
        return True