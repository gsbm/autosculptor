import bpy
import sys
import subprocess
import random
import threading
from bpy.app.handlers import persistent

# Blender add-on information
bl_info = {
    "name": "Autosculptor 3D Model Generator",
    "author": "Greenmagenta",
    "version": (1, 6, 0),
    "blender": (2, 80, 0),
    "category": "Add Mesh",
    "description": "Generate 3D models using generative models.",
    "warning": "Requires installation of dependencies",
    "location": "View3D > Sidebar > Autosculptor",
    "support": "COMMUNITY",
    "doc_url": "https://github.com/greenmagenta/autosculptor",
    "tracker_url": "https://github.com/greenmagenta/autosculptor/issues",
    "isDraft": False
}

# Check if gradio_client is installed
def ensure_gradio_installed():
    try:
        import gradio_client
        return True
    except ImportError:
        return False

# Install gradio_client using pip
def install_gradio():
    python_executable = sys.executable
    subprocess.check_call([python_executable, '-m', 'ensurepip'])
    subprocess.check_call([python_executable, '-m', 'pip', 'install', 'gradio_client'])

class InstallDependenciesOperator(bpy.types.Operator):
    bl_idname = "wm.install_dependencies"
    bl_label = "Install Dependencies"
    
    def execute(self, context):
        install_gradio()
        self.report({'INFO'}, "Dependencies installed successfully. Please restart Blender.")
        return {'FINISHED'}

class GeneratorOperator(bpy.types.Operator):
    bl_idname = "object.autosculptor_model_generator"
    bl_label = "Generate 3D Model"
    bl_description = "Generate a 3D model based on the provided prompt and settings"
    bl_options = {'REGISTER', 'UNDO'}
    
    generating = False

    def execute(self, context):
        if GeneratorOperator.generating:
            self.report({'WARNING'}, "A model is already being generated.")
            return {'CANCELLED'}

        if not ensure_gradio_installed():
            self.report({'ERROR'}, "gradio_client is not installed.")
            return {'CANCELLED'}

        # Import properties from context
        autosculptor_props = context.scene.autosculptor_props

        if autosculptor_props.run_in_thread:
            thread = threading.Thread(target=self.run_pipeline, args=(autosculptor_props,))
            thread.start()
            GeneratorOperator.generating = True
            bpy.context.window_manager.progress_begin(0, 100)
            bpy.app.timers.register(self.check_thread, first_interval=0.1)
        else:
            self.run_pipeline(autosculptor_props)

        return {'FINISHED'}

    def check_thread(self):
        if not GeneratorOperator.generating:
            bpy.context.window_manager.progress_end()
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
            return None
        return 0.1

    def run_pipeline(self, autosculptor_props):
        # Get properties from user input
        prompt = autosculptor_props.prompt
        if autosculptor_props.prompt_enhancer:
            prompt = self.enhance_prompt(prompt)
        guidance_scale = autosculptor_props.guidance_scale
        num_inference_steps = autosculptor_props.num_inference_steps
        model_type = autosculptor_props.model_type
        batch_count = autosculptor_props.batch_count
        image_width = autosculptor_props.image_width
        image_height = autosculptor_props.image_height

        for _ in range(batch_count):
            # Get seed for generation
            seed = autosculptor_props.seed
            if autosculptor_props.random_seed:
                seed = random.randint(0, 2147483647)

            # Generate the 3D model
            model_path = self.generate_model(prompt, seed, guidance_scale, num_inference_steps, model_type, image_width, image_height)
            
            # Handle errors in model generation
            if not model_path:
                self.report({'ERROR'}, "Invalid model type.")
                GeneratorOperator.generating = False
                return

            bpy.app.timers.register(lambda: self.import_generated_model(model_path, autosculptor_props.apply_material), first_interval=0.1)

        GeneratorOperator.generating = False

    def import_generated_model(self, model_path, apply_material):
        # Import the generated model into Blender
        bpy.ops.import_scene.gltf(filepath=model_path)
        
        # Check if any object was imported
        if not bpy.context.selected_objects:
            self.report({'ERROR'}, "No object was imported.")
            return

        # Get the imported object
        parent_obj = bpy.context.selected_objects[0]
        obj = next((child for child in parent_obj.children if child.type == 'MESH'), None)
        
        # Handle errors in finding a mesh object
        if obj is None:
            self.report({'ERROR'}, "No mesh object found among imported children.")
            return
        
        # Assign material to the imported object
        if apply_material:
            self.assign_material(obj)

    # Function to call the prompt enhancer API
    def enhance_prompt(self, prompt):
        import requests
        response = requests.post(
            "https://gustavosta-magicprompt-stable-diffusion.hf.space/api/predict",
            json={"data": [prompt + ", 3d model"]}
        )
        if response.status_code == 200:
            enhanced_prompt = response.json().get('data', [None])[0]
            if (enhanced_prompt):
                return enhanced_prompt.split("\n")[0]
        return prompt

    # Function to generate the model based on the type
    def generate_model(self, prompt, seed, guidance_scale, num_inference_steps, model_type, image_width, image_height):
        from gradio_client import Client, file

        try:
            if model_type == "model-shap-e":
                return self.generate_shape_e_model(prompt, seed, guidance_scale, num_inference_steps)
            elif model_type == "model-sdxl-shap-e":
                return self.generate_sdxl_shape_e_model(prompt, seed, guidance_scale, num_inference_steps, image_width, image_height)
            elif model_type == "model-sdxl-dreamgaussian":
                return self.generate_sdxl_dreamgaussian_model(prompt, seed, guidance_scale, num_inference_steps, image_width, image_height)
            elif model_type == "model-sdxl-instantmesh":
                return self.generate_sdxl_instantmesh_model(prompt, seed, guidance_scale, num_inference_steps, image_width, image_height)
            elif model_type == "model-sdxl-triposr":
                return self.generate_sdxl_triposr_model(prompt, seed, guidance_scale, num_inference_steps, image_width, image_height)
        except Exception as e:
            self.report({'ERROR'}, f"An error occurred: {str(e)}. This could be due to a model hosting issue or an internet connection problem.")
            return None

    # Function to generate Shap-E model
    def generate_shape_e_model(self, prompt, seed, guidance_scale, num_inference_steps):
        from gradio_client import Client
        client = Client("hysts/Shap-E")
        result = client.predict(
            prompt=prompt,
            seed=seed,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            api_name="/text-to-3d"
        )
        return result

    # Function to generate SDXL + Shap-E model
    def generate_sdxl_shape_e_model(self, prompt, seed, guidance_scale, num_inference_steps, image_width, image_height):
        from gradio_client import Client, file
        client1 = Client("hysts/SDXL")
        image = client1.predict(
            prompt=prompt,
            negative_prompt="",
            prompt_2="",
            negative_prompt_2="",
            seed=seed,
            guidance_scale_base=guidance_scale,
            num_inference_steps_base=num_inference_steps,
            width=image_width,
            height=image_height,
            api_name="/run"
        )
        image_path = image

        client2 = Client("https://one-2-3-45-one-2-3-45.hf.space/")
        segmented_img_filepath = client2.predict(
            image_path,
            api_name="/preprocess"
            )

        client3 = Client("hysts/Shap-E")
        result = client3.predict(
            image=file(segmented_img_filepath),
            seed=seed,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            api_name="/image-to-3d"
        )
        return result

    # Function to generate SDXL + DreamGaussian model
    def generate_sdxl_dreamgaussian_model(self, prompt, seed, guidance_scale, num_inference_steps, image_width, image_height):
        from gradio_client import Client, file
        client1 = Client("hysts/SDXL")
        image = client1.predict(
            prompt=prompt,
            negative_prompt="",
            prompt_2="",
            negative_prompt_2="",
            seed=seed,
            guidance_scale_base=guidance_scale,
            num_inference_steps_base=num_inference_steps,
            width=image_width,
            height=image_height,
            api_name="/run"
        )
        image_path = image

        client2 = Client("https://one-2-3-45-one-2-3-45.hf.space/")
        elevation_angle_deg = client2.predict(
            image_path,
            True,
            api_name="/estimate_elevation"
            )

        if elevation_angle_deg < -90 or elevation_angle_deg > 90:
            elevation_angle_deg = 0

        client3 = Client("https://jiawei011-dreamgaussian.hf.space/--replicas/94pz9/")
        result = client3.predict(
            image_path,
            True, 
            elevation_angle_deg,
            fn_index=2
        )
        return result

    # Function to generate SDXL + InstantMesh model
    def generate_sdxl_instantmesh_model(self, prompt, seed, guidance_scale, num_inference_steps, image_width, image_height):
        from gradio_client import Client, file
        client1 = Client("hysts/SDXL")
        image = client1.predict(
            prompt=prompt,
            negative_prompt="",
            prompt_2="",
            negative_prompt_2="",
            seed=seed,
            guidance_scale_base=guidance_scale,
            num_inference_steps_base=num_inference_steps,
            width=image_width,
            height=image_height,
            api_name="/run"
        )
        image_path = image

        client2 = Client("TencentARC/InstantMesh")
        processed_image = client2.predict(
            input_image=file(image_path),
            do_remove_background=True,
            api_name="/preprocess"
        )

        mvs = client2.predict(
            input_image=file(processed_image),
            sample_steps=num_inference_steps,
            sample_seed=seed,
            api_name="/generate_mvs"
        )

        result = client2.predict(
            api_name="/make3d"
        )
        return result[1]
    
    # Function to generate SDXL + TripoSR model
    def generate_sdxl_triposr_model(self, prompt, seed, guidance_scale, num_inference_steps, image_width, image_height):
        from gradio_client import Client, file
        client1 = Client("hysts/SDXL")
        image = client1.predict(
            prompt=prompt,
            negative_prompt="",
            prompt_2="",
            negative_prompt_2="",
            seed=seed,
            guidance_scale_base=guidance_scale,
            num_inference_steps_base=num_inference_steps,
            width=image_width,
            height=image_height,
            api_name="/run"
        )
        image_path = image

        client2 = Client("stabilityai/TripoSR")
        processed_image = client2.predict(
            file(image_path),
            True,
            0.5,
            api_name="/preprocess"
        )
        
        result = client2.predict(
            file(processed_image),
            320,
            api_name="/generate"
        )

        return result[1]

    # Function to assign material to the imported object
    def assign_material(self, obj):
        material = bpy.data.materials.new(name="ImportedMaterial")
        material.use_nodes = True

        # Find or create a Principled BSDF shader node
        bsdf = next((node for node in material.node_tree.nodes if isinstance(node, bpy.types.ShaderNodeBsdfPrincipled)), None)
        if not bsdf:
            bsdf = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')

        # Create and configure a Vertex Color node
        attribute_node = material.node_tree.nodes.new('ShaderNodeVertexColor')
        if obj.data.vertex_colors:
            attribute_node.layer_name = obj.data.vertex_colors[0].name
        else:
            attribute_node.layer_name = "Color"

        # Link the Vertex Color node to the BSDF node
        material.node_tree.links.new(attribute_node.outputs['Color'], bsdf.inputs['Base Color'])

        # Assign the material to the object
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)

# UI Panel for the add-on
class GeneratorPanel(bpy.types.Panel):
    bl_label = "Autosculptor"
    bl_idname = "OBJECT_PT_autosculptor_model_generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Autosculptor'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        autosculptor_props = scene.autosculptor_props

        if not ensure_gradio_installed():
            layout.label(text="Dependencies are not installed.", icon='ERROR')
            layout.operator("wm.install_dependencies")
        else:
            # Add main properties to the UI
            layout.prop(autosculptor_props, "prompt")
            layout.prop(autosculptor_props, "model_type")

            # Create a collapsible section for advanced settings
            box = layout.box()
            box.prop(autosculptor_props, "show_advanced", text="Advanced Settings", emboss=False, icon='TRIA_DOWN' if autosculptor_props.show_advanced else 'TRIA_RIGHT')
            
            if autosculptor_props.show_advanced:
                box.prop(autosculptor_props, "prompt_enhancer")
                box.prop(autosculptor_props, "apply_material")

                row = box.row()
                row.enabled = not autosculptor_props.random_seed
                row.prop(autosculptor_props, "seed")
                
                box.prop(autosculptor_props, "random_seed")
                box.prop(autosculptor_props, "guidance_scale")
                box.prop(autosculptor_props, "num_inference_steps")
                box.prop(autosculptor_props, "image_width")
                box.prop(autosculptor_props, "image_height")
                box.prop(autosculptor_props, "run_in_thread")
                box.prop(autosculptor_props, "batch_count")

            layout.label(text=f"Estimated time: {autosculptor_props.estimated_time}")
            layout.operator("object.autosculptor_model_generator", text="Generating..." if GeneratorOperator.generating else "Generate 3D Model", icon='MESH_DATA')

# Property group for user input
class GeneratorProperties(bpy.types.PropertyGroup):
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

@persistent
def update_estimated_time_on_load(dummy):
    bpy.context.scene.autosculptor_props.update_estimated_time(bpy.context)

def register():
    bpy.utils.register_class(GeneratorOperator)
    bpy.utils.register_class(GeneratorPanel)
    bpy.utils.register_class(InstallDependenciesOperator)
    bpy.utils.register_class(GeneratorProperties)
    bpy.types.Scene.autosculptor_props = bpy.props.PointerProperty(type=GeneratorProperties)
    bpy.app.handlers.load_post.append(update_estimated_time_on_load)

def unregister():
    bpy.utils.unregister_class(GeneratorOperator)
    bpy.utils.unregister_class(GeneratorPanel)
    bpy.utils.unregister_class(InstallDependenciesOperator)
    bpy.utils.unregister_class(GeneratorProperties)
    del bpy.types.Scene.autosculptor_props
    bpy.app.handlers.load_post.remove(update_estimated_time_on_load)

if __name__ == "__main__":
    register()
