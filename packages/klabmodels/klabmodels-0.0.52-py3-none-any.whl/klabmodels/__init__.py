import importlib

# List of modules to import symbols from
modules_to_import = ['models', 'api']
# Initialize the __all__ variable

__all__ = []

# Dynamically import all symbols from the specified modules

for module_name in modules_to_import:
  #print(module_name)
  #print(__name__)
  module = importlib.import_module(f'.{module_name}', package=__name__)
  for symbol in dir(module):
    if not symbol.startswith('_'):
      #print(symbol)
      globals()[symbol] = getattr(module, symbol)
      __all__.append(symbol)