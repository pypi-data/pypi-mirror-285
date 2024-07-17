from typing import Any

from pydantic import BaseModel, Field


class Option(BaseModel):
    Value: str = Field(alias="value", default=None)
    Function: str = Field(alias="function", default=None)


class BaseConfig(BaseModel):
    Code: str = Field(alias="code", default=None)
    Label: str = Field(alias="label", default=None)
    Enabled: str = Field(alias="enabled", default=None)
    OnClick: str = Field(alias="on_click", default=None)
    OnChange: str = Field(alias="on_change", default=None)
    Tab: str = Field(alias="tab", default="Main")
    Default: Any = Field(default=None, alias="default")
    DefaultFunction: str = Field(default=None, alias="default_function")
    Extension: str = Field(default=None, alias="extension")
    Immutable: bool = Field(default=False, alias="immutable")
    Key: str = Field(default=None, alias="key")
    InputOptions: list[Option] = Field(default=None, alias="options")


class Button(BaseConfig):
    Variant: str = Field(default="secondary", alias="variant")


class Tab(BaseConfig):
    pass


class InputFieldsBase(BaseConfig):
    Type: str = Field(default="text_input", alias="type")
    Required: bool = Field(default=False, alias="required")
    Min: int = Field(default=None, alias="min")
    Max: int = Field(default=None, alias="max")
    Order: str = Field(default=None, alias="order")
    Function: str = Field(alias="function", default=None)


class InputFields(InputFieldsBase):
    Image: str = Field(default=None, alias="image")
    Columns: list[InputFieldsBase] = Field(default=[], alias="columns")


class UserInterface(BaseConfig):
    Name: str = Field(alias="name")
    Description: str = Field(alias="description", default=None)
    Developer: str = Field(alias="developer")
    Concept: str = Field(alias="concept")
    Title: bool = Field(default=False, alias="title")
    Inputs: list[InputFields] = Field(default=[], alias="inputs")
    Tabs: list[Tab] = Field(default=[], alias="tabs")
    Buttons: list[Button] = Field(default=[], alias="buttons")
