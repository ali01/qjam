
def module_src(module):
  '''Return the source code for a given module object.'''
  filename = module.__file__
  filename = filename.replace('.pyc', '.py')
  with open(filename, 'r') as fh:
    return fh.read()
