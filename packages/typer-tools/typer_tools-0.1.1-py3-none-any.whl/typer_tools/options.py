from functools import wraps
import typer

@wraps(typer.Option)
def option(default, *args, **kwargs):
  """An option that can be put in many places and still share the same state.

  Ever wanted to make `cli -v export` and `cli export -v` work the same way!?
  
  ```
  Verbose = option(False, '-v', '--verbose')

  @app.callback()
  def main(verbose: bool = Verbose):
    ...

  @app.command()
  def export(verbose: bool = Verbose):
    ...
  ```
  """
  state = default
  og_callback = kwargs.pop('callback', None)
  
  def callback(value):
    nonlocal state
    if value is not None:
      if og_callback:
        og_callback(value)
      state = value
    return state
  
  return typer.Option(None, *args, callback=callback, **kwargs)