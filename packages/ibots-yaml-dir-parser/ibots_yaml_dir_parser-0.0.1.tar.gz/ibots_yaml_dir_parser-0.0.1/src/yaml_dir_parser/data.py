from typing import Any, Dict, Literal
from pathlib import Path, PurePosixPath

import markdown2
import yaml 

loaders = {
    'md': lambda text: markdown2.Markdown().convert(text),
    'yaml': lambda text: yaml.load(text, yaml.Loader),
}

def load_dir(base_path: Path | str) -> Dict[str, Any]:
    base_path = Path(base_path)

    return _extract_recursive(base_path, base_path)


def _process_file(item: Path, base_path: Path, collections: Dict[str, Any]) -> None:
    if '.yaml' in item.name:
        text = item.read_text()
        data = loads(text, format='yaml')

        # overwrite absolute filepath strings with the absolute path to the referenced file.
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and value.startswith('/'):
                    new_value = str(PurePosixPath(base_path).joinpath(value.lstrip('/')))
                    data[key] = new_value
        elif isinstance(data, list):
            for idx, value in enumerate(data):
                if isinstance(value, str) and value.startswith('/'):
                    new_value = str(PurePosixPath(base_path).joinpath(value.lstrip('/')))
                    data[idx] = new_value
        if item.name == '.yaml':  # Is only a YAML extension?  Read it and just stick the data onto the parent.
            collections.update(data)  
        else:
            collections[item.stem] = data
    else:  # Not sure how to parse the file?  Then assign a filepath.
        collections[item.stem] = str(PurePosixPath(item))


def loads(text, format: Literal['md', 'yaml']) -> Any:
    try:
        loader = loaders[format]
    except KeyError:
        raise NotImplementedError(f"{format} files not yet supported. Supported formats: {list(loaders.keys())}")
    
    data = loader(text)
    return data


def _extract_recursive(path: Path, base_path: Path) -> Dict[str, Any]:
    
    collections = {}
    for item in path.iterdir():
        if item.is_dir():
            collections[item.stem] = _extract_recursive(item, base_path)
        else:
            _process_file(item, base_path, collections)
    return collections

