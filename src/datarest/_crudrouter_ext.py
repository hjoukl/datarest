# A customized SLQAlchemyCRUDRouter subclass that adds filter query support.
# Gratefully adapted from https://github.com/awtkns/fastapi-crudrouter/pull/61

import textwrap
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from fastapi import Depends, Response, Query, status
from fastapi_crudrouter import SQLAlchemyCRUDRouter
from fastapi_crudrouter.core.sqlalchemy import (
    DEPENDENCIES, CALLABLE_LIST, PAGINATION, SCHEMA, Model, Session
    )
import pydantic


T = TypeVar("T", bound=pydantic.BaseModel)
FILTER = Dict[str, Optional[Union[int, float, str, bool]]]


filter_mapping = {
    "int": int,
    "float": float,
    "bool": bool,
    "str": str,
    "ConstrainedStrValue": str,
}

# Customize some CRUDRouter status code defaults since they're suboptimal
custom_routes_status = {
    'create': status.HTTP_201_CREATED,
    }


def status_code(http_code: int = status.HTTP_200_OK):

    def resp_status_code(response: Response):
        response.status_code = http_code
        return response

    return resp_status_code


# TODO: Any chance to do this without exec? AST?
# - Take a look at dataclass and/or attrs
# - see also https://github.com/tiangolo/fastapi/issues/4700 for potential
#   problems + hints
def query_factory(
        schema: Type[T],
        query_params: Optional[List[str]] = None
        ) -> Any:
    """Dynamically build a Fastapi dependency for query parameters.

    Based on available fields in the model and the given query_params names
    to expose.
    """
    query_params = [] if query_params is None else query_params

    arg_template = "{name}: Optional[{typ}] = Query(None)"
    args_list = []

    ret_dict_arg_template = "{}={}"
    ret_dict_args = []
    # TODO: Exclude REST resource id field from allowed query params
    for name, field in schema.__fields__.items():
        if (name in query_params
                and field.type_.__name__ in filter_mapping):
            args_list.append(
                arg_template.format(
                    name=name,
                    typ=filter_mapping[field.type_.__name__].__name__)
                )
            ret_dict_args.append(
                ret_dict_arg_template.format(name, field.name)
                )
    if args_list:
        args_str = ", ".join(args_list)
        ret_dict_args_str = ", ".join(ret_dict_args)

        filter_func_src = textwrap.dedent(f"""
            def filter_func({args_str}) -> FILTER:
                ret = dict({ret_dict_args_str})
                return {{k:v for k, v in ret.items() if v is not None}}
            """).strip("\n")
        exec(filter_func_src, globals(), locals())
        _filter_func = locals().get("filter_func")
        return _filter_func
    else:
        return None


class FilteringSQLAlchemyCRUDRouter(SQLAlchemyCRUDRouter):

    def __init__(
            self,
            schema: Type[SCHEMA],
            db_model: Model,
            db: "Session",
            create_schema: Optional[Type[SCHEMA]] = None,
            update_schema: Optional[Type[SCHEMA]] = None,
            prefix: Optional[str] = None,
            tags: Optional[List[str]] = None,
            paginate: Optional[int] = None,
            get_all_route: Union[bool, DEPENDENCIES] = True,
            get_one_route: Union[bool, DEPENDENCIES] = True,
            create_route: Union[bool, DEPENDENCIES] = True,
            update_route: Union[bool, DEPENDENCIES] = True,
            delete_one_route: Union[bool, DEPENDENCIES] = True,
            delete_all_route: Union[bool, DEPENDENCIES] = True,
            query_params: Optional[List[str]] = None,
            **kwargs: Any
            ) -> None:
        query_params = [] if query_params is None else query_params

        query_dependency = query_factory(schema, query_params)
        if query_dependency is None:
            self.filter = Depends(lambda: {})
        else:
            self.filter = Depends(query_factory(schema, query_params))
        super().__init__(
            schema=schema,
            db_model=db_model,
            db=db,
            create_schema=create_schema,
            update_schema=update_schema,
            prefix=prefix,
            tags=tags,
            paginate=paginate,
            get_all_route=get_all_route,
            get_one_route=get_one_route,
            create_route=create_route,
            update_route=update_route,
            delete_one_route=delete_one_route,
            delete_all_route=delete_all_route,
            **kwargs
            )

    def _get_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:

        def route(
                db: Session = Depends(self.db_func),
                pagination: PAGINATION = self.pagination,
                filter_: FILTER = self.filter
                ) -> List[Model]:
            skip, limit = pagination.get("skip"), pagination.get("limit")

            db_models: List[Model] = (
                db.query(self.db_model)
                .filter_by(**filter_)
                .order_by(getattr(self.db_model, self._pk))
                .limit(limit)
                .offset(skip)
                .all()
            )
            return db_models

        return route
