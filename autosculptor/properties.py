import bpy
from bpy.types import PropertyGroup

class GeneratorProperties(PropertyGroup):
    prompt: bpy.props.StringProperty(
        name="Prompt",
        description="The text prompt describing the 3D model to generate"
    )
    prompt_enhancer: bpy.props.BoolProperty(
        name="Prompt Enhancer",
        description="Enhance the prompt for better results",
        default=False
    )
    seed: bpy.props.IntProperty(
        name="Seed",
        description="Seed for generation",
        default=0,
        min=0,
        max=2147483647
    )
    random_seed: bpy.props.BoolProperty(
        name="Random Seed",
        description="Use a random seed for each generation",
        default=True
    )
    guidance_scale: bpy.props.IntProperty(
        name="Guidance Scale",
        description="Scale for the guidance during generation",
        default=15,
        min=1,
        max=20
    )
    num_inference_steps: bpy.props.IntProperty(
        name="Inference Steps",
        description="Number of inference steps for generation",
        default=64,
        min=2,
        max=100
    )
    image_width: bpy.props.IntProperty(
        name="Image Width",
        description="Width of the generated image",
        default=1024,
        min=256,
        max=1024
    )
    image_height: bpy.props.IntProperty(
        name="Image Height",
        description="Height of the generated image",
        default=1024,
        min=256,
        max=1024
    )
    apply_material: bpy.props.BoolProperty(
        name="Apply Material",
        description="Apply material to the generated model",
        default=True
    )
    model_type: bpy.props.EnumProperty(
        name="Model",
        description="Model pipeline to use for generation",
        items=[
            ("model-shap-e", "Shap-E", "hysts/Shap-E (~13s)"),
            ("model-sdxl-shap-e", "SDXL + Shap-E", "hysts/SDXL + hysts/Shap-E (~30s)"),
            ("model-sdxl-dreamgaussian", "SDXL + DreamGaussian", "hysts/SDXL + jiawei011/dreamgaussian (~600s)"),
            ("model-sdxl-instantmesh", "SDXL + InstantMesh", "hysts/SDXL + TencentARC/InstantMesh (~60s)"),
            ("model-sdxl-triposr", "SDXL + TripoSR", "hysts/SDXL + stabilityai/TripoSR (~30s)")
        ],
        default="model-shap-e",
        update=lambda self, context: self.update_estimated_time(context)
    )
    batch_count: bpy.props.IntProperty(
        name="Batch Count",
        description="Number of 3D models to generate",
        default=1,
        min=1,
        max=10,
        update=lambda self, context: self.update_estimated_time(context)
    )
    show_advanced: bpy.props.BoolProperty(
        name="Show Advanced Settings",
        description="Show or hide advanced settings",
        default=False
    )
    estimated_time: bpy.props.StringProperty(
        name="Estimated Time",
        description="Estimated time to generate the model",
        default=""
    )
    run_in_thread: bpy.props.BoolProperty(
        name="Run in Thread (experimental)",
        description="Run the model generation in a separate thread",
        default=False
    )

    def update_estimated_time(self, context):
        model_times = {
            "model-shap-e": 13,
            "model-sdxl-shap-e": 30,
            "model-sdxl-dreamgaussian": 600,
            "model-sdxl-instantmesh": 60,
            "model-sdxl-triposr": 30
        }
        time_per_model = model_times.get(self.model_type, 0)
        total_time = time_per_model * self.batch_count
        self.estimated_time = f"~{total_time}s"

    def init(self, context):
        self.update_estimated_time(context)