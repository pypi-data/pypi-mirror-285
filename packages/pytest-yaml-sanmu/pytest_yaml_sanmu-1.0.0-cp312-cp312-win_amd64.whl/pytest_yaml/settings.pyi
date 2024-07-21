from pathlib import Path

enable_plugin: bool
mark_can_use_vars: bool
steps_can_use_vars: bool
global_variable_paths: list[Path]
global_variable_paths_ignore_if_non_existent: bool
global_variable_python_class_name: str

def load_global_variable_by_paths() -> dict[None]: ...
