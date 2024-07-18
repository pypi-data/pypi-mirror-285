from pydantic import BaseModel, Field, ConfigDict


class ProblemDetails(BaseModel):
    type: str | None = None
    title: str | None = None
    status: int | None = None
    detail: str | None = None
    instance: str | None = None

    def __str__(self):
        message = [f"  {key}: {value}" for key, value in self.model_dump().items() if value]
        return str.join("\n", message)
