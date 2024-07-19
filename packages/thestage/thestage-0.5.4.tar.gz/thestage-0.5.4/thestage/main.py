import typer

from . import __app_name__

from thestage.controllers import base_controller, container_controller, instance_controller, storage_controller, config_controller

base_controller.app.add_typer(container_controller.app, name="container")
base_controller.app.add_typer(instance_controller.app, name="instance")
base_controller.app.add_typer(config_controller.app, name="config")
#base_controller.app.add_typer(storage_controller.app, name="storage")


def main():
    import thestage.config
    base_controller.app(prog_name=__app_name__)
