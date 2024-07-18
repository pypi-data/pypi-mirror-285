# ezdl
### just another yt-dlp wrapper for even more simplicity with rich styling and loading animations.

![](https://i.imgur.com/HHTUNv5.png)

### Dependencies
[Python](https://www.python.org/downloads/)

<details>
<summary> 
more deps</summary> 

- pip dependencies (these will be installed automatically)
```python
toml, rich, yt-dlp
```
- install or upgrade the dependencies seperate from ezdl
```python
pip install --upgarde toml rich yt-dlp
```


</details>

## Installation

You can install ezdl using pip:

```pwsh
pip install --upgrade nrdrch-ezdl
```

## usage examples:
- Help pages:
```pwsh
ezdl --help or -h
```
- Display a Helpful Table für Configuration

```pwsh
ezdl --help-settings or -hs
```
- Download a Youtube video (this will Ignore the rest of the playlist by default)
```pwsh
ezdl video https://youtu.be/dQw4w9WgXcQ
```
- just the audio
```pwsh
ezdl audio https://youtu.be/dQw4w9WgXcQ
```
- Download the whole playlist if the link leads to a playlist
```pwsh
ezdl video https://youtu.be/dQw4w9WgXcQ?list=PLE0hg-LdSfycrpTtMImPSqFLle4yYNzWD wp
```
- just the audio but the whole playlist
```pwsh
ezdl audio https://youtu.be/dQw4w9WgXcQ?list=PLE0hg-LdSfycrpTtMImPSqFLle4yYNzWD wp
```
- open locations by their name (settings, audio or video)
```pwsh
ezdl open settings
```
