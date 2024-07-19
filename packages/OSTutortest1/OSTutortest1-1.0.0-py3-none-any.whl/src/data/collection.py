from .storage import Storage
from dataclasses import dataclass
from tqdm import tqdm 
from src.dao import InstDao
from src.dao.entity import Inst
import os
import subprocess
from typing import List
from colorama import Fore, Style

@dataclass
class Collection:
    manPath: str   = 'src/assets/man'
    files:   tuple = ()
    types:   tuple = ('user', 'admin')  
    def collect(self):
        """
        收集本地数据，将知识库中存在于本地的指令存在标识置 1 。
        若本地指令在知识库中不存在，尝试在本地查找man文档并解析
        """
        rpms = self.collectRpm()
        insts = [self.collectInst(rpm) for rpm in tqdm(rpms, desc="Collecting INSTRUCTIONs")]
        insDao = InstDao()
        instcnt = 0 # 本地指令数
        notexistinfo = 0 # 无法找到信息的指令数
        insts = tqdm(insts, desc='Processing')
        for index, ins in enumerate(insts):
            
            rpmName = self.collectRpmInfo(rpms[index])[0]
            
            for type in self.types: # 分别收录两种不同命令
                storage = Storage(rpm=rpmName, exist=1, type=type)
                instcnt += len(ins[type]) 
                for i in ins[type]:
                    info = insDao.SelectByNameAndType(i, type) # 根据指令名查找信息
                    if info is not None: # 若指令在知识库中存在
                        # 更新指令存在标识,并填入对应rpm包
                        info.exist = 1
                        info.rpm   = rpmName
                        info.type  = type
                        insDao.Update(info)
                    if info is None: # 若指令在知识库中不存在
                        # 尝试在本地搜索man文档
                        file = self.collectMan(i, type)
                        if file is not None: # 若man文档存在
                            # 解析并存储man文档数据
                            storage.Store(file)
                        if file is None: # 若man文档不存在，记录不存在指令
                            notexistinfo += 1

        print(Fore.BLUE + f"本地总指令数：{instcnt} 无数据指令数：{notexistinfo}" + Style.RESET_ALL)
        print(Fore.GREEN + "Complete! ✔" + Style.RESET_ALL)

    def getManPath(self, type: str):
        flag = '1' if type == 'user' else '8'
        return f'{self.manPath +flag}/'

    def collectNoDataInsts(self):
        """
        收集本地知识库没有数据的指令
        """
        usernotedata = []; adminnotdata = []
        ucnt = 0; acnt = 0

        instDao = InstDao()
        rpms = self.collectRpm()
        insts = [self.collectInst(rpm) for rpm in tqdm(rpms, desc="Collecting INSTRUCTIONs")] 
        allUserInsts = set([i for ins in insts for i in ins['user']]) # 所有用户指令
        allAdminInsts = set([i for ins in insts for i in ins['admin']]) # 所有管理员指令

        existUserInsts = set([i.name for i in instDao.SelectAllExistByType('user')]) # 存在数据的用户指令
        existAdminInsts = set([i.name for i in instDao.SelectAllExistByType('admin')]) # 存在数据的管理员指令
        
        return allUserInsts - existUserInsts, allAdminInsts - existAdminInsts
        
        
    
    def collectRpm(self) -> List[str]:
        """
        收集本地rpm包
        """
        # 使用 subprocess.Popen 执行 rpm 命令并获取输出
        process = subprocess.Popen(['rpm', '-qa'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # 读取输出
        output, _ = process.communicate()
        # 将输出解码为字符串，并按行分割
        packages = output.decode().split('\n')
        # 移除列表中的空字符串
        packages = [pkg for pkg in packages if pkg]
        return packages
    
    def collectRpmInfo(self, rpm: str) -> list:
        """
        获取指定rpm包版本信息, list[0] 为名字 list[1] 为版本
        """
        # 使用 subprocess.Popen 执行 rpm 命令并获取输出
        process = subprocess.Popen(['rpm', '-qi', rpm], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # 读取输出
        output, _ = process.communicate()
        # 将输出解码为字符串，并按行分割
        infos = output.decode().split('\n')
        # 移除列表中的空字符串
        infos = [info for info in infos if info]
        
        return [infos[0].split(':')[-1].strip(), infos[1].split(':')[-1].strip()]

    def collectInst(self, rpm: str) -> dict:
        """
        收集指定rpm包指令
        """
        # 使用 subprocess.Popen 执行 rpm 命令并获取输出
        process = subprocess.Popen(['rpm', '-ql', rpm], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # 读取输出
        output, _ = process.communicate()
        # 将输出解码为字符串，并按行分割
        files = output.decode().split('\n')
        # 移除列表中的空字符串
        files = [file for file in files if file]
        # 提取指令名字
        userinsts =  [i.split('/')[-1] for i in files if '/bin/'  in i ]
        admininsts = [i.split('/')[-1] for i in files if '/sbin/' in i]
        return {
                    'user':userinsts, 
                    'admin':admininsts
                }

    def collectMan(self, inst: str, type: str):
        """
        收集指定指令Man文档
        """
        if not os.path.exists('src/assets/man1'):
            os.makedirs('src/assets/man1')
        if not os.path.exists('src/assets/man8'):
            os.makedirs('src/assets/man8')
        # 使用 subprocess.Popen 执行 rpm 命令并获取输出
        flag = '1' if type == 'user' else '8'
        process = subprocess.Popen(['man', flag ,inst], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # 读取输出
        output, _ = process.communicate()
        # 将输出解码为字符串，并按行分割
        text = output.decode()
        # 如果内容存在NAME标题则为有效内容
        if 'NAME' in  text:
            file = f'{self.getManPath(type) + inst}.txt'
            with open(file,'w') as f:
                f.write(text)
            return f'{inst}.txt'
        return None
    
    def exportRpmList(self):
        """
        导出rpm列表
        """
        import os
        # 获取当前工作目录
        cur_path = os.getcwd()

        rpm = self.collectRpm()
        infos = [self.collectRpmInfo(r) for r in tqdm(rpm, desc='Collecting RPMs')]
        req = [i[0] for i in infos]
        output = f'{cur_path}/rpmsexport.txt'
        with open(output,'w') as f:
            f.write('\n'.join(req))

        print(Fore.YELLOW  + f'output: {output}')
        print(Fore.GREEN + "Complete! ✔" + Style.RESET_ALL)

    def downLoadRpmList(self):
        """
        下载rpm列表
        """
        # 获取当前工作目录
        cur_path = os.getcwd()
        file = f'{cur_path}/rpmsexport.txt'
        # 确保rpmexport.txt文件存在
        if not os.path.isfile(file):
            print(Fore.RED + "error: The rpmsexport.txt file does not exist in the current directory" + Style.RESET_ALL)
            return

        with open(file, 'r') as f:
            rpms = [line.strip() for line in f if line.strip()]

        local = self.collectRpm()
        infos = [self.collectRpmInfo(r) for r in tqdm(local, desc='Query Existing')]
        localrpm = [i[0] for i in infos]

        # 将列表转换为集合以进行差集运算
        set_a = set(rpms)
        set_b = set(localrpm)

        # 计算差集，获取本地没有的rpm包
        difference = set_a.difference(set_b)

        error = []
        for rpm in tqdm(difference, desc="Installing RPMs"):
            try:
                subprocess.run(['dnf', 'install', '-y', rpm,], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            except subprocess.CalledProcessError as e:
                # 记录错误信息
                error.append(str(e.stderr.decode().strip()))

        if error!=[]:
            print('\n'.join(error))

        print(Fore.GREEN + "Complete! ✔" + Style.RESET_ALL)


    def initdatabase(self):
        """
        数据库初始化
        """
        for type in self.types:
            self.storage = Storage(type=type)
            self.files = os.listdir(self.getManPath(type))
            self.files = tqdm(self.files)
            for file in self.files:
                self.files.set_description(f'正在解析存储{type}指令信息 {file.split(".")[0]:15}')
                self.storage.Store(file)
        print(Fore.GREEN + "Complete! ✔" + Style.RESET_ALL)