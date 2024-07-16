import hashlib
from dataclasses import asdict, dataclass, field
from enum import Enum, auto
from typing import Any, List, Optional


@dataclass
class Actor:
    # id: int = field(init=False)  # pk
    key: str  # phone number
    type: str
    name: str
    email: str
    # created: int = field(init=False)
    # updated: int = field(init=False)


@dataclass(order=True)
class Company:
    domain: str  # unique
    name: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    meta: dict = field(default_factory=dict)
    id: int = field(default=None)  # primary key
    uid: Optional[int] = field(default=None)  # foreign key

    # @property
    # def description(self):
    #     return self.meta.get("description", None)

    @property
    def ownership(self):
        ownership = self.meta.get("ownership", None)
        return self.get_ownership(ownership)

    @property
    def was_acquired(self):
        # GPT searches get a and a homepage. Starts with yes or no
        return self.meta.get("was_acquired", None)

    @property
    def products(self) -> str:
        # as csv
        return self.meta.get("products", None)

    @property
    def services(self) -> str:
        # as csv
        return self.meta.get("services", None)

    @staticmethod
    def get_ownership(ownership):
        if ownership == "Bootstrapped":
            return "Private"
        elif ownership == "Investor Backed":
            return "Venture Capital"
        else:
            return ownership


class EventType(str, Enum):
    CREATE = auto()
    ADVANCE = auto()
    VALIDATE = auto()
    SEND = auto()
    CLIENT_APPROVE = auto()
    CONFLICT = auto()
    REJECT = auto()
    CLIENT_REJECT = auto()
    CRITERIA = auto()


@dataclass
class Event:
    # fk # add index
    actor_key: str  # fk
    type: str  # enum
    search_uid: Optional[int] = None
    domain: Optional[str] = None  # fk
    data: dict = field(default_factory=dict)
    id: int = field(default=None)  # pk
    # created: int = field(init=False)


@dataclass
class Comment(Event):
    def __post_init__(self):
        # self.type = EventType.COMMENT
        assert isinstance(self.data["comment"], str)


@dataclass
class Rating(Event):
    def __post_init__(self):
        assert isinstance(self.data["rating"], int)


@dataclass
class Inclusion:
    keywords: List[str] = field(default_factory=list)
    employees_range: List[Any] = field(default_factory=lambda: [100, 500])
    ownership: List[str] = field(default_factory=lambda: ["bootstrapped"])
    country: List[str] = field(default_factory=lambda: ["USA"])
    state: List[str] = field(default_factory=list)
    city: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.employees_range[0] is None:
            self.employees_range[0] = 0
        if self.employees_range[1] is None:
            self.employees_range[1] = 100_000


@dataclass
class Exclusion:
    keywords: List[str] = field(default_factory=list)
    state: List[str] = field(default_factory=list)


@dataclass
class Criteria:
    inclusion: Inclusion = field(default_factory=Inclusion)
    exclusion: Exclusion = field(default_factory=Exclusion)
    result_count: int = 25
    operator: str = "any"


@dataclass
class Maps:
    phrase: str = ""
    areas: List[str] = field(default_factory=list)
    top_n: int = 1
    radius: int = 25
    prompt: str = ""


@dataclass
class Search:
    uid: int  # foreign key, dealcloud id
    label: str  # maps to dealcloud engagement name
    meta: dict = field(default_factory=dict)
    criteria: Criteria = field(default_factory=Criteria)
    # maps: Maps = field(default_factory=Maps)

    # uh what are these for?
    @property
    def notes(self) -> str:
        return self.meta.get("notes", None)

    @property
    def type(self) -> str:
        return self.meta.get("search_type", None)

    @property
    def prompt(self) -> str:
        return self.meta.get("prompt", None)

    @property
    def products(self) -> str:
        # as csv
        return self.meta.get("products", None)

    @property
    def services(self) -> str:
        # as csv
        return self.meta.get("services", None)

    @property
    def customers(self) -> str:
        # as csv
        return self.meta.get("customers", None)

    @property
    def token(self) -> str:
        # Create an MD5 hash of the uid converted to string
        return hashlib.md5(str(self.uid).encode("utf-8")).hexdigest()
