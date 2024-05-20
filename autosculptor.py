import bpy
import random
from gradio_client import Client, file
import requests

# Blender add-on information
bl_info = {
    "name": "Autosculptor 3D Model Generator",
    "blender": (2, 80, 0),
    "category": "Object",
    "description": "Generate 3D models using generative models.",
    "author": "Greenmagenta",
    "version": (1, 3, 0),
    "location": "View3D > Sidebar > Autosculptor",
    "support": "COMMUNITY",
    "doc_url": "https://github.com/greenmagenta/autosculptor",
    "tracker_url": "https://github.com/greenmagenta/autosculptor/issues",
    "isDraft": False
}

# Operator for generating 3D models
class GeneratorOperator(bpy.types.Operator):
    bl_idname = "object.autosculptor_model_generator"
    bl_label = "Generate 3D Model"
    bl_description = "Generate a 3D model based on the provided prompt and settings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Import properties from context
        autosculptor_props = context.scene.autosculptor_props

        # Get properties from user input
        prompt = autosculptor_props.prompt
        if autosculptor_props.prompt_enhancer:
            prompt = self.enhance_prompt(prompt)
        seed = autosculptor_props.seed
        if autosculptor_props.random_seed:
            seed = random.randint(0, 2147483647)
        guidance_scale = autosculptor_props.guidance_scale
        num_inference_steps = autosculptor_props.num_inference_steps
        model_type = autosculptor_props.model_type

        # Generate the 3D model
        model_path = self.generate_model(prompt, seed, guidance_scale, num_inference_steps, model_type)
        
        # Handle errors in model generation
        if not model_path:
            self.report({'ERROR'}, "Invalid model type.")
            return {'CANCELLED'}

        # Import the generated model into Blender
        bpy.ops.import_scene.gltf(filepath=model_path)
        
        # Check if any object was imported
        if not bpy.context.selected_objects:
            self.report({'ERROR'}, "No object was imported.")
            return {'CANCELLED'}

        # Get the imported object
        parent_obj = bpy.context.selected_objects[0]
        obj = next((child for child in parent_obj.children if child.type == 'MESH'), None)
        
        # Handle errors in finding a mesh object
        if obj is None:
            self.report({'ERROR'}, "No mesh object found among imported children.")
            return {'CANCELLED'}
        
        # Assign material to the imported object
        self.assign_material(obj)

        return {'FINISHED'}

    # Function to call the prompt enhancer API
    def enhance_prompt(self, prompt):
        response = requests.post(
            "https://gustavosta-magicprompt-stable-diffusion.hf.space/api/predict",
            json={"data": [prompt + ", 3d model"]}
        )
        if response.status_code == 200:
            enhanced_prompt = response.json().get('data', [None])[0]
            if enhanced_prompt:
                return enhanced_prompt.split("\n")[0]
        return prompt

    # Function to generate the model based on the type
    def generate_model(self, prompt, seed, guidance_scale, num_inference_steps, model_type):
        if model_type == "model-shape-e":
            return self.generate_shape_e_model(prompt, seed, guidance_scale, num_inference_steps)
        elif model_type == "model-sdxl-shape-e":
            return self.generate_sdxl_shape_e_model(prompt, seed, guidance_scale, num_inference_steps)
        elif model_type == "model-sdxl-dreamgaussian":
            return self.generate_sdxl_dreamgaussian_model(prompt, seed, guidance_scale, num_inference_steps)
        elif model_type == "model-sdxl-instantmesh":
            return self.generate_sdxl_instantmesh_model(prompt, seed, guidance_scale, num_inference_steps)
        elif model_type == "model-sdxl-triposr":
            return self.generate_sdxl_triposr_model(prompt, seed, guidance_scale, num_inference_steps)
        return None

    # Function to generate Shape-E model
    def generate_shape_e_model(self, prompt, seed, guidance_scale, num_inference_steps):
        client = Client("hysts/Shap-E")
        result = client.predict(
            prompt=prompt,
            seed=seed,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            api_name="/text-to-3d"
        )
        return result

    # Function to generate SDXL + Shape-E model
    def generate_sdxl_shape_e_model(self, prompt, seed, guidance_scale, num_inference_steps):
        client1 = Client("ByteDance/Hyper-SDXL-1Step-T2I")
        image = client1.predict(
            num_images=1,
            height=1024,
            width=1024,
            prompt=prompt,
            seed=seed,
            api_name="/process_image"
        )
        image_path = image[0]['image']

        client2 = Client("https://one-2-3-45-one-2-3-45.hf.space/")
        segmented_img_filepath = client2.predict(image_path, api_name="/preprocess")

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
    def generate_sdxl_dreamgaussian_model(self, prompt, seed, guidance_scale, num_inference_steps):
        client1 = Client("ByteDance/Hyper-SDXL-1Step-T2I")
        image = client1.predict(
            num_images=1,
            height=1024,
            width=1024,
            prompt=prompt,
            seed=seed,
            api_name="/process_image"
        )
        image_path = image[0]['image']

        client2 = Client("https://one-2-3-45-one-2-3-45.hf.space/")
        elevation_angle_deg = client2.predict(image_path, True, api_name="/estimate_elevation")

        if elevation_angle_deg < -90 or elevation_angle_deg > 90:
            elevation_angle_deg = 0

        client3 = Client("https://jiawei011-dreamgaussian.hf.space/--replicas/e0l1g/")
        result = client3.predict(image_path, True, elevation_angle_deg, fn_index=2)
        return result

    # Function to generate SDXL + InstantMesh model
    def generate_sdxl_instantmesh_model(self, prompt, seed, guidance_scale, num_inference_steps):
        client1 = Client("ByteDance/Hyper-SDXL-1Step-T2I")
        image = client1.predict(
            num_images=1,
            height=1024,
            width=1024,
            prompt=prompt,
            seed=seed,
            api_name="/process_image"
        )
        image_path = image[0]['image']

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

        result = client2.predict(api_name="/make3d")
        return result[1]
    
    # Function to generate SDXL + InstantMesh model
    def generate_sdxl_triposr_model(self, prompt, seed, guidance_scale, num_inference_steps):
        client1 = Client("ByteDance/Hyper-SDXL-1Step-T2I")
        image = client1.predict(
            num_images=1,
            height=1024,
            width=1024,
            prompt=prompt,
            seed=seed,
            api_name="/process_image"
        )
        image_path = image[0]['image']

        client2 = Client("stabilityai/TripoSR")
        processed_image = client2.predict(
            image_path,
            True,
            0.5,
            api_name="/preprocess"
        )
        
        result = client2.predict(
            processed_image,
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

        # Add main properties to the UI
        layout.prop(autosculptor_props, "prompt")
        layout.prop(autosculptor_props, "model_type")

        # Create a collapsible section for advanced settings
        box = layout.box()
        box.prop(autosculptor_props, "show_advanced", text="Advanced Settings", emboss=False, icon='TRIA_DOWN' if autosculptor_props.show_advanced else 'TRIA_RIGHT')
        
        if autosculptor_props.show_advanced:
            box.prop(autosculptor_props, "prompt_enhancer")
            row = box.row()
            row.enabled = not autosculptor_props.random_seed
            row.prop(autosculptor_props, "seed")
            
            box.prop(autosculptor_props, "random_seed")
            box.prop(autosculptor_props, "guidance_scale")
            box.prop(autosculptor_props, "num_inference_steps")

        layout.operator("object.autosculptor_model_generator")

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
    model_type: bpy.props.EnumProperty(
        name="Model",
        description="Model pipeline to use for generation",
        items=[
            ("model-shape-e", "Shap-E", "hysts/Shap-E (~13s)"),
            ("model-sdxl-shape-e", "SDXL + Shap-E", "ByteDance/Hyper-SDXL-1Step-T2I + hysts/Shap-E (~30s)"),
            ("model-sdxl-dreamgaussian", "SDXL + DreamGaussian", "ByteDance/Hyper-SDXL-1Step-T2I + jiawei011/dreamgaussian (~600s)"),
            ("model-sdxl-instantmesh", "SDXL + InstantMesh", "ByteDance/Hyper-SDXL-1Step-T2I + TencentARC/InstantMesh (~60s)"),
            ("model-sdxl-triposr", "SDXL + TripoSR", "ByteDance/Hyper-SDXL-1Step-T2I + stabilityai/TripoSR (~30s)")
        ],
        default="model-shape-e"
    )
    show_advanced: bpy.props.BoolProperty(
        name="Show Advanced Settings",
        description="Show or hide advanced settings",
        default=False
    )

def register():
    bpy.utils.register_class(GeneratorOperator)
    bpy.utils.register_class(GeneratorPanel)
    bpy.utils.register_class(GeneratorProperties)
    bpy.types.Scene.autosculptor_props = bpy.props.PointerProperty(type=GeneratorProperties)

def unregister():
    bpy.utils.unregister_class(GeneratorOperator)
    bpy.utils.unregister_class(GeneratorPanel)
    bpy.utils.unregister_class(GeneratorProperties)
    del bpy.types.Scene.autosculptor_props

if __name__ == "__main__":
    register()
