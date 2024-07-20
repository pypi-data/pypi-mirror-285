'''
初始化Aiv应用全局参数
* 全局路径、Logger、环境变量等设置
* 无论是AivC、Aiv Bot模块,都可以使用
* _aivAppInit() 函数必须早于任何模块调用,在任何 import 之前调用,否则有可能路径失效,
报找不到模块,或import错误. (2023.8)
* loguru的日志级别名称: 'DEBUG','INFO','SUCCESS','WARNING','ERROR','CRITICAL'
'''
import os,sys

def _aivAppInit(exe_file :str, isMain=False, loglevel= 'INFO'):
    ''' 2023.8
    ### 注册Aiv app的模块 
    * 参数:
        exe_file : 是主模块路径
        isMain : 是否是bot模块,如果是bot模块,将被以子进程加载,bot模块的工作目录会被设为 bot上级目录。
                原因是bot上级目录里,包含有公共的python模块以及其它公共的数据文件夹(如mode,data,bin目录)
                如果bot模块要使用自己的自定义包,则可以复制到bot模块目录下(比如cv2模块)
        loglevel : 可选值 'DEBUG','INFO','SUCCESS','WARNING','ERROR','CRITICAL'
    * 此函数在其它代码前(在 import 前运行)
    * 设置路径/环境变量/日志等级等
    * 强制设置工作路径为当前执行程序的上一级目录
    * loglevel的设置只影响控制台输出的日志级别,与aivbot.py的run()的setLogFile()控制写入日志文件的级别不同.
    '''
    LOCAL_PATH = os.path.dirname(os.path.abspath(exe_file))

    #bot模块的工作目录会被设为 bot上级目录。原因是bot上级目录里,包含有公共的python模块以及其它公共的数据
    if isMain:
        os.chdir(os.path.join(LOCAL_PATH, '..')) #设置当前目录为执行文件的上级目录

    sys.path.insert(0,LOCAL_PATH)  #如果是bot程序,一定要把执行程序所在的目录添加到 path中 2024.3

    #初始化导入包目录（系统包、用户自定义包）--------------
    # 指定"lib"目录作为的 python 系统库目录(Aiv系统包库), import 搜索的目录
    sys.path.insert(0,'lib')     

    #把执行文件所在的文件夹也加入sys.path，目的是执行文件可以优先从本目录下导入包（优先于AIV系统指定的包）
    # sys.path.insert(0,os.path.basename(LOCAL_PATH)) #插入 sys.path 的顺序不能调换
    #---------------------------------------------------
    # 如果目录下有 venv 目录,则把 venv/Lib/site-packages 加入 搜索路径
    currPath = os.getcwd()
    
    if os.path.exists(os.path.join(currPath,'venv')):
        sys.path.insert(0, os.path.join(currPath,'venv/Lib/site-packages')) #添加到第一位

        # 把当前目录下的 venv/Scripts/ 目录添加到环境路径(与sys.path不一样,sys.path是python的搜索路径, os.getenv('PATH')是可执行程序、dll的搜索路径)
        envPath = os.getenv("PATH")
        scriptsPath = os.path.join(currPath,'venv/Scripts/')
        if scriptsPath not in envPath:
            os.environ["PATH"] = envPath + os.pathsep + scriptsPath

    # 解决导入  cv2 时的问题-----------------------------
    import site
    site.USER_SITE = os.path.join(os.getcwd(),'lib')
    site.USER_BASE = os.path.join(os.getcwd(),'Scripts') #可以创建，用于存放脚本
    #--------------------------------------------------

    # windows下临时添加路径到系统的 Path 变量中----------------
    #这是为了 动态载入  *.pyd *.so *.dll 文件的路径 ，linux 为 os.environ['LD_LIBRARY_PATH'] site.USER_BASE
    binpath = os.path.join(site.USER_SITE,'bin')
    if not 'PATH' in os.environ:
        os.environ['PATH'] = binpath + ";"
    else :
        os.environ['PATH'] = binpath + ";"+ os.environ['PATH']

    #设置 PythonPath 路径-----------------------------------
    # os.environ['PYTHONPATH'] = '' #设为空，则是屏蔽系统设置的 PYTHONPATH (如果有的话)
    #-------------------------------------------------------
    from loguru import logger #必须要等上面的路径添加到python的path才能初始化loguru,不然会显示找不到loguru路径 2024.2
    if loglevel != 'DEBUG': #非调试模式下,显示的信息相对简单(不显示代码文件和信息显示的代码行) 2024.3
        logger.remove() #删除默认的处理日志对hander,下面用 logger.add()重新配置 (colorize=True让各种信息按各自默认颜色显示,但要用<level></level>包裹)
        # 可以用 <cyan>{file}</cyan>:<cyan>{line}</cyan> 控制是否显示代码行
        logger.add(sys.stdout, format="[ {time:YYYY-MM-DD HH:mm:ss} {level} ] <level>{message}</level>", filter="",colorize=True, level= loglevel)
        # 2024.3经测试,在不同的进程中(比如bot子进程),各自设置logger是互不干扰的。在主程序中可以设置为 INFO,
        # 而在bot模块中,同样可以使用_aivAppInit()设置为 DEBUG,在同一个控制台窗口下,互不影响。

    if isMain and loglevel == 'DEBUG':
        logger.warning('AIV初始化成功! 已开启 DEBUG 模式')
    else:
        logger.debug('AIV初始化成功! 程序路径是: {}'.format(currPath))

if __name__ == "__main__":
    _aivAppInit(__file__) # test

