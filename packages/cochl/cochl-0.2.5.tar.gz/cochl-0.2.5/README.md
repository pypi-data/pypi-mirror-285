# cochl-sense-py

`cochl-sense-py` is a Python client library providing easy integration of Cochl.Sense API into any Python application.

Cochl.Sense API offers two types of audio inference: [File](#file-usage) and [Stream](#stream-usage). \
You can upload a file (MP3, WAV, OGG) or raw PCM audio stream. 

<br/>

## Installation

`cochl-sense-py` can be installed and used in Python 3.8+.

```python
pip install --upgrade cochl
```

<br/>

## File Usage

This simple setup is enough to input your file. API project key can be retrieved from [Cochl Dashboard](https://dashboard.cochl.ai/).

```python
import cochl.sense as sense

client = sense.FileClient("YOUR_API_PROJECT_KEY")

results = client.predict("your_file.wav")
print(results.to_dict())  # get results as a dict
```

<br/>

You can adjust the custom settings like below. For more details please refer to [Advanced Cconfigurations](#advanced-configurations).
```python
import cochl.sense as sense

api_config = sense.APIConfig(
    window_hop=sense.WindowHop.HOP_1s,
    sensitivity=sense.SensitivityConfig(
        default=sense.SensitivityScale.LOW,
        by_tags={
            "Baby_cry": sense.SensitivityScale.VERY_LOW,
            "Gunshot":  sense.SensitivityScale.HIGH,
        },
    ),
)

client = sense.FileClient(
    "YOUR_API_PROJECT_KEY",
    api_config=api_config,
)

results = client.predict("your_file.wav")
print(results.to_dict())  # get results as a dict
```

<br/>

The file prediction result can be displayed in a summarized format. More details at [Summarized Result](#summarzied-result).
```python
# print(results.to_dict())  # get results as a dict

print(results.to_summarized_result(
    interval_margin=2,
    by_tags={"Baby_cry": 5, "Gunshot": 3}
))  # get results in a simplified format

# At 0.0-1.0s, [Baby_cry] was detected
```

<br/>

Cochl.Sense API supports three file formats: MP3, WAV, OGG. \
If a file is not in a supported format, it has to be manually converted. More details [here](#convert-to-supported-file-formats-wav-mp3-ogg).


<br/>

## Stream Usage

Any raw PCM audio stream data can be predicted like below. API project key can be retrieved from [Cochl Dashboard](https://dashboard.cochl.ai/).


[stream_sample.py](./samples/stream_sample.py) shows more detailed example using `PyAudio`.

```python
import cochl.sense as sense

# when audio is sampled in 22,050Hz and each sample is in f32le
SENSE_DATA_TYPE = sense.AudioDataType.F32
SENSE_ENDIAN = sense.AudioEndian.LITTLE
SAMPLE_RATE = 22050

audio_type = sense.StreamAudioType(
    data_type=SENSE_DATA_TYPE,
    endian=SENSE_ENDIAN,
    sample_rate=SAMPLE_RATE,
)
client = sense.StreamClient(
    "YOUR_API_PROJECT_KEY",
    audio_type=audio_type,
)

# put `bytes` type data into StreamBuffer
# and it returns predictable audio window when pop()
buffer = client.get_buffer()
your_audio_stream_data = ...  # `bytes` type data
buffer.put(your_audio_stream_data)
if buffer.is_ready():
    audio_window = buffer.pop()
    result = client.predict(audio_window)
    print(result)
```

<br/>

(Note) The result of stream feature does not support summarized format because it outputs its result in real-time.

<br/>
<br/>

## Advanced Configurations

### Window Hop

Cochl.Sense analyzes audio data in "window" unit, which is a block of 1 second audio data.
Window hop represents the timely gap between windows, meaning frequency of inference in seconds.

For example, audio windows are like below when window hop is 0.5s.
- Window #0 (0.0s ~ 1.0s)
- Window #1 (0.5s ~ 1.5s)
- Window #2 (1.0s ~ 2.0s)

When window hop is 1.0s, audio windows are like below.
- Window #0 (0.0s ~ 1.0s)
- Window #1 (1.0s ~ 2.0s)
- Window #2 (2.0s ~ 3.0s)

The window hop is adjusted with `WindowHop` Enum.
  - `HOP_500ms` (default)
  - `HOP_1s`

```python
import cochl.sense as sense

api_config = sense.APIConfig(
    window_hop=sense.WindowHop.HOP_1s,  # or sense.WindowHop.HOP_500ms
)
client = sense.FileClient(
    "YOUR_API_PROJECT_KEY",
    api_config=api_config,
)
```

<br/>

### Sensitivity

Detection sensitivity can be adjusted for all tags or each tag individually. \
If you feel that tags are not detected well enough, increase sensitivities. If there are too many false detections, lower sensitivities.

The sensitivity is adjusted with `SensitivityScale` Enum.
  - `VERY_HIGH`
  - `HIGH`
  - `MEDIUM` (default)
  - `LOW`
  - `VERY_LOW`

```python
import cochl.sense as sense

api_config = sense.APIConfig(
    sensitivity=sense.SensitivityConfig(
        # default sensitivity applied to all tags not specified in `by_tags`
        default=sense.SensitivityScale.LOW,
        by_tags={
            "Baby_cry": sense.SensitivityScale.VERY_LOW,
            "Gunshot":  sense.SensitivityScale.HIGH,
        },
    ),
)
client = sense.FileClient(
    "YOUR_API_PROJECT_KEY",
    api_config=api_config,
)
```

<br/>
<br/>

## Other notes

### Convert to supported file formats (WAV, MP3, OGG)

`Pydub` is one of the easy ways to convert audio file into a supported format (WAV, MP3, OGG).

First install Pydub refering to this [link](https://github.com/jiaaro/pydub?tab=readme-ov-file#installation). \
Then write a Python script converting your file into a supported format like below.

```python
from pydub import AudioSegment

mp4_version = AudioSegment.from_file("sample.mp4", "mp4")
mp4_version.export("sample.mp3", format="mp3")
```

For more details of `Pydub`, please refer to this [link](https://github.com/jiaaro/pydub).

<br/>

### Summarzied Result
You can summarize the file prediction result by aggregating consecutive windows, returning the time and length of the detected tag. \
The 'interval margin' is a parameter that treats the unrecognized window between tags as part of the recognized ones and it affects all sound tags.
If you want to specify a different interval margin for specific sound tags, you can use the 'by_tags' option.

```python
print(results.to_summarized_result(
    interval_margin=2,
    by_tags={"Baby_cry": 5, "Gunshot": 3}
))

# At 0.0-1.0s, [Baby_cry] was detected
```

<br/>

### Links

Documentation: https://docs.cochl.ai/sense/api/
