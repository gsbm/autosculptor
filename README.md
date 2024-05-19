<p align="center">
  <img src="assets/logo.svg" height="64px" />
</p>
<p align="center">
🟠 Generate 3D models using Gradio API directly from Blender
</p>

---

<p align="center">
  <img src="assets/example_2.png" height="300px" />
  <img src="assets/example_1.png" height="300px" />
</p>

## Get started

### Installing Autosculptor

Download latest release in [Release page](https://github.com/greenmagenta/autosculptor/releases). Then, in Blender, go to `Preferences > Addons > Install` and select `autosculptor.py`.
To activate it, check it in the Menu. If an error appear, please take a look to the following instructions.

### Installing dependencies

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

| Model | Host | Average generation time |
|---|---|---|
| [Shap-E](https://github.com/openai/shap-e) | [hysts/Shap-E](https://huggingface.co/spaces/hysts/Shap-E) | ~13s |
| [SDXL](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0) + [Shap-E](https://github.com/openai/shap-e) | [hysts/SDXL](https://huggingface.co/spaces/hysts/SDXL) + [hysts/Shap-E](https://huggingface.co/spaces/hysts/Shap-E) | ~30s |
| [SDXL](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0) + [DreamGaussian](https://github.com/dreamgaussian/dreamgaussian) | [hysts/SDXL](https://huggingface.co/spaces/hysts/SDXL) + [jiawei011/dreamgaussian](https://huggingface.co/spaces/jiawei011/dreamgaussian) | ~600s |
| [SDXL](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0) + [InstantMesh](https://github.com/TencentARC/InstantMesh) | [hysts/SDXL](https://huggingface.co/spaces/hysts/SDXL) + [TencentARC/InstantMesh](https://huggingface.co/spaces/TencentARC/InstantMesh) | ~60s |


## Implementations

Currently working on other implementations like :
- Image to Mesh option
- Adding more Text2Mesh/Image2Mesh models
- Updating displayed parameters on differents models
- Self hosting/using more stable hosted models

## License

[GPL-3.0](https://github.com/greenmagenta/autosculptor/LICENSE/) License
