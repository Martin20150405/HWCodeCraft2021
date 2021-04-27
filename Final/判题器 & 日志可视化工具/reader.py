class HostInfo:
    def __init__(self, cpu, mem, hardware_cost, energy_cost):
        self.cpu = cpu
        self.mem = mem
        self.hardware_cost = hardware_cost
        self.energy_cost = energy_cost


class VmInfo:
    def __init__(self, cpu, mem, is_two_node):
        self.cpu = cpu
        self.mem = mem
        self.is_two_node = is_two_node

def parse_host_vm_info(input_lines):
    num_hosts = int(input_lines[0])
    host_infos = {}
    vm_infos = {}
    for i in range(num_hosts):
        values = input_lines[i + 1].strip()[1:-1].split(',')
        host_infos[values[0]] = HostInfo(int(values[1]), int(values[2]),
                                         int(values[3]), int(values[4]))
    num_vms = int(input_lines[num_hosts + 1])
    for i in range(num_vms):
        values = input_lines[num_hosts + 2 + i].strip()[1:-1].split(',')
        vm_infos[values[0]] = VmInfo(int(values[1]), int(values[2]),
                                     int(values[3]))
    return num_hosts,host_infos,num_vms,vm_infos

def get_requests_data(input_lines):
    values = input_lines[0].strip().split()
    num_days = int(values[0])
    requests = []
    index = 1
    for i in range(num_days):
        requests.append([])
        num_requests = int(input_lines[index])
        index += 1
        for j in range(num_requests):
            requests[-1].append(input_lines[index])
            index += 1
    return requests