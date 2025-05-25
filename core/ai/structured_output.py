from pydantic import BaseModel, Field


class ScholarshipListItem(BaseModel):
    url: str = Field(description="A link to scholarship details.")
    title: str = Field(description="The name of the scholarship program.")
    
class ScholarshipDetail(BaseModel):
    title: str = Field(description="The official name of the scholarship program.")
    url: str = Field(
        description="A link to scholarship details."
    )
    degree: list[str] = Field(
        description="Academic level supported by the scholarship. Valid options are: Bachelor's, Master's, PhD, Postdoc"

    )
    deadline: str = Field(
        description="Final date by which the application must be submitted (format: YYYY-MM-DD)."
    )
    registration_start_date: str = Field(
        description="Date when the application process opens (format: YYYY-MM-DD)."
    )
    description: str = Field(
        description="A concise overview of the scholarship’s purpose, sponsor, and target audience."
    )
    requirements: list[str] = Field(
        description="List of mandatory eligibility criteria (e.g., academic qualifications, language proficiency, experience)."
    )
    country: list[str] = Field(
        description="Full official name of the country where the scholarship is offered. Do NOT use abbreviations. For example: United Kingdom, not UK."
    )
    type: str = Field(
        description="Indicates the funding structure of the scholarship. Valid options are: Full ride, Partial, Merit-based, Need-based, Research-based, Athletic"
    )
    benefits: list[str] = Field(
        description="Specific advantages provided by the scholarship (e.g., tuition waiver, stipend, travel allowance)."
    )
    must_relocate: bool = Field(
        description="Indicates whether the scholarship requires the student to relocate to the study location."
    ),
    study_format: str = Field(
        description="The format of the study, valid formats are: in-person, online, hybrid"
    )


class ScholarshipList(BaseModel):
    scholarships: list[ScholarshipListItem]
