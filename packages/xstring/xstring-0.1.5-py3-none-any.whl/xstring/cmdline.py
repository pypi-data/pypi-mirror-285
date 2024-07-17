import typer
import asyncio
from typing import Optional, List
from xstring.manager import SimpleManager, DocstringMode  # 假设你的代码在 my_module.py 中
from pathlib import Path
import importlib.util
import sys
from types import ModuleType


app = typer.Typer()

docstring_mode_descriptions = {
    DocstringMode.TRANSLATE: "Translate the docstrings.",
    DocstringMode.POLISH: "Polish the docstrings.",
    DocstringMode.CLEAR: "Clear the docstrings.",
    DocstringMode.FILL: "Fill in missing docstrings."
}

def docstring_mode_help():
    return "\n".join(
        [f"{mode.value}: {description}" for mode, description in docstring_mode_descriptions.items()]
    )


def find_real_root(directory_path: Path) -> Path:
    current_path = directory_path
    while (current_path.parent / '__init__.py').exists():
        current_path = current_path.parent
    return current_path

def load_module(module_path_or_name: str) -> ModuleType:
    module_path = Path(module_path_or_name)

    if module_path.exists():
        # Find the real root of the module
        root_path = find_real_root(module_path)

        # Add the root path to sys.path
        sys.path.insert(0, str(root_path.parent))

        # Determine the module name relative to the root path
        relative_module_path = module_path.relative_to(root_path.parent)
        module_name = '.'.join(relative_module_path.with_suffix('').parts)

        # Import the module
        module = importlib.import_module(module_name)

        return module
    else:
        # If the path does not exist, try to import it as a standard module
        return importlib.import_module(module_path_or_name)
def parse_skip_modules(ctx: typer.Context, value:Optional[List]) -> List[str]:
    if value:
        return value[0].split(',')
    return []


@app.command()
def traverse(
    module_or_path: str,
    pattern: DocstringMode = typer.Option(..., help=f"Docstring handling mode.\n{docstring_mode_help()}"),
    skip_modules: Optional[List[str]] = typer.Option(None,
                                                     "--skip-modules", "-s",
                                                     help="List of modules to skip,splited by comma",
                                                     callback=parse_skip_modules),
    skip_on_error: bool = typer.Option(False, help="Whether to skip errors or raise them")
):
    """
    Traverse through the package or module to process docstrings.
    """
    try:
        module = load_module(module_or_path)
        manager = SimpleManager(pattern=pattern, skip_on_error=skip_on_error)
        print(skip_modules)
        manager.traverse(module, skip_modules)
        typer.echo(f"Traversal completed for module or path: {module_or_path}")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)

@app.command()
def atraverse(
    module_or_path: str,
    pattern: DocstringMode = typer.Option(..., help=f"Docstring handling mode.\n{docstring_mode_help()}"),
    skip_modules: Optional[List[str]] = typer.Option(None,
                                                     "--skip-modules", "-s",
                                                     help="List of modules to skip,splited by comma",
                                                     callback=parse_skip_modules),
    skip_on_error: bool = typer.Option(False, help="Whether to skip errors or raise them"),
    max_concurrency: int = typer.Option(10, help="Maximum number of concurrent tasks")
):
    """
    Asynchronously traverse through the package or module to process docstrings.
    """
    async def async_traverse():
        try:
            module = load_module(module_or_path)
            manager = SimpleManager(pattern=pattern, skip_on_error=skip_on_error)
            await manager.atraverse(module, skip_modules, max_concurrency)
            typer.echo(f"Async traversal completed for module or path: {module_or_path}")
        except Exception as e:
            typer.echo(f"Error: {e}", err=True)

    asyncio.run(async_traverse())


if __name__ == "__main__":
    app()
