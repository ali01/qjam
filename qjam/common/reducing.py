def default_reduce(result1, result2):
  '''Default reducer. Combines two results into one result. This function
  should be called multiple times (or passed to Python's reduce()) to combine a
  list of results.

  Arguments must be sequences of the same length or objects that implement
  __add__(). Sequences will be added element-wise with the plus (+)
  operator. Other objects will be added also using the plus (+) operator.

  Args:
    result1: a sequence (list, tuple) or an addable
    result2: same

  Raises:
    TypeError if sequences are not the same length or the results cannot be
    added.

  Returns:
    combination of result1 and result2
  '''
  if ((isinstance(result1, list) or isinstance(result1, tuple)) and
      (isinstance(result2, list) or isinstance(result2, tuple))):
    # Sequences must be the same length.
    if len(result1) != len(result2):
      raise TypeError, 'input sequences must be the same length'

    # Combine the sequences.
    result = list(result1)
    for i in range(len(result2)):
      result[i] += result2[i]
    return result
  else:
    return result1 + result2
