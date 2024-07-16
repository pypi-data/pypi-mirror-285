# coding: utf-8

"""
    FINBOURNE Luminesce Web API

    FINBOURNE Technology  # noqa: E501

    Contact: info@finbourne.com
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""


from __future__ import annotations
import pprint
import re  # noqa: F401
import json


from typing import Any, Dict, List, Optional
from pydantic.v1 import BaseModel, Field, StrictStr, conlist, constr
from luminesce.models.view_parameter import ViewParameter

class ConvertToViewData(BaseModel):
    """
    Representation of view data where will template the data into a 'create view' sql  # noqa: E501
    """
    query: constr(strict=True, min_length=1) = Field(..., description="view query")
    name: constr(strict=True, max_length=256, min_length=0) = Field(..., description="Name of view")
    description: Optional[constr(strict=True, max_length=256, min_length=0)] = Field(None, description="Description of view")
    documentation_link: Optional[constr(strict=True, max_length=256, min_length=0)] = Field(None, alias="documentationLink", description="Documentation link")
    view_parameters: Optional[conlist(ViewParameter)] = Field(None, alias="viewParameters", description="View parameters")
    other_parameters: Optional[Dict[str, StrictStr]] = Field(None, alias="otherParameters", description="Other parameters not explicitly handled by the ConvertToView generation.  These will be populated by the \"From SQL\" and should simply be returned by  the web GUI should the user edit / update / regenerate")
    starting_variable_name: Optional[StrictStr] = Field(None, alias="startingVariableName", description="Which variable the this start with, null if not started from a full Create View Sql Statement.")
    __properties = ["query", "name", "description", "documentationLink", "viewParameters", "otherParameters", "startingVariableName"]

    class Config:
        """Pydantic configuration"""
        allow_population_by_field_name = True
        validate_assignment = True

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.dict(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> ConvertToViewData:
        """Create an instance of ConvertToViewData from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of each item in view_parameters (list)
        _items = []
        if self.view_parameters:
            for _item in self.view_parameters:
                if _item:
                    _items.append(_item.to_dict())
            _dict['viewParameters'] = _items
        # set to None if description (nullable) is None
        # and __fields_set__ contains the field
        if self.description is None and "description" in self.__fields_set__:
            _dict['description'] = None

        # set to None if documentation_link (nullable) is None
        # and __fields_set__ contains the field
        if self.documentation_link is None and "documentation_link" in self.__fields_set__:
            _dict['documentationLink'] = None

        # set to None if view_parameters (nullable) is None
        # and __fields_set__ contains the field
        if self.view_parameters is None and "view_parameters" in self.__fields_set__:
            _dict['viewParameters'] = None

        # set to None if other_parameters (nullable) is None
        # and __fields_set__ contains the field
        if self.other_parameters is None and "other_parameters" in self.__fields_set__:
            _dict['otherParameters'] = None

        # set to None if starting_variable_name (nullable) is None
        # and __fields_set__ contains the field
        if self.starting_variable_name is None and "starting_variable_name" in self.__fields_set__:
            _dict['startingVariableName'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> ConvertToViewData:
        """Create an instance of ConvertToViewData from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return ConvertToViewData.parse_obj(obj)

        _obj = ConvertToViewData.parse_obj({
            "query": obj.get("query"),
            "name": obj.get("name"),
            "description": obj.get("description"),
            "documentation_link": obj.get("documentationLink"),
            "view_parameters": [ViewParameter.from_dict(_item) for _item in obj.get("viewParameters")] if obj.get("viewParameters") is not None else None,
            "other_parameters": obj.get("otherParameters"),
            "starting_variable_name": obj.get("startingVariableName")
        })
        return _obj
