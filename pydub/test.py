import wave
# import PyAudio


def play():
    chunk=1024  #2014kb
    wf=wave.open(r"11.wav",'rb')
    p=PyAudio()
    stream=p.open(format=p.get_format_from_width(wf.getsampwidth()),channels=wf.getnchannels(),rate=wf.getframerate(),output=True)
 
    data = wf.readframes(chunk)  # 读取数据
    print(data)
    while data != '':  # 播放  
        stream.write(data)
        data = wf.readframes(chunk)
        print('while循环中！')
        print(data)
    stream.stop_stream()   # 停止数据流
    stream.close()
    p.terminate()  # 关闭 PyAudio
    print('play函数结束！')

play()
