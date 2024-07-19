from pydantic import BaseModel, ConfigDict, Field


class File(BaseModel):
    """
    This class represents a file that is stored in the database.
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )
    file_name_for_docstore: str | None = Field(default=None, title="File Name For Docstore")
    folder_name_for_docstore: str | None = Field(default=None, title="Folder Name For Docstore")
    file: bytes = Field(..., title="File")
