# Autosculptor
🟠 A Blender addon powered by Gradio API to generate 3D models

## Installation

### Clone the repository

ALternatively, you can download the repository.

```bash
$ git clone https://github.com/greenmagenta/autosculptor.git
```

### Install the addon

Go to Preferences > Addons > Install and select `autosculptor.py`.

### Install Gradio module

This addon a use third-party Gradio Python module. To install Gradio module please refer to the following protocol to avoid any error.

In Blender [Python console](https://docs.blender.org/manual/en/latest/editors/python_console.html):
```py
>>> import sys
>>> sys.exec_prefix
'/path/to/blender/python'
```
Then in a shell (running as administrator on Windows):
```bash
# change the working directory to Blender python bin path
$ cd /path/to/blender/python/bin

# check if pip is installed
$ ./python -m ensurepip

# install Gradio module
$ ./python -m pip install gradio_client
```
If you still have trouble installing Gradio to Blender python, please check [this StackExchange thread](https://blender.stackexchange.com/questions/5287/using-3rd-party-python-modules).

## Available models

| Model | Host | Prompt type |
|---|---|---|
| [Shap-E](https://github.com/openai/shap-e) | [hysts/Shap-E](https://huggingface.co/spaces/hysts/Shap-E) | Text |

## Implementations

Currently working on other implementations like :
- Image to Mesh option
- Adding more Text2Mesh/Image2Mesh models

## License

[GPL-3.0](https://github.com/greenmagenta/autosculptor/LICENSE/) License
