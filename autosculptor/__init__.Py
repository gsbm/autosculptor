import bpy
from .operators import GeneratorOperator, InstallDependenciesOperator
from .panels import GeneratorPanel
from .properties import GeneratorProperties
from bpy.app.handlers import persistent

bl_info = {
    "name": "Autosculptor 3D Model Generator",
    "author": "Greenmagenta",
    "version": (1, 7, 0),
    "blender": (2, 80, 0),
    "category": "3D View",
    "description": "Generate 3D models using generative models.",
    "warning": "Requires installation of dependencies",
    "location": "View3D > Sidebar > Autosculptor",
    "support": "COMMUNITY",
    "doc_url": "https://github.com/greenmagenta/autosculptor",
    "tracker_url": "https://github.com/greenmagenta/autosculptor/issues",
    "isDraft": False
}

@persistent
def update_estimated_time_on_load(dummy):
    bpy.context.scene.autosculptor_props.update_estimated_time(bpy.context)

def update_estimated_time_later():
    if bpy.context.scene and bpy.context.scene.autosculptor_props:
        bpy.context.scene.autosculptor_props.update_estimated_time(bpy.context)
        return None  # Stop the timer
    return 0.1  # Check again after 0.1 second

def register():
    bpy.utils.register_class(GeneratorOperator)
    bpy.utils.register_class(InstallDependenciesOperator)
    bpy.utils.register_class(GeneratorPanel)
    bpy.utils.register_class(GeneratorProperties)
    bpy.types.Scene.autosculptor_props = bpy.props.PointerProperty(type=GeneratorProperties)
    bpy.app.handlers.load_post.append(update_estimated_time_on_load)
    bpy.app.timers.register(update_estimated_time_later)

def unregister():
    bpy.utils.unregister_class(GeneratorOperator)
    bpy.utils.unregister_class(InstallDependenciesOperator)
    bpy.utils.unregister_class(GeneratorPanel)
    bpy.utils.unregister_class(GeneratorProperties)
    del bpy.types.Scene.autosculptor_props
    bpy.app.handlers.load_post.remove(update_estimated_time_on_load)

if __name__ == "__main__":
    register()
