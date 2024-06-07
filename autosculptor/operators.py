import bpy
import sys
import subprocess
import threading
import random
from bpy.types import Operator
from .utils import ensure_gradio_installed, install_gradio

class InstallDependenciesOperator(Operator):
    bl_idname = "wm.install_dependencies"
    bl_label = "Install Dependencies"
    
    def execute(self, context):
        install_gradio()
        self.report({'INFO'}, "Dependencies installed successfully. Please restart Blender.")
        return {'FINISHED'}

class GeneratorOperator(Operator):
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

    def generate_model(self, prompt, seed, guidance_scale, num_inference_steps, model_type, image_width, image_height):
        from gradio_client import Client, handle_file

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

    def generate_sdxl_shape_e_model(self, prompt, seed, guidance_scale, num_inference_steps, image_width, image_height):
        from gradio_client import Client, handle_file
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
            image=handle_file(segmented_img_filepath),
            seed=seed,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            api_name="/image-to-3d"
        )
        return result

    def generate_sdxl_dreamgaussian_model(self, prompt, seed, guidance_scale, num_inference_steps, image_width, image_height):
        from gradio_client import Client, handle_file
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

    def generate_sdxl_instantmesh_model(self, prompt, seed, guidance_scale, num_inference_steps, image_width, image_height):
        from gradio_client import Client, handle_file
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
            input_image=handle_file(image_path),
            do_remove_background=True,
            api_name="/preprocess"
        )

        mvs = client2.predict(
            input_image=handle_file(processed_image),
            sample_steps=num_inference_steps,
            sample_seed=seed,
            api_name="/generate_mvs"
        )

        result = client2.predict(
            api_name="/make3d"
        )
        return result[1]
    
    def generate_sdxl_triposr_model(self, prompt, seed, guidance_scale, num_inference_steps, image_width, image_height):
        from gradio_client import Client, handle_file
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
            handle_file(image_path),
            True,
            0.5,
            api_name="/preprocess"
        )
        
        result = client2.predict(
            handle_file(processed_image),
            320,
            api_name="/generate"
        )

        return result[1]

    def assign_material(self, obj):
        material = bpy.data.materials.new(name="ImportedMaterial")
        material.use_nodes = True

        bsdf = next((node for node in material.node_tree.nodes if isinstance(node, bpy.types.ShaderNodeBsdfPrincipled)), None)
        if not bsdf:
            bsdf = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')

        attribute_node = material.node_tree.nodes.new('ShaderNodeVertexColor')
        if obj.data.vertex_colors:
            attribute_node.layer_name = obj.data.vertex_colors[0].name
        else:
            attribute_node.layer_name = "Color"

        material.node_tree.links.new(attribute_node.outputs['Color'], bsdf.inputs['Base Color'])

        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)
