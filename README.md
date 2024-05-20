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

### Installing development version

For latest features not yet implemented in stable version, you can download the development version available in [Development Branch](https://github.com/greenmagenta/autosculptor/tree/development). Please note that the stability of these versions cannot be guaranteed.

## Available models

| Model | Host | Average generation time |
|---|---|---|
| [Shap-E](https://github.com/openai/shap-e) | [hysts/Shap-E](https://huggingface.co/spaces/hysts/Shap-E) | ~13s |
| [SDXL](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0) + [Shap-E](https://github.com/openai/shap-e) | [ByteDance/Hyper-SDXL-1Step-T2I](https://huggingface.co/spaces/ByteDance/Hyper-SDXL-1Step-T2I) + [hysts/Shap-E](https://huggingface.co/spaces/hysts/Shap-E) | ~30s |
| [SDXL](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0) + [DreamGaussian](https://github.com/dreamgaussian/dreamgaussian) | [ByteDance/Hyper-SDXL-1Step-T2I](https://huggingface.co/spaces/ByteDance/Hyper-SDXL-1Step-T2I) + [jiawei011/dreamgaussian](https://huggingface.co/spaces/jiawei011/dreamgaussian) | ~600s |
| [SDXL](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0) + [InstantMesh](https://github.com/TencentARC/InstantMesh) | [ByteDance/Hyper-SDXL-1Step-T2I](https://huggingface.co/spaces/ByteDance/Hyper-SDXL-1Step-T2I) + [TencentARC/InstantMesh](https://huggingface.co/spaces/TencentARC/InstantMesh) | ~60s |

### Examples

| Shap-E | SDXL + Shape-E | SDXL + DreamGaussian | SDXL + InstantMesh |
|---|---|---|---|
| <img src="assets/model_shape-e.jpg" height="200px" /> | <img src="assets/model_sdxl-shape-e.jpg" height="200px" /> | <img src="assets/model_sdxl-dreamgaussian.jpg" height="200px" /> | <img src="assets/model_sdxl-instantmesh.jpg" height="200px" /> |
| A pinguin, 3d model ||||
| <img src="assets/model_shape-e_2.jpg" height="200px" /> | <img src="assets/model_sdxl-shape-e_2.jpg" height="200px" /> | <img src="assets/model_sdxl-dreamgaussian_2.jpg" height="200px" /> | <img src="assets/model_sdxl-instantmesh_2.jpg" height="200px" /> |
| A hamburger, 3d model ||||

### Prompt Enhancer

Prompt enhancer requests [gustavosta-magicprompt-stable-diffusion](https://gustavosta-magicprompt-stable-diffusion.hf.space/api/predict) for generating a extended prompt more adapted to 3D model generation.

| Prompt | Standard (SDXL + InstantMesh) | Prompt Enhanced (SDXL + InstantMesh) |
|---|---|---|
| A orange cat | <img src="assets/not_pe_1.jpg" height="200px" /> | <img src="assets/pe_1.jpg" height="200px" /> |
| A orange cat, photorealistic | <img src="assets/not_pe_2.jpg" height="200px" /> | <img src="assets/pe_2.jpg" height="200px" /> |

## Implementations

Currently working on other implementations like :
- Image to Mesh option
- Adding more Text2Mesh/Image2Mesh models
- Updating displayed parameters on differents models
- Self hosting/using more stable hosted models

## License

This project is licensed under [GPL-3.0](https://github.com/greenmagenta/autosculptor/LICENSE/) License.

### Warning

Before using this addon, please be aware that different models used in this project may have their own specific licenses and usage terms. It is your responsibility to review and comply with the licenses of each model to ensure that your use case is permitted. Failure to do so may result in legal consequences. Always verify the licensing terms of the models you intend to use.
