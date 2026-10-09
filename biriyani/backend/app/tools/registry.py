from __future__ import annotations
import inspect
from typing import Any, Callable, Dict, Optional, Type
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.models.user import User


class ToolPermissionError(Exception):
    pass


class ToolValidationError(Exception):
    pass


class ToolExecutionError(Exception):
    pass


from pydantic import BaseModel, ConfigDict, Field


class ToolDefinition(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    description: str
    permission: str = "USER"  # "USER" or "ADMIN"
    read_only: bool = True
    input_schema: Optional[Type[BaseModel]] = None


class RegisteredTool:
    def __init__(
        self,
        name: str,
        description: str,
        permission: str,
        read_only: bool,
        input_schema: Optional[Type[BaseModel]],
        func: Callable,
    ):
        self.name = name
        self.description = description
        self.permission = permission
        self.read_only = read_only
        self.input_schema = input_schema
        self.func = func

    def validate_and_execute(
        self,
        db: Session,
        current_user: User,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Validate permissions, sanitize input arguments against schema, and execute tool.
        Enforces server-side authorization: current_user identity CANNOT be overridden by params.
        """
        # 1. Permission check
        if self.permission == "ADMIN" and getattr(current_user, "role", "USER") != "ADMIN":
            raise ToolPermissionError(
                f"Access denied: Tool '{self.name}' requires ADMIN permissions."
            )

        # 2. Input validation against Pydantic schema if provided
        sanitized_params = dict(params) if params else {}

        # Strip any client-supplied user_id or role override attempt
        sanitized_params.pop("user_id", None)
        sanitized_params.pop("current_user", None)
        sanitized_params.pop("role", None)

        if self.input_schema:
            try:
                validated_model = self.input_schema(**sanitized_params)
                validated_kwargs = validated_model.model_dump()
            except Exception as e:
                raise ToolValidationError(f"Invalid parameters for tool '{self.name}': {str(e)}") from e
        else:
            validated_kwargs = sanitized_params

        # 3. Inspect function signature to pass db and current_user if expected
        sig = inspect.signature(self.func)
        kwargs = {}
        if "db" in sig.parameters:
            kwargs["db"] = db
        if "current_user" in sig.parameters:
            kwargs["current_user"] = current_user

        for key, val in validated_kwargs.items():
            if key in sig.parameters:
                kwargs[key] = val

        # 4. Execute tool
        try:
            raw_result = self.func(**kwargs)
            return {
                "success": True,
                "tool_name": self.name,
                "result": raw_result,
            }
        except Exception as exc:
            return {
                "success": False,
                "tool_name": self.name,
                "error": str(exc),
            }


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, RegisteredTool] = {}

    def register(
        self,
        name: str,
        description: str,
        permission: str = "USER",
        read_only: bool = True,
        input_schema: Optional[Type[BaseModel]] = None,
    ):
        def decorator(func: Callable):
            tool = RegisteredTool(
                name=name,
                description=description,
                permission=permission,
                read_only=read_only,
                input_schema=input_schema,
                func=func,
            )
            self._tools[name] = tool
            return func

        return decorator

    def get_tool(self, name: str) -> RegisteredTool:
        if name not in self._tools:
            raise ToolValidationError(f"Tool '{name}' is not registered in the system tool registry.")
        return self._tools[name]

    def list_tools(self, current_user: Optional[User] = None) -> list[dict[str, Any]]:
        is_admin = getattr(current_user, "role", "USER") == "ADMIN" if current_user else False
        result = []
        for name, tool in self._tools.items():
            if tool.permission == "ADMIN" and not is_admin:
                continue
            result.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "permission": tool.permission,
                    "read_only": tool.read_only,
                }
            )
        return result

    def execute(
        self,
        tool_name: str,
        db: Session,
        current_user: User,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        tool = self.get_tool(tool_name)
        return tool.validate_and_execute(db, current_user, params)


# Global singleton Tool Registry
tool_registry = ToolRegistry()
