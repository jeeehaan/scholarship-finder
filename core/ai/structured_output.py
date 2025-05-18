from pydantic import BaseModel, Field


class ScholarshipListItem(BaseModel):
    url: str = Field(description="A link to scholarship details.")
    title: str = Field(description="The official name of the scholarship program.")
    
class ScholarshipDetail(BaseModel):
    title: str = Field(description="The official name of the scholarship program.")
    url: str = Field(
        description="A link to scholarship details."
    )
    degree: str = Field(
        description="Academic level supported by the scholarship. "
                    "Valid options are: Bachelor's, Master's, PhD, exchange."
                    "Choose only one."
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
    country: str = Field(
        description="Geographic location where the study will take place or where the scholarship is offered."
    )
    type: str = Field(
        description="Indicates the funding structure of the scholarship (e.g., Fully funded, Partially funded, Exchange program). Return only one value."
    )
    benefits: list[str] = Field(
        description="Specific advantages provided by the scholarship (e.g., tuition waiver, stipend, travel allowance)."
    )


class ScholarshipList(BaseModel):
    scholarships: list[ScholarshipListItem]
