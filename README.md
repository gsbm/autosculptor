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

### Installation
Download latest release in [releases page](https://github.com/greenmagenta/autosculptor/releases). Then, in Blender, go to `Preferences > Add-ons > Install` and select `autosculptor.py`. To activate it, check it in the add-on list.

This add-on integrate a built-in dependencies installer. At first use, it will ask the user the consent to install complementary dependencies. This step will require internet to download and install required packages. In case of error, or for manual dependencies installation, please refer to [troubleshooting dependencies](#dependencies) section.

### Usage

After installation, Autosculptor is available in Blender on `View3D > Sidebar > Autosculptor`. Please note that this add-on require internet to execute API requests.

### Features

This add-on includes:
- ⚙️ **Multiples Models**: Access different model pipelines for 3D model generation.
- ✨ **Prompt Enhancer**: Enhance the prompt for better results adapted to 3D generation.
- 🏭 **Batch Generation**: Generate multiples differents models in a row (if random seed enabled).

## Troubleshooting

### Dependencies

This addon the use third-party Gradio Python module. If a dependency error still occurs after complete installation, please try to reinstall Gradio module.

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

# uninstall Gradio module (if applicable)
$ ./python -m pip uninstall gradio_client

# install Gradio module
$ ./python -m pip install gradio_client
```
If you still have trouble installing Gradio to Blender python, please check [this StackExchange thread](https://blender.stackexchange.com/questions/5287/using-3rd-party-python-modules).

## Available models

| Model pipeline | API Host(s) | Average generation time |
|---|---|---|
| [Shap-E](https://github.com/openai/shap-e) | [hysts/Shap-E](https://huggingface.co/spaces/hysts/Shap-E) | ~13s |
| [SDXL](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0) + [Shap-E](https://github.com/openai/shap-e) | [hysts/SDXL](https://huggingface.co/spaces/hysts/SDXL) + [hysts/Shap-E](https://huggingface.co/spaces/hysts/Shap-E) | ~30s |
| [SDXL](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0) + [DreamGaussian](https://github.com/dreamgaussian/dreamgaussian) | [hysts/SDXL](https://huggingface.co/spaces/hysts/SDXL) + [jiawei011/dreamgaussian](https://huggingface.co/spaces/jiawei011/dreamgaussian) | ~600s |
| [SDXL](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0) + [InstantMesh](https://github.com/TencentARC/InstantMesh) | [hysts/SDXL](https://huggingface.co/spaces/hysts/SDXL) + [TencentARC/InstantMesh](https://huggingface.co/spaces/TencentARC/InstantMesh) | ~60s |
| [SDXL](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0) + [TripoSR](https://github.com/VAST-AI-Research/TripoSR) | [hysts/SDXL](https://huggingface.co/spaces/hysts/SDXL) + [stabilityai/TripoSR](https://huggingface.co/spaces/stabilityai/TripoSR) | ~30s |

### Examples

| Shap-E | SDXL +<br>Shape-E | SDXL +<br>DreamGaussian | SDXL +<br>InstantMesh | SDXL +<br>TripoSR |
|---|---|---|---|---|
| <img src="assets/model_shape-e.jpg" width="150px" /> | <img src="assets/model_sdxl-shape-e.jpg" width="150px" /> | <img src="assets/model_sdxl-dreamgaussian.jpg" width="150px" /> | <img src="assets/model_sdxl-instantmesh.jpg" width="150px" /> | <img src="assets/model_sdxl-triposr.jpg" width="150px" /> |
| `A pinguin, 3d model` |||||
| <img src="assets/model_shape-e_2.jpg" width="150px" /> | <img src="assets/model_sdxl-shape-e_2.jpg" width="150px" /> | <img src="assets/model_sdxl-dreamgaussian_2.jpg" width="150px" /> | <img src="assets/model_sdxl-instantmesh_2.jpg" width="150px" /> | <img src="assets/model_sdxl-triposr_2.jpg" width="150px" /> |
| `A hamburger, 3d model` |||||

### Prompt Enhancer

Prompt enhancer requests [gustavosta/magicprompt-stable-diffusion](https://gustavosta-magicprompt-stable-diffusion.hf.space/) for generating an extended prompt more adapted to 3D model generation.

| Prompt | Standard<br>(SDXL + InstantMesh) | Prompt Enhanced<br>(SDXL + InstantMesh) |
|---|---|---|
| `A orange cat` | <img src="assets/not_pe_1.jpg" width="200px" /> | <img src="assets/pe_1.jpg" width="200px" /> |
| `A orange cat, photorealistic` | <img src="assets/not_pe_2.jpg" width="200px" /> | <img src="assets/pe_2.jpg" width="200px" /> |

## Implementations

Currently working on other implementations like :
- Adding image to Mesh option
- Adding more Text2Mesh/Image2Mesh models
- Updating displayed parameters on differents models
- Thinking about self hosting/using more stable hosted models
- Adding preset system

## License

This project is licensed under [GPL-3.0](https://github.com/greenmagenta/autosculptor/LICENSE/) License.

### Warning

Before using this addon, please be aware that different models used in this project may have their own specific licenses and usage terms. It is your responsibility to review and comply with the licenses of each model to ensure that your use case is permitted. Failure to do so may result in legal consequences. Always verify the licensing terms of the models you intend to use. This program is provided for educational and experimental purposes.
