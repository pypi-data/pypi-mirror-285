from typing import Any, Callable

from greyhorse.app.utils.registry import Registry

type Operator = Any
type OperatorKey = type
type OperatorFactoryFn = Callable[[], Operator]
type OperatorRegistry = Registry[OperatorKey, Operator]
type OperatorFactoryRegistry = Registry[OperatorKey, OperatorFactoryFn]
