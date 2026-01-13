import shutil
import platform

# I needed support for the flatpak version of sumo so please use this
def get_sumo_cmd(base_args, gui=False):
    """
    base_args: list of SUMO arguments, e.g.
      ["-n", "net.xml", "-r", "routes.rou.xml", "--step-length", "0.1"]
    """
    binary = "sumo-gui" if gui else "sumo"
    if platform.system() == "Darwin":
        SUMO_BINARY = "/Library/Frameworks/EclipseSUMO.framework/EclipseSUMO/share/sumo/bin/sumo-gui"
        return [SUMO_BINARY] + base_args
    if shutil.which(binary) or platform.system() == "Darwin":
        return [binary] + base_args

    flatpak_id = "org.eclipse.sumo"
    return ["flatpak", "run", flatpak_id] + base_args