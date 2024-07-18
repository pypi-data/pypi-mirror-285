from typing import Any, Callable

from ..utils.registry import Registry

type Operator = Any
type OperatorKey = type
type OperatorFactoryFn = Callable[[], Operator]
type OperatorFactoryRegistry = Registry[OperatorKey, OperatorFactoryFn]
