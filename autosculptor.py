import bpy
import random
from gradio_client import Client, file

bl_info = {
    "name": "Autosculptor 3D Model Generator",
    "blender": (2, 80, 0),
    "category": "Object",
    "description": "Generate 3D models using generative models.",
    "author": "Greenmagenta",
    "version": (1, 1, 0),
    "location": "View3D > Sidebar > Autosculptor",
    "support": "COMMUNITY",
    "doc_url": "https://github.com/greenmagenta/autosculptor",
    "tracker_url": "https://github.com/greenmagenta/autosculptor/issues",
    "isDraft": False
}

class GeneratorOperator(bpy.types.Operator):
    bl_idname = "object.autosculptor_model_generator"
    bl_label = "Generate 3D Model"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Import properties from context
        autosculptor_props = context.scene.autosculptor_props
        
        prompt = autosculptor_props.prompt
        seed = autosculptor_props.seed
        if autosculptor_props.random_seed:
            seed = random.randint(0, 2147483647)
        guidance_scale = autosculptor_props.guidance_scale
        num_inference_steps = autosculptor_props.num_inference_steps
        model_type = autosculptor_props.model_type
        
        # Shape-E model
        if model_type == "shape-e-text":
            # Generate 3D model with Shape-E model
            client = Client("hysts/Shap-E")
            result = client.predict(
                prompt=prompt,
                seed=seed,
                guidance_scale=guidance_scale,
                num_inference_steps=num_inference_steps,
                api_name="/text-to-3d"
            )
            model_path = result

        # SDXL + Shape-E model
        elif model_type == "sdxl-shape-e":
            # Generate image with SDXL model
            client1 = Client("https://zhuguangbin86-stabilityai-stable-diffusion-xl-base-1-0.hf.space")
            image = client1.predict(
                prompt,
                api_name="/predict"
            )
            image_path = image

            # Preprocess image with One-2-3-45 model
            client2 = Client("https://one-2-3-45-one-2-3-45.hf.space/")
            segmented_img_filepath = client2.predict(
                image_path, 
                api_name="/preprocess"
            )

            # Generate 3D model with Shape-E model
            client3 = Client("hysts/Shap-E")
            result = client3.predict(
                    image=file(segmented_img_filepath),
                    seed=seed,
                    guidance_scale=guidance_scale,
                    num_inference_steps=num_inference_steps,
                    api_name="/image-to-3d"
            )
            model_path = result

        # SDXL + DreamGaussian model
        elif model_type == "sdxl-dreamgaussian":
            # Generate image with SDXL model
            client1 = Client("https://zhuguangbin86-stabilityai-stable-diffusion-xl-base-1-0.hf.space")
            image = client1.predict(
                prompt,
                api_name="/predict"
            )
            image_path = image

            # Estimate elevation angle with One-2-3-45 model
            client2 = Client("https://one-2-3-45-one-2-3-45.hf.space/")
            elevation_angle_deg = client2.predict(
                image_path,
                True,
                api_name="/estimate_elevation"
            )

            if elevation_angle_deg < -90 or elevation_angle_deg > 90:
                elevation_angle_deg = 0

            # Generate 3D model with DreamGaussian model
            client3 = Client("https://jiawei011-dreamgaussian.hf.space/--replicas/e0l1g/")
            result = client3.predict(
                image_path,
                True,
                elevation_angle_deg,
                fn_index=2
            )
            model_path = result

        # SDXL + InstantMesh model
        elif model_type == "sdxl-instantmesh":
            # Generate image with SDXL model
            client1 = Client("https://zhuguangbin86-stabilityai-stable-diffusion-xl-base-1-0.hf.space")
            image = client1.predict(
                prompt,
                api_name="/predict"
            )
            image_path = image

            # Preprocess image with InstantMesh model
            client2 = Client("TencentARC/InstantMesh")
            preprocessed_image = client2.predict(
                input_image=file(image_path),
                do_remove_background=True,
                api_name="/preprocess"
            )

            # Generate MVS images with InstantMesh model
            mvs = client2.predict(
                input_image=file(preprocessed_image),
                sample_steps=num_inference_steps,
                sample_seed=seed,
                api_name="/generate_mvs"
            )

            # Generate 3D model with InstantMesh model
            result = client2.predict(
                api_name="/make3d"
            )

            model_path = result[1]

        else:
            self.report({'ERROR'}, "Invalid model type.")
            return {'CANCELLED'}

        # Load the generated model
        bpy.ops.import_scene.gltf(filepath=model_path)
        
        # Ensure an object has been imported
        if not bpy.context.selected_objects:
            self.report({'ERROR'}, "No object was imported.")
            return {'CANCELLED'}
        
        # Get the imported object (parent)
        parent_obj = bpy.context.selected_objects[0]
        
        # Find mesh object
        obj = None
        if parent_obj.children:
            for child in parent_obj.children:
                if child.type == 'MESH':
                    obj = child
                    break
        
        if obj is None:
            self.report({'ERROR'}, "No mesh object found among imported children.")
            return {'CANCELLED'}
        
        # Create a new material
        material = bpy.data.materials.new(name="ImportedMaterial")
        material.use_nodes = True
        
        # Initialize Principled BSDF node
        bsdf = None
        for node in material.node_tree.nodes:
            if isinstance(node, bpy.types.ShaderNodeBsdfPrincipled):
                bsdf = node
                break
        if bsdf is None:
            bsdf = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
        
        # Create an attribute node
        attribute_node = material.node_tree.nodes.new('ShaderNodeVertexColor')
        if obj.data.vertex_colors:
            attribute_node.layer_name = obj.data.vertex_colors[0].name
        else:
            attribute_node.layer_name = "Color"
        
        # Assign the material to the object
        material.node_tree.links.new(attribute_node.outputs['Color'], bsdf.inputs['Base Color'])
        
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)
    
        return {'FINISHED'}

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
        
        layout.prop(autosculptor_props, "prompt")
        layout.prop(autosculptor_props, "seed")
        layout.prop(autosculptor_props, "random_seed")
        layout.prop(autosculptor_props, "guidance_scale")
        layout.prop(autosculptor_props, "num_inference_steps")
        layout.prop(autosculptor_props, "model_type")
        layout.operator("object.autosculptor_model_generator")

class GeneratorProperties(bpy.types.PropertyGroup):
    prompt: bpy.props.StringProperty(name="Prompt")
    seed: bpy.props.IntProperty(name="Seed", default=0, min=0, max=2147483647)
    random_seed: bpy.props.BoolProperty(name="Random Seed", default=True)
    guidance_scale: bpy.props.IntProperty(name="Guidance Scale", default=15, min=1, max=20)
    num_inference_steps: bpy.props.IntProperty(name="Inference Steps", default=64, min=2, max=100)
    model_type: bpy.props.EnumProperty(
        name="Model",
        items=[
            ("shape-e-text", "Shap-E", "hysts/Shap-E (~13s)"),
            ("sdxl-shape-e", "SDXL + Shap-E", "zhuguangbin86/stabilityai-stable-diffusion-xl-base-1.0 + hysts/Shap-E (~30s)"),
            ("sdxl-dreamgaussian", "SDXL + DreamGaussian", "zhuguangbin86/stabilityai-stable-diffusion-xl-base-1.0 + jiawei011/dreamgaussian (~600s)"),
            ("sdxl-instantmesh", "SDXL + InstantMesh", "zhuguangbin86/stabilityai-stable-diffusion-xl-base-1.0 + TencentARC/InstantMesh (~60s)")
        ],
        default="shape-e-text"
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
