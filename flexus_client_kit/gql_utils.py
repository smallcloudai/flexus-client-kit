from typing import Dict, Any, Type, TypeVar, get_type_hints, Union, Callable, Awaitable
import pydantic
import dataclasses
import logging
import aiohttp.client_exceptions
from flexus_client_kit import ckit_shutdown

T = TypeVar('T')


def strawberry_from_prisma(prisma_obj: pydantic.BaseModel, strawberry_class: Type[T]) -> T:
    """
    Prisma models are pydantic.BaseModel.
    Strawberry models are dataclasses.

    Use for return types like this:

    @strawberry.type
    class MyOutputStruct:
        field1: str

    @strawberry.field
    async def my_external_api_call(
        self,
        ...
    ) -> MyOutputStruct:
        ...
        my_struct = await my_prisma.flexus_group.find_unique(...)
        return gql_utils.strawberry_from_prisma(my_struct, MyOutputStruct)
    """
    field_values = {}
    for f in dataclasses.fields(strawberry_class):
        if hasattr(prisma_obj, f.name):
            val = getattr(prisma_obj, f.name)
            if dataclasses.is_dataclass(f.type) and isinstance(val, pydantic.BaseModel):
                field_values[f.name] = strawberry_from_prisma(val, f.type)
            else:
                field_values[f.name] = val
        else:
            origin = getattr(f.type, "__origin__", None)   # Optional[T] is syntactic sugar for Union[T, None]
            args = getattr(f.type, "__args__", ())
            assert origin is Union and type(None) in args, f"Field '{f.name}' is missing from prisma object but is not optional"
            field_values[f.name] = None
    return strawberry_class(**field_values)


def dataclass_from_dict(data: Dict[str, Any], cls: Type[T]) -> T:
    """
    For python client side, use like this:

    @dataclass
    class MyDataclassForResponse:
        field1: str
    async for result in session.subscribe("subscription NameOfClientScript ...", variable_values={"x": 1337}):
        typed_subs = gql_utils.dataclass_from_dict(result["NameOfClientScript"], MyDataclassForResponse)

    Most of the code in this project is server side, but chat advancer and some other isolated services are
    client side, meaning they use GraphQL to communicate with the server.
    """
    filtered_data = {k: v for k, v in data.items() if k in cls.__annotations__}
    for field_name, field_value in filtered_data.items():
        if field_value is not None and field_name in cls.__annotations__:
            field_type = cls.__annotations__[field_name]
            if hasattr(field_type, "__origin__") and field_type.__origin__ is Union:
                inner_types = [arg for arg in field_type.__args__ if arg is not type(None)]
                if inner_types:
                    # Try to discriminate between Union types based on which has matching fields
                    if len(inner_types) > 1 and isinstance(field_value, dict) and all(hasattr(t, "__annotations__") for t in inner_types):
                        best_match = None
                        best_match_count = 0
                        for candidate_type in inner_types:
                            candidate_fields = set(candidate_type.__annotations__.keys())
                            data_fields = set(field_value.keys())
                            match_count = len(candidate_fields & data_fields)
                            if match_count > best_match_count:
                                best_match = candidate_type
                                best_match_count = match_count
                        field_type = best_match if best_match else inner_types[0]
                    else:
                        field_type = inner_types[0]
            # JSON scalar types should pass through as-is (already parsed)
            is_json = (
                getattr(field_type, '__name__', None) == 'JSON' or
                getattr(getattr(field_type, 'wrap', None), '__name__', None) == 'JSON'
            )
            if is_json:
                filtered_data[field_name] = field_value
            elif hasattr(field_type, "__origin__") and field_type.__origin__ is list:
                if field_type.__args__ and isinstance(field_value, list):
                    inner_type = field_type.__args__[0]
                    if hasattr(inner_type, "__annotations__"):
                        # List of dataclasses
                        filtered_data[field_name] = [dataclass_from_dict(item, inner_type) for item in field_value]
                    else:
                        # List of primitives, keep as is
                        filtered_data[field_name] = field_value
            elif field_type is Any:
                # Fallback for Any type
                filtered_data[field_name] = field_value
            elif hasattr(field_type, "__annotations__"):
                filtered_data[field_name] = dataclass_from_dict(field_value, field_type)
    return cls(**filtered_data)


def gql_fields(cls: Type[Any], depth: int = 4) -> str:
    """
    Another function for client side, use together with dataclass_from_dict() to prepare the query string.

    from gql import gql
    req = gql(f'''
        subscription NameOfClientScript ... {{
            real_function_name() {{
                {gql_utils.gql_fields(MyDataclassForResponse)}
            }}
        }}
        ''')
    """
    result = []
    indent = "    " * depth
    for field_name, field_type in get_type_hints(cls).items():
        origin = getattr(field_type, "__origin__", None)
        args = getattr(field_type, "__args__", [])

        # Optional: unwrap only if Union[T, None] or Union[None, T]
        unwrapped_type = field_type
        if origin is Union and len(args) == 2 and type(None) in args:
            non_none_args = [arg for arg in args if arg is not type(None)]
            if len(non_none_args) == 1:
                unwrapped_type = non_none_args[0]
                field_type = unwrapped_type
                origin = getattr(field_type, "__origin__", None)
                args = getattr(field_type, "__args__", [])

        # Skip ERP relation fields
        if dataclasses.is_dataclass(unwrapped_type):
            module_name = getattr(unwrapped_type, '__module__', '')
            if module_name == 'flexus_client_kit.erp_schema':
                continue

        # Union (non-optional unions, or after unwrapping Optional)
        if origin is Union:
            union_types = [arg for arg in args if arg is not type(None)]
            if union_types and all(hasattr(t, "__annotations__") for t in union_types):
                fragments = []
                for union_member in union_types:
                    type_name = union_member.__name__
                    if not type_name.endswith("Output"):
                        type_name = type_name + "Output"
                    nested_fields = gql_fields(union_member, depth + 1)
                    if nested_fields:
                        fragments.append(f"{indent}    ... on {type_name} {{\n{nested_fields}\n{indent}    }}")
                if fragments:
                    result.append(f"{indent}{field_name} {{\n" + "\n".join(fragments) + f"\n{indent}}}")
                else:
                    result.append(f"{indent}{field_name}")
            else:
                result.append(f"{indent}{field_name}")

        # List
        elif origin is list and args:
            inner_type = args[0]
            if hasattr(inner_type, "__annotations__"):
                nested_fields = gql_fields(inner_type, depth + 1)
                if nested_fields:
                    result.append(f"{indent}{field_name} {{\n{nested_fields}\n{indent}}}")
                else:
                    result.append(f"{indent}{field_name}")
            else:
                result.append(f"{indent}{field_name}")

        # Aggregated dataclass
        elif hasattr(field_type, "__annotations__"):
            nested_fields = gql_fields(field_type, depth + 1)
            if nested_fields:
                result.append(f"{indent}{field_name} {{\n{nested_fields}\n{indent}}}")
            else:
                result.append(f"{indent}{field_name}")
        else:
            result.append(f"{indent}{field_name}")

    return "\n".join(result)


async def gql_with_retry(
    operation: Callable[[], Awaitable[T]],
    logger: logging.Logger,
    operation_name: str,
    initial_delay: int = 10,
    max_delay: int = 300,
    max_attempts: int = 10,
) -> T:
    retry_delay = initial_delay
    attempt = 1
    complained = False
    while not ckit_shutdown.shutdown_event.is_set():
        try:
            result = await operation()
            if complained:
                logger.warning(f"{operation_name} after {attempt} attempts successed, phew!!!")
            return result
        except (aiohttp.client_exceptions.ClientError) as e:
            if ckit_shutdown.shutdown_event.is_set():
                break
            logger.warning(f"{operation_name} attempt {attempt} failed: {e}, retrying in {retry_delay}s")
            complained = True
            if attempt == max_attempts:
                raise
            if await ckit_shutdown.wait(retry_delay):
                break
            retry_delay = min(retry_delay * 2, max_delay)
            attempt += 1
