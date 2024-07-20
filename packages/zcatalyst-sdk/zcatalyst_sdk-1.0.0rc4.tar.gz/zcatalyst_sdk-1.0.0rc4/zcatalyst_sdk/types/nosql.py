from typing import List, Literal, Optional, TypedDict, Dict, Set, Union

NoSqlAttributeType = Literal["keys_only", "all", "include"]

NoSqlGroupOperator = Literal["AND", "OR"]

NoSqlCrudOperation = Literal["create", "read", "update", "delete"]

NoSqlUpdateOperation = Literal["PUT", "DELETE"]

NoSqlOperator = Literal[
    "contains",
    "begins_with",
    "not_contains",
    "ends_with",
    "in",
    "not_in",
    "between",
    "not_between",
    "equals",
    "not_equals",
    "greater_than",
    "less_than",
    "greater_equal",
    "less_equal",
]

ItemType = Literal["S", "N", "B", "L", "M", "SS", "SB", "SN", "BOOL"]

NoSqlSecondaryKeyCondition = Literal[
    "begins_with",
    "between",
    "equals",
    "greater_than",
    "less_than",
    "greater_equal",
    "less_equal",
]

ReturnType = Literal["NEW", "OLD", "NULL"]


class NoSqlKeyItems(TypedDict):
    S: str
    N: int


class NoSqlItemValues(NoSqlKeyItems):
    B: Union[bytes, bytearray]
    SS: Set[str]
    SB: Set[Union[bytes, bytearray]]
    SN: Set[int]
    BOOL: bool
    L: List["NoSqlItemValues"]
    M: Dict[str, "NoSqlItemValues"]


class CatalystSysUser(TypedDict):
    user_id: str
    user_type: str
    email_id: str
    first_name: str
    last_name: str
    zuid: Optional[str]
    is_confirmed: Optional[bool]


class CatalystProjectInfo(TypedDict):
    id: str
    project_name: str
    project_type: str


class CatalystNoSqlKeyInfo(TypedDict):
    column_name: str
    data_type: str


class NoSqlTableResponse(TypedDict):
    id: str
    api_access: bool
    created_by: CatalystSysUser
    created_time: str
    modified_by: CatalystSysUser
    modified_time: str
    name: str
    partition_key: CatalystNoSqlKeyInfo
    project_id: CatalystProjectInfo
    sort_by: CatalystNoSqlKeyInfo
    status: str
    ttl_attribute: str
    ttl_enabled: bool
    type: str


ProjectedAttribute = TypedDict(
    "ProjectedAttribute",
    {
        "type": str,
    },
)


class NoSqlIndexRes(TypedDict):
    created_by: CatalystSysUser
    created_time: str
    id: str
    modified_by: CatalystSysUser
    modified_time: str
    name: str
    partition_key: CatalystNoSqlKeyInfo
    project_id: CatalystProjectInfo
    projected_attributes: ProjectedAttribute
    sort_key: CatalystNoSqlKeyInfo
    status: str
    type: str


class NoSqlTableResourceRes(TypedDict):
    additional_sort_keys: List[NoSqlIndexRes]
    api_access: bool
    created_by: CatalystSysUser
    created_time: str
    global_index: List[NoSqlIndexRes]
    id: str
    modified_by: CatalystSysUser
    modified_time: str
    name: str
    partition_key: CatalystNoSqlKeyInfo
    project_id: CatalystProjectInfo
    sort_key: CatalystNoSqlKeyInfo
    status: str
    ttl_enabled: bool
    type: str

class AttributePath:
    attribute_path: List[str]


class NoSqlItemUpdateAttributeOperation(AttributePath):
    operation_type: NoSqlUpdateOperation
    update_value: NoSqlItemValues


class NoSqlFunctionCondition(TypedDict):
    function_name: Literal["attribute_exits", "attribute_type"]
    args: AttributePath


class NoSqlConditionFuncOperation:
    function: Optional[NoSqlFunctionCondition]


class NoSqlAttributeCondition(TypedDict):
    attribute: Optional[NoSqlAttributeType]
    operator: Optional[NoSqlOperator]
    value: NoSqlItemValues


class NoSqlGroupCondition(TypedDict):
    group_operator: Optional[str]
    group: Optional["NoSqlCondition"]
    negate: bool


NoSqlCondition = Union[
    NoSqlAttributeCondition, NoSqlGroupCondition, NoSqlConditionFuncOperation
]

# class NoSqlReturnType:
#     return

# class NoSqlInsertItemReq(NoSqlReturnType):
#     item: NoSqlItemValues
#     condition: Optional[NoSqlCondition]

NoSqlInsertItemReq = TypedDict('NoSqlInsertItemReq', {
    'item': NoSqlItemValues,
    'condition': Optional[NoSqlCondition],
    'return': ReturnType
})


class NoSqlFetchItemReq(TypedDict):
    keys: List[NoSqlKeyItems]
    required_objects: List[str]


class NoSqlDeleteItemReq(TypedDict):
    keys: NoSqlKeyItems
    condition: Optional[NoSqlCondition]


class NoSqlUpdateItemReq(TypedDict):
    keys: NoSqlKeyItems
    condition: Optional[NoSqlCondition]
    update_attributes: List[NoSqlItemUpdateAttributeOperation]


class NoSqlQueryItemReq(TypedDict):
    consistent_read: bool
    key_condition: NoSqlCondition
    other_condition: Optional[NoSqlCondition]
    secondaryKeyCondition: Optional[NoSqlCondition]
    limit: int
    forwardScan: bool
    startKey: NoSqlKeyItems
    additional_sort_key: str
