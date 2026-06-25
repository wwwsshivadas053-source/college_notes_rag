from importlib import util
from pathlib import Path
import sys


def _load_create_app():
    package_dir = Path(__file__).resolve().parent / "app"
    spec = util.spec_from_file_location(
        "college_notes_webapp",
        package_dir / "__init__.py",
        submodule_search_locations=[str(package_dir)],
    )
    module = util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.create_app


create_app = _load_create_app()
app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
