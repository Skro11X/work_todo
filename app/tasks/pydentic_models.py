from pydantic import BaseModel, computed_field


class CreateTask(BaseModel):
    title: str
    project: str
    organisation: str
    description: str

    @computed_field
    def status(self) -> int:
        return 0