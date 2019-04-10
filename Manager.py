import subprocess
from threading import Timer

class Manager:
    def __init__(self, etcd, config):
        self.etcd = etcd
        self.container_list = []
        self.config = config
        self.timer = Timer(60, self.__auto_loader()).start()
        self.cpu_max = 80.0
        self.cpu_min = 20.0
        self.mem_max = 80.0
        self.mem_min = 20.0

    def __auto_loader(self):
        image_list = self.__get_images_name()
        for image in image_list:
            if len(image) == 0:
                return
            amount, cpu, mem = self.__check_health_of_service(image)
            if cpu > self.cpu_max or mem > self.mem_max:
                if amount < self.__get_upper(image):
                    self.run_service(image, amount + 1)
            if cpu < self.cpu_min and mem < self.mem_min and amount > self.__get_lower(image):
                self.run_service(image, amount - 1)

    def __check_service(self):
        return False

    def __get_upper(self, name):
        return self.__etcd_get("upper_" + name)

    def __get_lower(self, name):
        return self.__etcd_get("lower_" + name)

    def __get_image_number(self):
        return len(self.__etcd_get_prefix("image_")) / 2

    def __get_images_name(self):
        list = self.__etcd_get_prefix("image_")
        i=0
        image_list = []
        for item in list:
            if i%2 == 0:
                image_list.append(item[6:])
            i += 1
        return image_list
    def __etcd_get_prefix(self, prefix):
        return subprocess.run(args=["etcdctl", "--endpoints=" + self.etcd, "get",
                                    "--prefix", prefix],capture_output=True).\
            stdout.decode("utf-8").strip().split("\n")

    def __etcd_get(self, key):
        return subprocess.run(args=["etcdctl", "--endpoints=" + self.etcd, "get", key],
                              capture_output=True).stdout.decode("utf-8").strip()

    def __etcd_del(self, key):
        subprocess.run(args=["etcdctl", "del", key])

    def __etcd_del_prefix(self, prefix):
        subprocess.run(args=["etcdctl", "del", "--prefix", prefix])

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
        return_value = subprocess.run(args=["etcdctl", "--endpoints=" + self.etcd, "put", key, value], capture_output=True)
        if return_value.stdout.strip().decode("utf-8") == "OK":
            return True
        return False

    def get_all_container(self):
        return False

    #deprecated
    """
    def create_new_service(self, name, position):
        if self.__image_exist():
            return False
        command = "  " + name + ":\n"
        command += "    image:" + position + "\n"
        command += "    labels: - \"traefik.frontend.rule=Host:whoami.docker.localhost\"\n"
        with open(self.config, "a") as file:
            file.write(command)
        subprocess.run(args=["etcdctl", "--endpoints=" + self.etcd, "put", "image", ""])
        return True;
    """

    def create_service_from_yml(self, name, filename, upper, lower):
        if self.__image_exist(name):
            return False
        command = ""
        try:
            with open(filename, "r") as file:
                line = file.readline()
                while line:
                    command += "  " + line
                    line = file.readline()
                command += "    labels: \n      - \"traefik.frontend.rule=Host:" + name + ".docker.localhost\"\n"
            if not self.__etcd_put("image_" + name, "0"):
                return False
            with open(self.config, "a") as file:
                file.write(command)
        except:
            print("Don't have the config file")
            return False
        self.__etcd_put("upper_" + name, str(upper))
        self.__etcd_put("lower_" + name, str(lower))
        return True

    def list_all_service(self):
        list = self.__etcd_get_prefix("image_")
        answer = "{:30s}{:30s}".format("Service Name", "Number of instances") + "\n"
        i=0
        for item in list:
            if i%2 == 0:
                answer += "{:30s}".format(item[6:])
            else:
               answer += "{:30s}".format(item) + "\n"
            i += 1
        return answer

    def get_containerid_for_service(self, name):
        list = self.__etcd_get_prefix("container_" + name + "_")
        containerid = []
        i=0
        for item in list:
            if i%2 == 1:
                containerid.append(item)
            i+=1
        return containerid

    def run_service(self, name, amount):
        subprocess.run(["docker-compose","up", "--scale", name+"="+amount, "-d"], capture_output=True)
        self.__etcd_put("image_" + name, amount)
        name_filter = "name=" + name
        id_list = subprocess.run(["docker", "ps", "-qf", name_filter], capture_output=True)\
            .stdout.strip().decode("utf-8").split("\n")
        self.__etcd_del_prefix("container_" + name)
        i=1
        for id in id_list:
            self.__etcd_put("container_" + name + "_" + str(i), id)
            i += 1
        output = subprocess.run(["docker", "ps", "-f", name_filter], capture_output=True)
        return output.stdout.decode("utf-8")

    def check_health_of_service(self, name):
        amount, cpu, mem = self.__check_health_of_service(name)
        answer = "{:30s}{:30s}{:30s}{:30s}".format("Service Name", "Number of instances"
                                                   , "CPU Useage", "MEM Useage") + "\n"
        answer += "{:30s}{:30s}{:30s}{:30s}".format(name, str(amount), str(cpu) + "%", str(mem) + "%")
        return answer

    def __check_health_of_service(self, name):
        if not self.__image_exist(name):
            print("No such service")
            return False
        containerid = self.get_containerid_for_service(name)
        cpu = 0.0
        mem = 0.0
        amount = 0
        output = subprocess.run(["docker", "stats", "--no-stream"], capture_output=True)
        output = output.stdout.strip().decode("utf-8").split("\n")[1:]
        for line in output:
            info = line.split()
            if info[0] in containerid:
                cpu += float(info[2][:-1])
                mem += float(info[6][:-1])
                amount += 1
        return amount, cpu, mem
