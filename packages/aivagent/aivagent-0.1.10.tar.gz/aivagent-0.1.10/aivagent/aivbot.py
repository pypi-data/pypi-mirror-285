'''
### AIV平台Bot自动化程序管理模块
* 此模块的 run()函数,在用户的Bot模块中被调用,必须是最先运行的代码 (不一定是顺序排前面,
    相反,run应该写__main__里(在api开头的函数声明后面);
* 本模块是 AivAgent 端的核心。负责初始化用户开发的Bot自动化程序模块,并管理bot的api函数列表、参数等
* Aiv的Bot模块接口为api开头命名函数,以此开头的函数将自动注册为bot的api函数,在客户端可以直接被调用;
    如果api函数比较多,也可以分模块写,然后使用import导入;
* run()启动前,最好把Bot所在的路径添加到Path中,然后import入loguru(AIV Bot必备模块),否则容易报 
    import错误,找不到依赖包,然后初始化日志工具等,最后再调用run()函数;
* 根据AIV平台注册的Bot 接口,匹配api开头的函数,并把参数拼接和格式化,最后成功调用Bot的api函数;
* 每个Bot api 函数,都有三个阶段被AIV AGI调用,分别是 cmd='init'(Bot被初始化调用)、cmd='param'
    (初始化后获取参数)、cmd='run'(前端用户调用)三个阶段;
* 用户的Bot程序,由AIV AGI服务程序直接调用,而AIV AGI与AIV客户端(app/web)相连接,
* 关于调试: 找到安装目录下: aivc/bin/debug.bat,直接运行即可(运行前要把AIV AGI服务程序关闭);
* AIV AGI 服务程序管理地址: http://127.0.0.1:28067/
* 常用的工具函数,统一放在 aivtool.py 模块中(比如生成文件md5码的函数)
    (2023.12)
* 不要直接使用 AivBot 中以 '_'开头的函数
'''
import sys,os,time,traceback
from loguru import logger

botName= ''
## 1、初始化Aiv Bot 的第一个函数=======================================================================
def run(botId=None, callFun=None,logLevel = 'INFO', option = None) -> None:
    '''
        注册AIV平台的Bot
        @param botId:   Aiv平台分配的bot唯一的token
        @param callfun:  程序初始化后,回调的函数
        @param logLevel: 可选 'DEBUG','INFO','SUCCESS','WARNING','ERROR','CRITICAL' 
        @param option: 当前Bot的参数(如: reload,timeout, ...)

        - desc
        * 此函数,必须是在用户Bot中执行的第一行代码(__main__中,但应该在bot api函数<以api开头>声明之后)
        * 当前模块下,所有非'_'开头的函数,都自动注册为AIV系统的iBot接口函数
        * run()函数必须在模块的 "__main__" 后面调用,并且不能包裹在函数里面调用!
        * 每一个Bot模块都运行在一个独立进程中, 可以在option参数设置 reLoad: True 开启代码修改自动更新客户端iBot接口功能
        * 注意: 在Aivc.exe启动时, 在启动并初始化所有Bot进程, 如何用户对某个Bot开启了 option['reload'] = True, 则初始化后,
                Bot子进程不会退出。因此,Bot的开发目录将被独占(window下不能改名,不能被删除)
    '''
    try:
        import inspect
        # inspect.stack() 返回函数的调用栈
        frame = inspect.stack()
        if frame[1][3] != '<module>':
            raise Exception('run() 函数必须在用户的bot模块"__main__"下调用,且不能包裹在函数中调用')
        
        obj = inspect.getmembers(frame[1][0]) #  
        #数据是[(,) , (,) , (,) , (,)] 这样的
        globalvar = None 
        for tup in obj:
            if tup[0]=='f_globals': #字段'f_globals'记录的值 ,等同于函数 globals() 返回的值, 但globals()必须在自己的模块下运行,灵活性不足
                globalvar = tup[1]
                break

        from .aivapp import _aivAppInit #初始化全局路径、环境变量、logger
        _aivAppInit(globalvar['__file__'],False, loglevel=logLevel)
        
        
        aivBotInfo = AivBotInfo()
        global botName
        botName = aivBotInfo.botName

        # 检测某些模块是否安装(目的是提醒开发者,减少无谓的时间浪费) 2024.6
        def _checkModuleInstalled(moduleName, isMust= True):
            import importlib
            try:
                importlib.import_module(moduleName)
            except ImportError:
                msg = f"Bot: {aivBotInfo.botName} 检测发现 {moduleName} 未安装! 请在cmd窗口运行: pip install 安装"
                if moduleName == 'loguru':
                    print(msg)
                else:
                    if isMust: #必须安装的包, 给出警告
                        logger.warning(msg)
                    else:
                        logger.debug(msg+" (可选)")

        # logger.warning('Bot的Option是: {}'.format(aivBot.botOption))
                    
        _checkModuleInstalled('loguru')
        _checkModuleInstalled('psutil')
        _checkModuleInstalled('cv2', False)  #对于用到opencv-python包,在用nuitka编译,如果在main.exe代码中不显式import cv2
                                             # 会导至以下错误： ImportError: DLL load failed while importing cv2: 找不到指定的模块。
                                             # cv2 用 pip install opencv-python 安装
        
        import asyncio

        os.environ['PYTHONUNBUFFERED'] = '1' #禁用标准输出的缓冲区 2023.10
        # 当使用Python调用FFmpeg时，如果输出信息太多，可能会导致标准输出（stdout）
        # 缓冲区溢出并引发错误。这通常是因为输出信息超过了缓冲区的容量。
        # 标准输出的默认缓冲区大小通常是8192字节,通过设置环境变量PYTHONUNBUFFERED为1来禁用缓冲区

        # 设置日志保存的文件路径,每一个iBot进程都要设置一次(loguru) 2024.2
        botPath = os.path.dirname(os.path.abspath(globalvar['__file__'])) #Bot程序路径
        
        from .aivtool import setLogFile  
        #设置日志保存的文件路径和级别,默认把WARNING级别的日志保存在执行程序目录的botError.log文件中(但不影响控制台输出的日志) 2024.2 
        logFile = os.path.join(botPath,'botError.log') #在bot模块根目录下生成一个日志文件 2024.3
        
        setLogFile(logFile, logLevel= 'INFO')  #默认只显示 INFO信息(只影响写入本地文件的日志等级,不影响控制台输入日志的等级)
        
        # global aivBot
        aivBot = AivBot()
        aivBot.botInfo = aivBotInfo  # AivBotInfo 类
        aivBot.botInfo.path = botPath
        aivBot.botInfo.botId = botId
        aivBot.botOption = option # 当前Bot的配置内容
        aivBot.botInfo.logLevel = logLevel
        
        aivBot._regBotApi(globalvar)

        from .aivmmap import AivBotMmap
        # global aivBotMmap
        # print('AivBot收到的 taskMMAPName333 ==> {}'.format(aivBot.taskMMAPName))
        aivBotMmap = AivBotMmap(aivBot)
        aivBot.aivBotMmap = aivBotMmap

        aivBot.aivBotMmap.onStartTask = aivBot._onStartTask #响应AGI调用Bot的api接口执行任务的事件
        aivBot.aivBotMmap.onGetBotApi = aivBot._onGetBotApi #响应AGI获取Bot的api接口数据事件 2024.4

        if callFun is not None:
            callFun()  #调用用户设置的回调函数----------

        # aivBot._initParam() # 加载 Bot Api的参数,在这里,可以在PY端设定客户端必须传递的参数(约定用户必须输入的参数) 2023.11

        ''' 2023.11
            用线程检测进程 wcPid 是否退出
            用线程检测 wcPid 进程是否退出(不是用 asyncio 协程,是用 threading 检测),如果wcPid进程退出,线程也跟着退出 
            原因是 asyncio的所有子协程都是在进程的主线程运行, 当AIV平台的bot模块运行任务时,基本是上独占模式(死循环)
            这样如果用户中止任务,虽然bot模块也收到 TaskState.taskProExit 信号,但 aivBotMmap.run() 阻塞在运行任务上
            没办法响应  TaskState.taskProExit 信号, 但线程是可以的.因此,在 aivBotMmap.run()检测任务是否中止信号上,
            另外用线程 threading 建立一个独立于主线程的子线程,用于检测wcPid是否退出(这里是检测aivwc.py的进程)。这样,
            当协程失灵时,threading的线程仍然可用,可以保证主进程下达的中止指令可以被执行。
        '''
        aivBot.aivBotMmap.createCheckPidThread([aivBot.botInfo.ppid,aivBot.botInfo.wcpid],aivBot.botInfo.botName)

        if option.get('reload', False):
            logger.warning(f'Bot模块: {aivBot.botInfo.botName} 启动成功. 已经打开 "reload"模式,建议正式发布后关闭.')
        else:
            logger.debug(f'Bot模块: {aivBot.botInfo.botName} 启动成功.')
            
        # 协程函数
        async def _main():
            # aivBotMmap的功能主要是检测是否有新任务(抢单),二是检测任务的状态,如果任务被前端取消,则马上退出进程
            # 另外,也要不断检测任务是否超时,超时就自动中止进程 2023.11
            asyncio.create_task(aivBot._initParam()) # 2024.6
            asyncio.create_task(aivBot.aivBotMmap.run())  
            asyncio.create_task(aivBot.aivBotMmap.runSlot())  
            while True:
                await asyncio.sleep(0.2) #只要主程序不退出,上面的协程就一直运行

        asyncio.run(_main())

    except Exception as e:
        logger.warning(f'Bot模块: {botName} > run() 出错! Error= {e}')



class AivBotInfo:
    '''
        当前运行的Bot对象的信息汇总
    '''
    def __init__(self) -> None:
        self.logLevel = 'INFO'
        self.pid = os.getpid() # 当前进程的PID
        self.botId = ''
        self.path = '' #主执行文件路径(含文件名)

        if len(sys.argv)>1:
            self.ppid = int(sys.argv[1]) #父进程的pid,根据父进程pid,如果它退出,自己也退出
        if len(sys.argv)>2:
            self.taskMMAPName = sys.argv[2] #这个是前端传过来的 taskId (32位长度的字符串,全球唯一), 当前任务启用的共享内存名称
        if len(sys.argv)>3:
            self.wcpid = int(sys.argv[3])  # 同级子进程 wc的进程pid,如果在命令行参数中传入此值,则可以根据此值,同步退出进程
        if len(sys.argv)>4:
            self.botName = sys.argv[4] #第4个参数传 botName 2023.12
        if len(sys.argv)>5:
            # 所有参数都必须转成str类型传进子进程,因为这里要对比 == 'True'
            self.isGetBotApi = sys.argv[5] == 'True' #第5个参数传决定当前进程是任务进程还是获取Bot数据的进程 2024.4
            

    def getBotInfo(self):
        '''
            返回当前模块的信息
        '''
        return {
            'logLevel': self.logLevel,
            'botName': self.botName,
            'botId' : self.botId,
            'path': self.path,
            'pid': self.pid,
            'ppid': self.ppid,
            'wcpid': self.wcpid,
            'taskMMAPName': self.taskMMAPName
        }

class AivBot:
    def __init__(self) -> None:
        self.botInfo = None # AivBotInfo 类
        self.task = None #用于临时记录任务信息, 在 addFileToTaskOutParam()调用
        self.botOption = None
        self.api = [] # 记录当前bot模块所有的Api信息
        self.cmd = ''   #调用iBot的Api时指令类型 ('init','run' 可选)
        self.isSetResult= False # 用户是否设置了返回值

    async def _initParam(self):
        '''
            2024.1
            约定客户端调用此Bot必须要传递的参数
            每一个iBot接口,都可以在 aivBot.cmd == 'init' 阶段,初始化iBot被调用时的参数约定。相当于通讯协议或调用约定
            在Bot初始化阶段, initParam会调用iBot接口,并设置 aivBot.cmd = 'init' 标志,根据此标志位,开发者可以按照AIV
            约定设置调用参数。
            * 请勿直接调用AivBot以'_'开头的函数
        '''
        import asyncio

        if self.api is not None:
            # logger.debug('self.api 不为空!')
            for aivApi in self.api:
                # logger.debug('循环所有Api {}'.format(aivApi['name']))
                if aivApi['paramIn'] is None:
                    try:
                        # callParam = {'sysInfo':aivBotMmap.sysInfo} #把任务信息和系统信息打包,一起给bot的api传参
                        self.cmd = 'init'    #把指令设为初始化标志

                        param = None
                        try:
                            if asyncio.iscoroutinefunction(aivApi['fun']): #检测如果是异步函数(函数用 async def xxx() 定义的),则用 await 调用 2024.6
                                param = await aivApi['fun'](self) #执行api的初始化函数, 传递 cmd = 'init' 指令进去, 如果有自定义的参数,则一起返回
                            else:
                                param = aivApi['fun'](self) #执行api的初始化函数, 传递 cmd = 'init' 指令进去, 如果有自定义的参数,则一起返回
                        except BaseException as e:
                            logger.warning(f'Bot: {self.botInfo.botName} {aivApi["fun"]}() 在{self.cmd}阶段错误, Error= {e}')
                            traceback.print_exc()  # 输出完整的堆栈跟踪信息                             

                        if param is not None:
                            logger.debug(f"{aivApi['name']} 的自定义参数是: {param}")
                    except Exception as e:
                        logger.warning(f"函数: {aivApi['name']}获取参数阶段出错, Error= {e}")
        
            # 检查所有的Api函数的参数是否都设置了---
            haveParam = True
            for aivApi in self.api:
                if aivApi['paramIn'] is None:
                    haveParam = False
                    break

            if haveParam:
                logger.debug('Bot模块 {} 载入完成!'.format(self.botInfo.botName))
                # break


    def _onGetBotApi(self):
        ''' 2024.4
            响应AGI向当前Bot获取api接口数据的事件
            self.api 中的数据是api对象列表,api中包含function的内存地址,它们是不能转换成Json数据.
            (aivtool.py中的_aiv_json()在转换成JSON数据时,会自动抛弃指向function内存地址的数据)

            botApi: Bot的api列表(api中也有每个api的配置: 'apiOption' 字段)
            botOption: Bot的全局配置参数(如:reload,timeout等)
            * 请勿直接调用AivBot以'_'开头的函数
        '''
        return {'botApi': self.api, 'botOption': self.botOption}
    
                      
    def _addFileToTaskOutParam(self,filePath, paramName= 'prompt', paramList = None):
        ''' 2024.6
            往参数列表添加文件
            默认是操作 self.task['paramOut'], 也可以指定一个空的 [] 操作,这样可以自定义一个参数列表,最后再赋值给 'paramIn' 或 'paramOut'
            @param filePath :文件必须存在磁盘
            @param paramName: 指定保存的参数名称(名称不区分大小写, 同类型的参数,如果名称重复,将会合并)
            @param paramList :如果要单独生成一个Aiv平台使用的输入输出参数, 可以传递一个非None列表进来
            @return : 返回一个包含输入参数的列表
            * 请勿直接调用AivBot以'_'开头的函数
        '''
        
        if paramList is None:
            paramList = []
        
        if not os.path.exists(filePath):
            logger.warning('找不到文件: {}'.format(filePath))
            return paramList
        
        else:

            
            # logger.debug('接收新的回传文件: {}'.format(filePath))
            # def _caleFile(): #统计生成的文件数量及所有文件大小, 以便后期统计
            #     fileCount,fileSize = 0,0
            #     for paramOut in self.task['paramOut']:
            #             if paramOut['type'].lower() == 'file':
            #                 for file in paramOut['data']:
            #                     fileCount += 1
            #                     fileSize = fileSize + file['size']
            #     return {'fileCount': fileCount, 'allFileSize': fileSize}

            from .aivtool import getFileInfo         
            currParam = None
            isEmptyFile = True
            if len(paramList) > 0:                
                for param in paramList:
                    # 'paramOut'里面必须有且仅有一条 'type'=='FILE'的记录 2024.4
                    if (param['type'].lower() == 'file'  and param['name'].lower()== paramName) and param['data'] is not None:
                        isFind = False
                        currParam = param
                        # 如果已经存在 param['type'] == 'FILE' 的记录,则查询当前文件是否保存在里面
                        for file in param['data']:
                            if file['path'].lower() == filePath.lower():
                                isFind = True
                                break

                        if not isFind:
                            # logger.debug('接收新的回传文件: {}'.format(filePath))
                            # 如果判断没有保存,则新增一个文件记录到 'data'数组
                            param['data'].append(getFileInfo(filePath))

                        isEmptyFile = False

            if isEmptyFile: #没有 'type' == 'FILE' 的记录,直接添加一条
                currParam = {'type': 'file', 'name': paramName, 'data': [getFileInfo(filePath)]}
                paramList.append(currParam)

            # option = _caleFile()
            # currParam['option'] = option

            return paramList


    def _addStringToTaskOutParam(self, text, paramName= 'prompt', paramList = None):
        ''' 2024.6
            往参数列表添加字符串
            默认是操作 self.task['paramOut'], 也可以指定一个空的 [] 操作,这样可以自定义一个参数列表,最后再赋值给 'paramIn' 或 'paramOut'
            @param text : 文本
            @param paramName: 指定保存的参数名称(名称不区分大小写, 同类型的参数,如果名称重复,将会合并)
            @param paramList 如果要单独生成一个Aiv平台使用的输入输出参数, 可以传递一个非None列表进来
            * 请勿直接调用AivBot以'_'开头的函数
        '''
        
        if paramList is None:
            paramList = []

        def _caleText(): #统计生成的文字行数及字数,以便后期评估生成的数据
            line,textLong = 0,0
            for paramOut in paramList:
                    if paramOut['type'].lower() == 'string':
                        for text in paramOut['data']:
                            line += text.count('\n') #计算每个字符串中包含多少个'\n'即是多少行
                            textLong += len(text)
            return {'lineCount': line, 'textCount': textLong}

        isEmptyText = True
        currParam = None
        if len(paramList)>0:
            for param in paramList:
                # 'paramOut'里面必须有且仅有一条 'type'=='STRING'的记录 2024.4
                if (param['type'].lower() == 'string' and param['name'].lower()== paramName) and param['data'] is not None:
                    currParam = param
                    param['data'].append(text)
                    isEmptyText = False
                    break
 
        if isEmptyText:      
            currParam = {'type':'string','name':paramName, 'data': [text]}    
            paramList.append(currParam)

        option = _caleText() #统计生成的文字行数及字数 (如果是文件数据,则由aivc模块统计生成的文件总大小和文件数量) 2024.6
        currParam['option'] = option

        return paramList
        


    def _regBotApi(self,glob:dict): #利用 globals() 读取指定模块的所有函数名
        ''' 2023.10
        ### 注册 bot 模块
        * 参数 glob 包含有模块的函数及函数地址！
        * 将自动注册所有用户自定义的函数!(除以横线'_'开头的和run()函数)
        * Api 函数必须有两个参数,分别是(cmd, parser)
        * 可以导入其它模块的函数成为api函数 : from xxx.xxx import xxxxfun
        * 请勿直接调用AivBot以'_'开头的函数
        '''
        from .aivtool import checkReservedName
        lst = list(glob)
        import types
        # logger.debug('bot 模块所有参数如下 (包含模块内所有函数、方法名称和内存地址): \n{}'.format(glob))

        #循环模块的所有函数,把aiv 开头的函数自动导入----------------------------------
        for fun_name in lst:
            fun = glob[fun_name]   
            if (type(fun) == types.FunctionType) or (type(fun) == types.MethodType): #判断是方法（而不是属性)
                if fun_name != 'run' and not fun_name.startswith('_'): #排除检测 run()函数和 "_"开头的函数 2024.3 ,其它函数都可以导出                              
                    
                    if not checkReservedName(fun_name,'Bot: {} 的Api函数'.format(self.botInfo.botName)):
                        
                        title = ''
                        if fun.__doc__ is not None:
                            title = fun.__doc__.strip()[:16] #读取函数备注内容,取前16个字符

                        # apidict 只记录静态的信息
                        apidict = {'bot':self.botInfo.botName, 'name':fun_name, 'title': title, 'fun':fun,'paramIn':None,'apiOption':None}
                        self.api.append(apidict)

                        # callParam = {'bot':self, 'sysInfo':aivBotMmap.sysInfo} #把任务信息和系统信息打包,一起给bot的api传参  
                        # fun('init', callParam) #初始化Api函数
                 

        logger.info(f'Bot: {self.botInfo.botName} - iBot 接口列表初始化完成.')

        if len(self.api)==0:
            logger.warning(f'Bot: {self.botInfo.botName} 还没有注册任何 iBot 接口.')
        else:
            logger.debug(f'Bot: {self.botInfo.botName} > run() 成功启动! \n---- iBot 接口列表是 ----: \n{self.api}')



    async def _onStartTask(self,task):
        ''' 2023.09
            @param task: 任务信息
            * 前端返回服务器,服务器调用 Bot 的参数,是一个dict列表,本函数用 parser.parse_args 把dict转换成 Namespace 命名空间
            * 此函数把多余的数据删除,只留下类似格式dict: {'参数名1': '参数值1','参数名2': '参数值2', ... } 
            * 请勿直接调用AivBot以'_'开头的函数
        '''
        import asyncio
        # logger.debug('aivBot 收到的启动任务参数是: task ==> {}'.format(task))

        # ======= 调api的参数准备 ============================================== 1
        apiName = None
        self.isSetResult = False
        try:
            # 检测是否有输入参数 'paramIn'
            if task['paramIn'] is None:
                raise Exception("任务的 ParamIn 为空！")
            
            self.task = task
            self.task['result']['apiTimeStart'] = int(time.time()*1000) # api的启动时间(毫秒)

            # 检查是否有调用的bot api 函数名
            apiName = task['apiInfo'].get('name',None)
            if apiName is None:
                logger.error('客户端没有指定要调用的bot iBot接口名称! ')

            if len(self.api)==0:
                logger.error('检测到Bot: {} 无注册任何iBot函数.'.format(self.botInfo.botName))


            apiName = apiName.strip()
            # 根据任务给定的api函数名,找出 bot 对应的真实函数 (通过 botName)
            apiFun = None
            # apiOption = None
            for apiObj in self.api:
                if apiObj['name'].strip().lower() == apiName.lower():

                    apiFun = apiObj['fun']
                    # apiOption = apiObj['apiOption'] #对于 api的配置,用户可以在api函数中自行利用
                    break

            if apiFun is None:
                raise Exception(f'本地Bot模块无api函数:[ {apiName} ]! 请检测Bot模块的api函数名称.')
            
            # ============正式调用bot api 函数 =========================================================== 2 
            from .aivmmap import TaskResultCode
        
            # 运行bot api函数('run'阶段)----------------------------------------------
            # callParam = {'sysInfo':aivBotMmap.sysInfo, 'taskInfo': task, 'apiOption': apiOption} #把任务信息和系统信息打包,一起给bot的api传参
            self.cmd = 'run'    #把指令改为运行标志
            if asyncio.iscoroutinefunction(apiFun):  #检测如果是异步函数(函数用 async def xxx() 定义的),则用 await 调用 2024.6
                await apiFun(self) #调用用户Bot的api函数 2024.4
            else:
                apiFun(self)
            # logger.warning('Bot api {} 运行返回结果是: {}'.format(apiName,retTask))
            # -----------------------------------------------------------------------
            
            if self.isSetResult == False and  self.task['result']['code'] != 200: #如果开发者没有设置返回结果, 则默认返回 code=200 的成功标志 2024.1
                # 设置成功标志
                self.aivBotMmap.setTaskResultCode(TaskResultCode.taskOk, f'Bot: {self.botInfo.botName} > {apiName} > 运行成功.') # 设置为OK状态

        except BaseException as e:
            import traceback
            traceback.print_exc()  # 输出完整的堆栈跟踪信息
            if self.botInfo.logLevel == 'DEBUG':            
                e = traceback.format_exc() # 获取出错的所有文本
            
            errMsg = f'Bot: {self.botInfo.botName} > {apiName}() 在{self.cmd}阶段出错--->\n {e}'
            self.aivBotMmap.setTaskResultCode(TaskResultCode.taskSvr,errMsg) # 设置为服务器出错状态,并把出错信息回传js端 2023.12
        
        finally:
            self.task['result']['apiTimeEnd'] = int(time.time()*1000) # api运行的结束时间(毫秒)
            self.aivBotMmap.endTask() # api函数内修改了task对象,也会同步返回



    async def startSlotTask(self, apiInfo, paramIn= None , timeOut = 0):
        ''' 2024.6
            启动插槽任务  

            @apiInfo 对象, 调用第三方Bot的信息, 数据格式: {'agiDeviceId': '调用的 AGI deviceId', 'botName': '调用的Bot名称', 'botApi': '调用的 iBot 的名称'}
            @param paramIn 数组, 调用第三方Bot的输入参数列表 (输入None默认选择当前任务的ParamIn)
            @param timeOut 任务超时等待时间, 0 为Bot主进程超时设置相同 (在Bot的run()中可以设置)
            @return 返回第三方Bot运行的结果(数据格式与当前 aivBot.task 一样)

            * 当前startSlotTask()函数被调用后,会一直阻塞等待 Slot 任务返回, 开发者可以设置超时等待时间
            * 但超时间不能大于当前 Bot 设置的超时时间(如果超过,Bot的主进程就被kill,这里的等待子进程也会退出)
            * 调用此函数必须使用 await 修饰,并且用户的Bot的iBot函数也必须用 async def xxx() 定义为异步函数
            * 需要 import asyncio
        '''
        import copy

        if paramIn is not None:
            slotParamIn = copy.deepcopy(paramIn)  #必须深度复制,避免修改原来的 paramIn 参数
            logger.debug('调用第三方Bot使用了用户自定义输入参数!')
        else:
            slotParamIn = copy.deepcopy(self.task['paramIn']) #必须深度复制,避免修改原来的 paramIn 参数
            logger.debug('调用第三方Bot使用了原输入参数!')

        for param in slotParamIn:
            if param['type'].lower() == 'file':
                for file in param['data']:
                    file['isDownload'] = None #把是否下载的标志初始化为 '未下载' None 状态 

        # print(f'生成的任务参数得: {slotParamIn}')
        return await self.aivBotMmap.startSlotTask(apiInfo, slotParamIn, timeOut)



    def createParamIn(self,type, data, paramName= 'prompt', paramIn= None):
        ''' 2024.6
            创建一个指定数据的AIV标准参数记录, 填入 paramIn 中,并返回
            一般是用于调用第三方 Bot 时,需要准备 paramIn 参数列表, 用这个 pushIn() 即可以完成工作
            @param type 参数类型 常用的两大类: 'string' (可以放json字符串), 'file' , (以后会扩充: 'enum', 'bool', 'int' 等 )
            @param data 可以是字符串, 或文件路径(字符串), 根据type类型填写正确
            @param paramName   参数名称 (可选)
            @param paramIn  操作的参数列表 (如果多次操作同一个 paramIn, 则会合并成仅一条 'file'参数或仅一条 'string'参数,
                            但参数的 ['data'] 字段中有多条记录)
            @return 填充了参数的 paramIn 列表
        '''
        if type.lower() == 'string':
            return self._addStringToTaskOutParam(data,paramName, paramIn)

        if type.lower() == 'file':
            return self._addFileToTaskOutParam(data,paramName, paramIn)
        
        
    # def pushParam(self, type, data, paramName= 'prompt', paramList= None):
    #     if type.lower() == 'string':
    #         return self._addStringToTaskOutParam(data, paramName, paramList)

    #     if type.lower() == 'file':
    #         return self._addFileToTaskOutParam(data, paramName, paramList)
        

    def push(self,type,data, paramName= 'prompt', paramStr= 'paramOut'):
        ''' 2024.1
            添加输出内容
            @param type: 可选值 'file','string' ('string' 可以放 json, 未来支持'enum','int','bool')
            @param data: 输出客户端的具体内容(文件路径、输出到客户端的字符串等)  
            @param paramName: 指定保存的参数字段名称 (相同的字段名称,每次调用 push()都会合并在一起 )
            @param paramStr: 默认是往 task['paramOut']添加参数, 可选值 'paramOut', 'paramIn'
                    'paramIn'的使用场景是在调用第三方Bot时,可以给'paramIn'添加新的参数使用
            @return : 返回添加了内容的 paramOut 参数列表 
        '''
        if self.task is None:
            logger.warning("如果是 cmd =='init' 阶段, push()函数不能使用! 需要在 cmd =='run' 阶段, 请加上if cmd == 'run' 语句")
            return
        
        if type.lower() == 'string':
            return self._addStringToTaskOutParam(data, paramName, self.task[paramStr])

        if type.lower() == 'file':
            return self._addFileToTaskOutParam(data, paramName, self.task[paramStr])

        
        # logger.debug('当前输出的内容是: {}'.format(self.task['paramOut']))

    def setResult(self, code, msg, task= None, isShow= True):
        ''' 2024.6
            设置当前Bot任务的返回信息
            @param code : 200 代表成功, 其它值均为失败
            @param msg  : 返回的消息
            @param task : 可以设置第三方Bot调用后返回的任务 (比如把失败的任务改成功的任务)

            默认在整个 iBot执行过程中无需调用 setResult 设置返回值, AIV会自动根据执行情况返回对应的内容。
            如果开发者需要根据自定义的情况返回错误/成功的信息,可以使用此函数
            * 如果设置了 code非200的值, 则表示Bot任务失败并返回客户端.
            * 也可以直接修改 aivBot.task里面的'result'对象
        '''
        setTask = self.task
        if task is not None:
            setTask = task
        if setTask is None:
            return
        
        setTask['result']['code'] = code
        setTask['result']['msg'] = msg

        if code != 200 and isShow:
            logger.warning(msg)

        self.isSetResult = True 


    def getOutPath(self,extName= '', childPath= None, defaultDir= 'out'):
        ''' 2024.3
            获取输出文件目录 或 文件名

            @param extName 需要返回的文件名扩展名(如果设置了此参数,则函数会返回一个可用的文件名<扩展名是extName> )
            @param childPath : 需要创建的子目录 (如果指定此值,则在 aivc/data/out 目录下再创建一个子目录,如 comfyUI可以创建此目录)
                                Aiv系统将会定时清理aivc/data/out及其子目录
            @param defaultDir : 默认的输出目录, 可选值 'out', 'temp'
            @return : 返回一个在系统输出目录下的子目录或一个文件名 (一般在 d:/aivc/data/out)

            目的是在AIV系统默认的输出目录中创建一个子文件夹(一般是 d:/aivc/data/out 目录),用于保存iBot生成的数据
            可以在此系统目录基础上新建一个子目录给每个Bot专用 ,'sys.outDir'目录里的生成文件会定时被清理, 
            可以避免系统运行久了垃圾过多的问题. (每隔10分钟系统清理一次超过24小时未使用的临时文件,比如图片、视频等)
            客户端一般都是生成图片或程序即会自动下载, AGI端无需长期保存. 2024.3
        '''
        
        outPath = self.aivBotMmap.sysInfo['sys.outDir']  # 对应安装目录的 aivc/data/out
        if defaultDir.lower() == 'temp':
            outPath = self.aivBotMmap.sysInfo['sys.tempDir']  # 对应安装目录的 aivc/data/temp

        if childPath is not None:
            outPath = os.path.normpath(os.path.join(outPath,childPath)) #需要用normpath()规范化路径
            if not os.path.exists(outPath):
                os.mkdir(outPath)

        if extName is not None and extName != '':
            if not extName.startswith('.'):
                extName = '.' + extName
            import time
            fileName = str(int(time.time()))
            count = 0
            while True:
                filePath = os.path.normpath(os.path.join(outPath, fileName + extName))
                if not os.path.exists(filePath):
                    break # 如果 aivc/data/out 目录还没存在此文件,则把文件名返回
                else:
                    count += 1

            return filePath

        return outPath # 如果 extName 扩展名参数为'', 则返回目录名
    

    def getSysinfo(self):
        ''' 2024.1
            获取系统信息
            包含 AGI 行时间、系统使用的路径、软件版本等所有信息
        '''
        return self.aivBotMmap.sysInfo

    # async def getPrompt(self, apiInfo = None, timeOut= 5):
    #     ''' 2024.6
    #         获取客户端传过来的 prompt 

    #         @param apiInfo: 即将调用的远程Bot语音转文字机器人的iBot信息 (如果是调用本机则不用传)
    #         @param timeOut: (单位:分钟),调用第三方Bot机器人的超时时间, 默认5分钟
    #         @result: 文字的提示词内容
            
    #         与 self.getParam() 函数类似, getParam()通用性更强, getPrompt()仅支持获取prompt提示词
    #         此函数先检查 'string' 参数中是否有 'prompt' 字段的参数,如果有直接返回
    #         如果没有,则检查是否有 *.mp3/*.wav等的音频文件,如果有,则调用第三方Bot(一般是AivAudio)语音转文字
    #         把生成的文字设为 'prompt'的值并返回

    #         * 注意: 因为此函数有可能调用第三方的 Bot, 因此函数被声明为 async 异步函数,调用时必须使用 await,
    #         * 而且用户的Bot的iBot函数也要声明为 async 异步函数 (需要 import asyncio)
    #         * 用户也可以自定义从客户端的 task['paramIn'] 列表中取出客户端传递的参数
    #     '''
    #     promptText = None
    #     param = self.getParam()

    #     if param is not None: #优先取 task['paramIn']的 'string' 中的 'prompt' 入参
    #         promptText = param
        
    #     else: 
    #         # 如果没有文字入参, 则尝试查询是否有mp3或wav文件(前端可以使用语音输入指令),如果有则调用第三方的 Bot 获取语音识别文字
    #         # 用户也可以自定义其它语音识别的方法(比如用http调用百度语音、迅飞语音接口返回语音识别的文字) 2024.6
    #         fileList = self.getFiles() #如果使用语音输入做提示词, 一定要把语音的paramName 设为 prompt
    #         if len(fileList)>0:
    #             mp3File = fileList[0] #获取第一个文件 (prompt的音频文件必须放在第1个元素) 2024.6
    #             logger.debug(f'使用识别 prompt 的音频文件是：{mp3File}')
    #             extList = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.aiff', '.au', '.m4a', '.opus']
    #             fileExtension = os.path.splitext(mp3File['name'])[1].lower()
    #             if fileExtension.lower() not in [x.lower() for x in extList]:
    #                 logger.warning(f'不是语音文件: {extList}, 获取 prompt 提示词失败!')
    #                 return None

    #         else:
    #             logger.warning('客户端没上传参数名为 "prompt" 的提示词或参数名为 "prompt" 的语音文件, 请检查客户端!')
    #             return None

    #         # logger.debug(f'输入参数是: {paramIn}')
    #         if apiInfo is None:
    #             apiInfo = {
    #                 'agiDeviceId': '', #如果是调用本机的 Bot, 则传空值
    #                 'botName': 'AivAudio',
    #                 'botApi': 'audioToText'
    #             }
    #         slotTask = await self.startSlotTask(apiInfo,None, timeOut= timeOut)

    #         if slotTask['result']['code'] != 200:
    #             errMsg = f'{slotTask["result"]["msg"]}'
    #             logger.warning(errMsg)
    #             return None

    #         else:
    #             if len(slotTask['paramOut']) == 0:
    #                 errMsg = f'AivAudio: 返回空数据!'
    #                 logger.warning(errMsg)
    #                 return None
            
    #             # return aivBot.setResult(400, 'AI任务执行失败!')
    #             text = self.getParam(paramStr= 'paramOut',task= slotTask)   
    #             if text is not None:         
    #                 promptText = text

    #     # logger.warning(f'AivAudio: Bot返回的结果是: {promptText}')
    #     return promptText
    
    def getFiles(self, paramName= 'prompt', paramStr = 'paramIn', task = None):
        ''' 2024.7
            获取 task['paramIn'] 或 task['paramOut'] 中的文件参数
            默认是获取'prompt'参数的文件,这是常用的文件参数,也可以指定获取其它参数名的文件
            @param paramName: 参数名称, 默认为'prompt', 在客户端,可以在 聊天录入框底部"+"按钮中添加文件参数
            @param paramStr: 指定读取 'paramIn'或'paramOut'对象的数据
            @param task: 可以指定读取第三方Bot返回的任务内容中的'paramIn'或'paramOut'中的参数
            @result: None|[ 文件列表<包含名称、路径、大小...>等信息 ] 列表
        '''
        if paramStr not in ['paramIn', 'paramOut']:
            logger.warning('获取参数只能从 "paramIn","paramOut" 中二选一')
            return None
        
        if task is None: #可以指定非当前 self.task 的值 (使用场景: 调用第三方Bot返回的数据,与 self.task 格式相同,可以使用 get()函数获取)
            task = self.task
        paramList = task[paramStr] # 可以读出 'paramIn' 或 'paramOut'
        for param in paramList:
            if param['type'].lower() == 'file' and  param['name'].lower() == paramName.lower():
                return param['data']
            
        return None
    

    def getParam(self, paramName= 'prompt', paramtype= None, paramStr = 'paramIn', task = None):
        ''' 2024.6
            获取任务参数 (只能读取非'file'的参数)
            @param paramName 可以指定获取参数的名字, 如 'prompt' (必须与客户端传参匹配)
            @param paramtype:    将要读取的参数类型信息 (不指定将自动判断)
            @param paramStr 读取的参数名字符, 可选 'paramIn', 'paramOut'
            @param task 要读取的任务对象, 默认是读取当前aivBot的task对象. 
                        可以指定非当前 self.task 的值 (使用场景: 调用第三方Bot返回的数据,与 self.task 格式相同,可以使用 get()函数获取)
            @return : 'file'返回值是一个 [{fileInfo}列表] ,  其它是返回一个值, 否则返回 None, 注意!

            功能:
                1、获取 task['paramIn'] 的参数 (客户端调用当前AGI的Bot的iBot接口,传参放置在 task['paramIn'] 列表中)
                2、或获取调用第三方Bot返回的数据,返回的结果存在 task['paramOut'] 列表中
        '''
        if paramStr not in ['paramIn', 'paramOut']:
            logger.warning('获取参数只能从 "paramIn","paramOut" 中二选一')
            return None
        
        if task is None: #可以指定非当前 self.task 的值 (使用场景: 调用第三方Bot返回的数据,与 self.task 格式相同,可以使用 get()函数获取)
            task = self.task
        paramList = task[paramStr] # 可以读出 'paramIn' 或 'paramOut'

        for param in paramList:      

            if param['name'].lower() == paramName.lower() and param['type'].lower() != 'file': #排除不搜索 'file'类型的数据

                if paramtype is not None:
                    if param['type'].lower() == 'boolean' or param['type'].lower() == 'bool': # 返回一个值
                        return param['data'][0]
                    elif param['type'].lower() == 'string': # 返回一个值
                        return '\n'.join(param['data']) # 返回一个字符串(如果是多行,则以 \n 分隔)
                    else:
                        return None
                    
                else:
                    if isinstance(param['data'][0], (bool,int,float)):
                        return param['data'][0]
                    elif isinstance(param['data'][0], str):
                        return '\n'.join(param['data']) # 返回一个字符串(如果是多行,则以 \n 分隔)
                    else:
                        logger.warning(f'参数: {param["name"]} 中未识别的数据类型是: {type(param["data"][0])}')
                        return None
                    
        return None

    
    async def getPrompt(self, apiInfo= None):
        ''' 2024.7
            获取提示词
            @param apiInfo: 第三方语音识别的 接口
            支持自动识别客户端上传的: 字符串、txt文件、语音文件
            如果要自动识别语音文件,默认需要安装 GPT-SoVITS 模块, 或者使用 apiInfo 参数指定可以使用的第三方Bot模块
            如果要使用网络上的语音识别接口,需要仿这个函数别写代码, promptFiles[0] 是客户端上传的文件(音频)
        '''
        promptText = self.getParam() #首先尝试获取客户端上传的文字提示词
        if promptText is not None: 
            if promptText.strip() != '':
                return promptText.strip()
            else:
                return None
    
        else:
            '''
                如果没有提示词,而想用语音输入提示词,则需获取语音文件(用语音录音生成提示词, 需要要语音识别模块支持)
                可以安装另一个我打包的整合包: GPT-SoVITS,它有一个接口可以语音识别, 也可以使用在线语音接口: 百度或讯飞的接口
            '''
            promptFiles = self.getFiles()
            if promptFiles is None:
                logger.warning('客户端没有上传文字提示词, 也没有上传语音提示词!')
                return None
        
            else: 
                from aivagent.aivmedia import mediaType
                #尝试查找用户是否上传了语音文件或文本文件  
                promptFileInfo = promptFiles[0]
                # 判断文件是文本文件还是语音文件
                fileExtension = os.path.splitext(promptFileInfo['name'])[1]

                textFile = None
                if fileExtension.lower() in mediaType['audioList']: # 判断是否是音频文件        
                    
                    if apiInfo is None:
                        # 对语音文件进行识别转文字
                        # 调用第三方Bot识别, 这里是调用本机安装的 GPT-SoVITS 模块接口 WaveToText()识别。也可以跨网络调用
                        apiInfo = {
                            'agiDeviceId': None, #调用本机AGI的接口,传 None
                            'botName': 'GptSovits', # 在Aiv启动时会显示, 在 /aivc/data/config/aiv.yaml 中配置的名称
                            'botApi' : 'WaveToText' # GPT-SoVITS项目aivbot.py中声明的函数
                        }
                    
                    # 指定 GptSovits 输出的内容是'string'字符串
                    self.push( type= 'string', data= 'str', paramName= 'out',paramStr= 'paramIn') #利用原来 aivBot.task['paramIn']的参数,添加一个'string'参数
                    # paramIn = aivBot.createParamIn('string', 'str', 'out')
                    botTask = await self.startSlotTask(apiInfo, None, 10) #获取调有第三方Bot并等待返回结果

                    if botTask['result']['code'] != 200:
                        logger.warning(f'调用第三方Bot进行语音识别出错: {apiInfo}')
                        return None
                    # logger.warning(f'返回的Slot Task = {botTask}')
                    promptText = self.getParam(paramStr='paramOut', task= botTask) # 获取 GptSovits返回语音识别的文本
                
                    return promptText

                elif fileExtension.lower() in ['.txt']: #如果是文本文件,则直接使用

                    textFile = promptFileInfo['path'] # path中是下载在本机的路径

                    with open(textFile, 'r',  encoding= "utf-8") as f:
                        content = f.read()

                    promptText =''.join(content)
                    self.push('string',promptText)

                    return promptText

                else:
                    logger.warning('客户端上传的文件无法识别')
                    return None
                
                # loggeruru.warning(f'要打开的文本文件是: {textFile}')
                # 读出文本文件中的文字内容
                



    







