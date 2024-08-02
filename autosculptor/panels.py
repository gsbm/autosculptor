import bpy
from bpy.types import Panel
from .utils import ensure_gradio_installed
from .operators import GeneratorOperator

class GeneratorPanel(Panel):
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
            if not autosculptor_props.estimated_time:
                autosculptor_props.update_estimated_time(context)
            
            layout.prop(autosculptor_props, "prompt")
            layout.prop(autosculptor_props, "model_type")

            box = layout.box()
            box.prop(autosculptor_props, "show_advanced", text="Advanced Settings", emboss=False, icon='TRIA_DOWN' if autosculptor_props.show_advanced else 'TRIA_RIGHT')
            
            if autosculptor_props.show_advanced:
                box.prop(autosculptor_props, "additional_prompt")
                box.prop(autosculptor_props, "negative_prompt")
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
                box.prop(autosculptor_props, "api_key")

            layout.label(text=f"Estimated time: {autosculptor_props.estimated_time}")
            layout.operator("object.autosculptor_model_generator", text="Generating..." if GeneratorOperator.generating else "Generate 3D Model", icon='MESH_DATA')
