import subprocess
import csv
def GetPiIP(path):
    """
    获取树莓派IP，传入binding.csv路径
    """
    # 读取binding.csv
    with open(path,'r')as f:
        data = csv.reader(f)
        binding = []
        for i in data:
            binding.append(i)

    # 获取本地IP
    p = subprocess.Popen("hostname -I", shell=True, stdout=subprocess.PIPE)
    nodeIP = p.stdout.read()
    nodeIP = str(nodeIP,encoding = 'UTF-8').strip(' \n')

    # 树莓派名称
    parentID = 0
    for ele in binding:
        if ele[1] == nodeIP:
            parentID = ele[3]
            break

    # 树莓派IP
    parentIP = ""
    for ele in binding:
        if ele[0] == parentID:
            parentIP = ele[1]
            break
    return parentIP

if __name__ == '__main__':
    # 修改下path
    path = "/home/pi/yanhu/DASP/system/binding.csv"
    PiIP = GetPiIP(path)
