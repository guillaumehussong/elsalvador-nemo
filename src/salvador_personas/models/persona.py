from dataclasses import dataclass
from typing import Literal

EconomicRole = Literal["merchant", "consumer", "both", "inactive"]

NARRATIVE_COLUMNS = (
    "professional_persona",
    "sports_persona",
    "arts_persona",
    "travel_persona",
    "culinary_persona",
    "family_persona",
    "persona",
    "cultural_background",
    "skills_and_expertise",
    "skills_and_expertise_list",
    "hobbies_and_interests",
    "hobbies_and_interests_list",
    "career_goals_and_ambitions",
)

STRUCTURED_COLUMNS = (
    "uuid",
    "sex",
    "age",
    "marital_status",
    "household_type",
    "education_level",
    "occupation",
    "area",
    "municipality",
    "department",
    "languages_spoken",
    "country",
)


@dataclass(frozen=True)
class ParsedTags:
    digital_score: float
    consumption_tags: tuple[str, ...]


@dataclass(frozen=True)
class DerivedFields:
    income_usd_monthly: float
    economic_role: EconomicRole
    adoption_propensity: float


@dataclass(frozen=True)
class PersonaFilter:
    departments: tuple[str, ...] | None = None
    municipalities: tuple[str, ...] | None = None
    occupations: tuple[str, ...] | None = None
    age_min: int | None = None
    age_max: int | None = None
    area: Literal["urbano", "rural"] | None = None
    sex: Literal["Femenino", "Masculino"] | None = None
    income_min: float | None = None


@dataclass(frozen=True)
class Persona:
    uuid: str
    sex: str
    age: int
    marital_status: str
    household_type: str
    education_level: str
    occupation: str
    area: str
    municipality: str
    department: str
    languages_spoken: str
    narratives: dict[str, str]
    backstory: str
    tags: ParsedTags
    derived: DerivedFields
