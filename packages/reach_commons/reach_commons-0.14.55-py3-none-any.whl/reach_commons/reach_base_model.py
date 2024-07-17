from datetime import date, datetime, time

from pydantic import BaseModel
from pydantic.v1 import validator


class ReachBaseModel(BaseModel):
    def model_dump(self, *args, **kwargs):
        original_dict = super().model_dump(*args, **kwargs)
        for key, value in original_dict.items():
            if isinstance(value, datetime):
                original_dict[key] = value.isoformat()
            elif isinstance(value, date):
                original_dict[key] = value.isoformat()
            elif isinstance(value, time):
                original_dict[key] = value.strftime("%H:%M:%S")
        return original_dict


class ReachDeserializeBaseModel(BaseModel):
    @validator("*", pre=True, always=True)
    def deserialize_values(cls, value, field):
        if isinstance(value, str):
            try:
                if field.type_ == datetime:
                    return datetime.fromisoformat(value)
                elif field.type_ == date:
                    return date.fromisoformat(value)
                elif field.type_ == time:
                    return datetime.strptime(value, "%H:%M:%S").time()
            except ValueError:
                pass  # Handle the case where the string is not in the expected format
        return value
