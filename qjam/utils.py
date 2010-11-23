
def module_path(module):
  '''returns the file path of the source code for a given module object'''
  filename = module.__file__
  return filename.replace('.pyc', '.py')

def module_src(module):
  '''return the source code for a given module object.'''
  filename = module_path(module)
  with open(filename, 'r') as fh:
    return fh.read()
