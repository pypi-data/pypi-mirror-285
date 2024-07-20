
import os,json,traceback
from loguru import logger
import psutil #用 pip3 install psutil 才能安装


AivReservedNameList = ['aiv','chat','set','help','llm','updown'] #Aiv系统保留的关键字(用户的Bot的API函数不能以此命名) 2024.4

#--------------------------------进程IPC数据共享： 内存共享--------------------------------------------
#----------------------------------------------------------------------------------------------------
def checkReservedName(name, msg=None):
    ''' 2024.4
        检测用户指定的api函数是否是系统保留字
    '''
    if name.lower() in [reservedName.lower() for reservedName in AivReservedNameList]:
        if msg is not None:
            logger.warning('{}: [{}] 不能使用AIV预留的关键字.'.format(msg,name))
        return True
    else:
        return False

# 把配置文件（dic)写入进程共享内存块中的数据
def _write_mmap(mmaps,data,start=0,lens=0,tojson=True): # mmaps 是共享内存的指针,一个应用中可能有多块
    '''
    * 参数 lens ,指定共享内存长度
    * 参数 tojson ,表明是否要经json转换
    * 参数 data 中,不能包含 '\x00' 空白字符,否则在读取阶段，会读取不完整
    '''
    if tojson:
        jsonstr = _aiv_json(data)
        
    else:
        jsonstr = data
    jsonlen = len(jsonstr)    
    if lens!=0:
        if jsonlen>= lens:
            logger.warning('配置文件超过长度{}，超出内存长度！自动截断'.format(lens))

    #logger.debug('接收到写入长度为：{}参数到共享内存：\n{}'.format(jsonlen,data))
    mmaps.seek(start)
    mmaps.write(bytes(jsonstr,encoding='utf-8'))
    mmaps.flush()

    #在文件末尾添加结束符 '\x00'-----------------
    mmaps.write(b'\x00')
    mmaps.flush()
    #logger.debug('写长度为：{} 的Json格式参数到共享内存：\n{}'.format(jsonlen,jsonstr))
    

#从进程内存块中,读出配置文件 (json字符串),转为 dic 返回
def _read_mmap(mmaps,start=0,leng=0,return_dict=False):
    '''
    ### 读取共享内存中的数据
    * 在写入阶段,写入的数据不能包含 '\x00' 空白字符,否则在读取阶段，读取不完整
    '''
    if mmaps is None:
        logger.error('未建立配置文件内存区域')
    mmaps.seek(start)
    # 把二进制转换为字符串
    buffer = bytearray()
    
    while True:
        chr = mmaps.read(1) #这里的 read()函数返回值是 bytes 
        if not chr:
            break
        
        if chr == b'\x00': # 如果是 空字符,标明读到尽头,chr是bytes类型 ，所以比较时, b'\x00' 前面的b 不能少
            #logger.warning("找到'\x00'空字符串")
            break
        buffer += chr # b'\x00' 字符不能加到文件末尾,不然 json 不能解析
        

    data = None
    if len(buffer)>0:
        data = buffer.decode('utf-8').rstrip()

    #info_str = mmaps.read().translate(None, b'\x00').decode(encoding='utf-8')
    if data is not None:
        pass
        #logger.debug('_read_mmap()从共享内存读长度为：{}的参数\n{},'.format(len(data),data))

    if data is not None and return_dict:
        return json.loads(data) # 从Json 转成 dic 并返回     
    else:
        return data   


#自定义的 python ==> Json 类,可以处理 fun之类的数据
import datetime,types
class AivJson(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            #print("MyEncoder-datetime.datetime")
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        if isinstance(obj, int):
            return int(obj)
        elif isinstance(obj, float):
            return float(obj)
        elif isinstance(obj, types.FunctionType) or isinstance(obj, types.MethodType):
            pass #返回 None 或 null
        #    return obj.tolist()
        else:
            pass  # 2024.1 如果不是以上类型的数据,都略过
            # return super(AivJson, self).default(obj)

def _aiv_json(data):
    '''
        ### Python 数据转 Json
        * 支持 dict/list/tub/datetime/python class (function,byte,str)
        * 直接显示中文 ensure_ascii=False
        * 去除 , : 前后空格separators=(',',':') 
    '''
    return json.dumps(data,cls=AivJson,ensure_ascii=False,separators=(',',':'),indent=4) 

import hashlib

def aivJoinPath(path,*paths):
    ''' 2024.1
        避免在window与linux下路径错误
    '''
    r = os.path.normpath(os.path.join(path,*paths))
    # ret = r.replace('\\', '/')
    return r

def getFileMd5(fileName):
    '''
        计算小文件的md5值 2023.10
        * 4G的文件计算md5码大概要7秒,js端用CryptoJS计算大概要2分钟
    '''
    md5_hash = hashlib.md5()
    with open(fileName, 'rb') as f:
        # 读取文件的块大小
        chunk_size = 1024 * 1024
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

def caleFilePartInfo(filePart,fileSize,partSize= 10):
        ''' 2024.1
            @param filePart 必须大于0  # 分块发送,则从 1开始
            @param fileSize (单位字节B) 指定文件大小
            @param part_size (单位字 Mb) 分包的大小(默认为 10M)
            这个函数不管文件是否存在, 只是根据给定的数据计算各个包的起始位置、可以分多少个包等信息
        '''      
        import math
        partSizeTemp = partSize * 1024 * 1024
        filePartSize = fileSize  #初始化值! 发送的文件块默认是整个文件
        startPos = partSizeTemp * (filePart - 1)  # 开始读取的位置
        # 计算出需要发送的文件块大小(最后的一块也许不足50M)
        filePartCount = 1
        if fileSize > partSizeTemp:  
            filePartCount = math.ceil(fileSize / partSizeTemp) #  math.ceil向上取整
        if filePart<=0 or filePart>filePartCount:
            logger.warning(f'caleFilePartParam()错误: 文件块索引必须介于 1--{filePartCount} 之间')
            return None,None,None

        # 计算出需要发送的文件块字节数 (最后一块和整个文件小于5M的,sendFilePartSize可能都不足 5M)
        if filePart == filePartCount:
            filePartSize = fileSize - (partSizeTemp * (filePart-1))
        else:
            filePartSize = partSizeTemp

        return filePartSize,startPos, filePartCount

def getFileInfo(fileName,reName=False, createMd5=True, part=1, partSize=10):
    '''
        返回一个文件信息对象 2023.10
        * 参数 createMd5  ,默认为True,表示是否生成md5 (对于5G以上的文件,生成md5码大概要10秒时间)
        * 参数 reName, 默认为False,表示是否以md5为名改名
        * 参数 part ,默认0表示不分包,大于0指第n个包,生成的文件信息除了包含总文件信息还,还会生成第n包的信息 2024.1 
            (默认生成第1包的信息, 如果不需要分包, 把生成后的对象的part 改为0即可 ,默认为 part= 1 目的是为了在P2P传输提供完整的文件信息 2024.6)
        * 参数 partSize = 10 (M为单位) = 10485760 = 10 * 1024 * 1024 #文件块大小默认是 10M  2024.1
        * 如果此文件不存在,则只返回文件的路径、文件名在内的信息
        * 如果文件存在,则返回文件的详细信息,包括文件大小、创建时间、访问时间、文件类型等
        * 如果设置reName参数为True,则会计算文件的md5值,并用md5值重新为文件命名

        这是AIV平台的文件传输协议
    '''
    fileInfo = {
        'isDownload': None, # None表示文件没下载, False 表示正在下载, True 表示下载完成
        'downloadCount': 0 ,  #尝试下载次数 (一般不超过 3 次)
        'path': fileName,
        'name': os.path.basename(fileName),
        'size': 0,
        'md5' : None,
        'part': part, #后面可能修改了 2024.6
        'lastModified': None,
        'lastModifiedDate': None,
        'type': None,
        'webkitRelativePath': ''
    }

    if os.path.exists(fileName): #文件如果不存在, 则不能生成文件块的信息  2024.6
        md5 = None
        if createMd5:
            md5 = getFileMd5(fileName)
        import mimetypes
        mime_type, encoding = mimetypes.guess_type(fileName)
        fileInfo['type'] = mime_type
        fileInfo['md5'] = md5
        fileInfo['size'] = os.path.getsize(fileName)
        fileInfo['createDate'] =  int(os.path.getctime(fileName))
        fileInfo['lastModified'] = int(os.path.getmtime(fileName))
        fileInfo['lastModifiedDate'] = int(os.path.getatime(fileName))

        if part>0: # 如果指定分包的索引,则添加以下三个'part','partFileSize','partFilePos'信息到fileInfo对象中 2024.1
            partFileSize,partStartPos, filePartCount = caleFilePartInfo(part,fileInfo['size'],partSize)
            # from loguru import logger
            # logger.warning(f'生成的文件信息是：{partFileSize}、 {partStartPos} 、{filePartCount} ')
            fileInfo['part'] = part #如果分块传输,则从 1 块开始计数 (如果 part=0 表示不分块传输) 2024.6
            fileInfo['partFileSize'] = partFileSize
            fileInfo['partFileCount'] = filePartCount
            fileInfo['partFilePos'] = partStartPos
            

        if reName:
            md5 = fileInfo['md5']
            if md5 is None:
                print('getFileInfo()错误: md5码没有生成!')
            else:
                filePath = os.path.dirname(fileName)
                # print('filePath==',filePath)
                newFileName = os.path.join(filePath,md5+os.path.splitext(fileName)[1])
                # print('newFileName==',newFileName)
                os.rename(fileName,newFileName)
                fileInfo['path'] = newFileName
                fileInfo['name'] = os.path.basename(newFileName)

    return fileInfo

def getDirName(fileName):
    '''
        获取文件所在的文件夹名
    '''
    folder_name = os.path.basename(os.path.dirname(fileName))  # 获取文件夹名
    return folder_name

def getFileNameWithoutExtension(filePath):
    '''
        获取文件名(不包含扩展名) 
    '''
    file_name = os.path.basename(filePath)
    file_name_without_extension = os.path.splitext(file_name)[0]
    return file_name_without_extension

def createQrCode(data,outFileName,logoFile=None):
    ''' 2023.11
        生成二维码
        根据数据data, 生成一个二维码文件,并保存到 outFileName 目录
        logoFile 参数: 决定是否要生成一个带 logo 的二维码
    '''
    import qrcode,json # pip install qrcode 7.4.2
    from PIL import Image #使用 pip3 install Pillow安装,2024.7 , PIL 10.4.0（Python Imaging Library）已经被更强大的库Pillow替代

    # 创建QRCode对象
    qr = qrcode.QRCode(
        version=5,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2
    )

    # 添加数据到QRCode对象中
    # data = {'cmd': 'test', 'data': 'id_12345678'}
    txt = json.dumps(data)
    qr.add_data(txt)
    qr.make(fit=True)

    # 创建Image对象，并将QRCode对象转化成Image对象
    img = qr.make_image(fill_color="black", back_color="white").convert('RGBA')

    if logoFile is not None:
        # 打开logo图片，并将其resize
        # logo = Image.open("E:/QuickSoft/Demo/Aiv图标/紫色/圆角图标(108x108).png")
        logo = Image.open(logoFile)
        logo = logo.resize((80, 80))

        # 计算logo位置
        img_w, img_h = img.size
        logo_w, logo_h = logo.size
        logo_pos = ((img_w - logo_w) // 2, (img_h - logo_h) // 2)

        # 将logo图片添加到QRCode图片中
        img.paste(logo, logo_pos, logo)

    # 保存QRCode图片
    try:
        img.save(outFileName)
    except Exception as e:
        traceback.print_exc()  # 输出完整的堆栈跟踪信息  
        logger.warning('生成二维码出错! error = {}'.format(e))

def checkPortOccupy(port):
    ''' 2024.2
        用psutil模块查询端口是否被占用
        如果端口被占用,则返回占用的程序名和pid, 否则返回 None,None
    '''
    pid = name = None
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            connections = proc.connections()
            for conn in connections:
                if conn.laddr.port == port:
                    name = proc.info['name'].lower().strip()
                    pid = proc.pid
                    # proc.info['cmdline'] 是命令行
                    break
        except psutil.AccessDenied:
            pass
        except psutil.NoSuchProcess:
            pass
    return name,pid

def setWinEnv(path):
    ''' 2024.6
        更新 Window 的环境变量
        只对当前此次Python运行的环境有效(不是永久加入系统的环境PATH变量)
        比如把系统安装的 FFmpeg/bin 运行目录添加到环境变量,方便Py代码调用
    '''
    # 获取当前的系统环境变量
    current_path = os.environ.get("PATH")
    newPath = f"{current_path};{path}" #添加在第一个搜索路径中
    os.environ["PATH"] = newPath # 更新系统环境变量

def setLogFile(logFile,logLevel = 'WARNING'):
    ''' 2024.2
        必须先安装 loguru 包
        默认设置日志的级别和写入的日志文件名 (超过100MB就重新写一个日志文件) 2024.1
        每个子进程<用Process()启动或用subprocess.Popen()启动>都要重新设置一次,不然不会起效果(包括bot模块里,也要重新设置一次)
        logLevel 可选值: TRACE,DEBUG,INFO,SUCCESS,WARNING,ERROR,CRITICAL
        ** 这里的 logLevel 设置,并不影响 loguru 在控制台窗口的输出(只影响写入logFile文件的日志级别)
    '''
    logger.add(logFile, format="[ {time:YYYY-MM-DD HH:mm:ss} {level} ] {message}", filter="", level= logLevel,rotation="100 MB", encoding="utf-8")


def deleteFolderContents(folderPath):
    ''' 2024.2
        只删除文件夹里面的文件及子文件夹,不删除文件夹本身 (清空文件夹)
        因为如果要删除整个文件夹,如果文件夹被占用,有可能不能删除,因此删除里面的内容即可
    '''
    import shutil
    for fileName in os.listdir(folderPath):
        filePath = os.path.join(folderPath, fileName)
        try:
            if os.path.isfile(filePath) or os.path.islink(filePath):
                os.unlink(filePath)
            elif os.path.isdir(filePath):
                shutil.rmtree(filePath)
        except Exception as e:
            logger.warning(f"删除目录: {filePath}失败. Error= {e}")

