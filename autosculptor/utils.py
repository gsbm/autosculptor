import sys
import subprocess

def ensure_gradio_installed():
    try:
        import gradio_client
        from packaging import version
        if version.parse(gradio_client.__version__) >= version.parse("1.4.0"):
            return True
        else:
            return False
    except ImportError:
        return False

def install_gradio():
    python_executable = sys.executable
    subprocess.check_call([python_executable, '-m', 'ensurepip'])
    subprocess.check_call([python_executable, '-m', 'pip', 'install', 'gradio_client==1.4.0'])
