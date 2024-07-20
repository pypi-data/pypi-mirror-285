'''
    2024.7
    媒体处理模块

    此模块需要ffmpeg 支持
'''
import os,sys,datetime,wave,subprocess,uuid
from loguru import logger

mediaType = {
    'picList': ['.png', '.jpeg', '.jpg', '.gif', '.bmp', '.tiff', '.ico', '.svg', '.webp'],
    'videoList': ['.mp4', '.avi', '.mkv', '.flv', '.mov', '.wmv', '.webm', '.mpeg', '.3gp', '.rmvb'],  
    'audioList' : ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.wma', '.ape', '.alac', '.ac3', '.m4a'],
    'srtList' : ['.srt', '.vtt', '.ass'], #字幕文件扩展名
}


def timeToMilliseconds(timeStr): 
    ''' 2024.7
        把字幕内容中的时间转换成毫秒
    '''
    if ',' in timeStr:
        time_obj = datetime.strptime(timeStr, '%H:%M:%S,%f') # 有些又是以这种格式："00:08:19,60" 
        milliseconds = (time_obj.hour * 3600000) + (time_obj.minute * 60000) + (time_obj.second * 1000) + (time_obj.microsecond // 1000)
        return milliseconds
    
    else:
        time_obj = datetime.strptime(timeStr, '%H:%M:%S.%f') # 有些又是以这种格式："00:08:19.60" (ffmpeg是返回这种格式)
        milliseconds = (time_obj.hour * 3600000) + (time_obj.minute * 60000) + (time_obj.second * 1000) + (time_obj.microsecond // 1000)
        return milliseconds
    

def checkWaveDuration(waveFile, forceDuration= 0): #获取音频时长
    ''' 2024.7
        这个函数只能读取标准格式的 wave 文件的时长
        像m4a这格式读不了,有些mp3 也读不了
        @param waveFile : 要读取的音频文件
        @param forceDuration : 强制截取的长度
    '''
    with wave.open(waveFile, 'rb') as audio:
        frames = audio.getnframes()
        framerate = audio.getframerate()
        duration = frames / float(framerate) * 1000

    if forceDuration>0 and  duration> forceDuration* 1000:
        outputFile =os.path.join(os.path.dirname(waveFile) , uuid.uuid4().hex + os.path.splitext(waveFile)[1])
        command = f"ffmpeg -y -i {waveFile} -ss 0 -t {forceDuration} {outputFile}"
        subprocess.call(command, shell=True)
        logger.debug(f'强制截取音频: {waveFile} {forceDuration}秒')
        os.remove(waveFile)
        os.rename(outputFile, waveFile)

    return duration