from typing import Callable, TypeVar, Generic
from dataclasses import dataclass
from inspect import Signature, Parameter

T = TypeVar('T')

def delete_kw(sig: Signature, name: str) -> Signature:
  """Deletes a keyword-only parameter from a signature."""
  params = list(sig.parameters.values())
  new_params = [param for param in params if param.name != name]
  return sig.replace(parameters=new_params)

def add_kw(sig: Signature, name: str, default) -> Signature:
  """Adds a keyword-only parameter to a signature. (before the **kwargs)"""
  new_param = Parameter(name, Parameter.KEYWORD_ONLY, default=default)
  params = list(sig.parameters.values())
  if params and params[-1].kind == Parameter.VAR_KEYWORD:
    new_params = params[:-1] + [new_param, params[-1]]
  else:
    new_params = params + [new_param]
  return sig.replace(parameters=new_params)

@dataclass
class Dependency(Generic[T]):
  """Ever wished typer had dependency injection? Here it is! (sort of)
  
  ```
  def parse_client(
    host: str = typer.Option(..., '--host', help='HTTP host'),
    port: int = typer.Option(80, '--port', help='HTTP port'),
    token: str = typer.Option(..., '--token', help='Access token')
  ) -> Client:
    ...

  dep = Dependency(parse_client)

  @typer.command()
  @dep.inject
  def main(some_option: str, client: Client = dep.Depends()):
    ...
  ```
  """
  parse: Callable[..., T]

  def inject(self, func: Callable) -> Callable:
    """Decorate `func` with the dependency"""
    wrapped_sig = sig = Signature.from_callable(func)
    
    # func(..., x: T = dep.Depends) to func(..., **kwargs_of_parse)
    
    # 1. Delete mark
    argname = None
    for name, param in sig.parameters.items():
      if param.default is self:
        argname = name
        wrapped_sig = delete_kw(wrapped_sig, name)
        break
    if argname is None:
      raise ValueError(f'Dependency not found in {func.__name__}')

    # 2. Add parsed parameters
    parsed_sig = Signature.from_callable(self.parse)
    for name, param in parsed_sig.parameters.items():
      wrapped_sig = add_kw(wrapped_sig, name, param.default)

    def wrapper(*args, **kwargs):
      parse_args = {name: kwargs.get(name) for name in parsed_sig.parameters}
      parsed = self.parse(**parse_args)
      # delete from kwargs
      for name in parsed_sig.parameters:
        kwargs.pop(name, None)
      return func(*args, **kwargs, **{argname: parsed})
    
    wrapper.__signature__ = wrapped_sig # type: ignore
    wrapper.__name__ = func.__name__
    return wrapper
    
  def Depends(self) -> T:
    """Dependency injection marker (used by `inject` to substitute the parsed value)"""
    return self # type: ignore
