## SenseVoice-python with onnx

[SenseVoice](https://github.com/FunAudioLLM/SenseVoice)是阿里开源的多语言asr.



## 使用方式

### 安装
```bash
pip install sensevoice-onnx

# or pip from github
pip install git+https://github.com/lovemefan/SenseVoice-python.git
```

### 使用

```bash
sensevoice --audio sensevoice/resource/asr_example_zh.wav
```


第一次使用会自动从huggingface下载，如果下载不下来，可以使用镜像

* Linux:
```bash 
export HF_ENDPOINT=https://hf-mirror.com
```

* Windows Powershell
```bash
$env:HF_ENDPOINT = "https://hf-mirror.com"
* ```

或者非入侵方式使用环境变量
```bash
HF_ENDPOINT=https://hf-mirror.com sensevoice --audio sensevoice/resource/asr_example_zh.wav
```



```
Sense Voice 脚本参数设置

optional arguments:
  -h, --help            show this help message and exit
  -a , --audio_file 设置音频路径
  -dp , --download_path 自定义模型下载路径，默认`sensevoice/resource`
  -d , --device, 使用cpu时为-1，使用gpu（需要安装onnxruntime-gpu）时指定卡号 默认`-1`
                        Device
  -n , --num_threads , 线程数, 默认 `4`
                        Num threads
  -l , --language {auto,zh,en,yue,ja,ko,nospeech} 语音代码，默认`auto`
  --use_itn             是否使用itn
  --use_int8            是否使用int8 量化的onnx模型

```

### 结果


```bash
2024-07-19 14:16:41,522 INFO [sense_voice_ort_session.py:130] Loading model from /Users/cenglingfan/Code/python-project/SenseVoice-python/sensevoice/resource/embedding.npy
2024-07-19 14:16:41,525 INFO [sense_voice_ort_session.py:133] Loading model /Users/cenglingfan/Code/python-project/SenseVoice-python/sensevoice/resource/sense-voice-encoder.onnx
2024-07-19 14:16:43,994 INFO [sense_voice_ort_session.py:140] Loading /Users/cenglingfan/Code/python-project/SenseVoice-python/sensevoice/resource/embedding.npy takes 2.47 seconds
2024-07-19 14:16:44,031 INFO [sense_voice.py:76] Audio resource/asr_example_zh.wav is 5.58 seconds
2024-07-19 14:16:44,253 INFO [sense_voice.py:81] <|zh|><|NEUTRAL|><|Speech|><|woitn|>欢迎大家来体验达摩院推出的语音识别模型
2024-07-19 14:16:44,253 INFO [sense_voice.py:83] Decoder audio takes 0.22162580490112305 seconds
2024-07-19 14:16:44,253 INFO [sense_voice.py:84] The RTF is 0.03971788618299696.

```
