import zipimport


def LoadPyDLL(Path: str, specific_module: str = None):
    try:
        # Use zipimport to import the package
        package = zipimport.zipimporter(Path)
        
        if specific_module is None:
            # Load __init__.py module by default
            module = package.load_module('__init__')
        else:
            # Load the specified module
            module = package.load_module(specific_module)

        return module

    except zipimport.ZipImportError as e:
        raise ImportError(f"Failed to import package from '{Path}': {e}")