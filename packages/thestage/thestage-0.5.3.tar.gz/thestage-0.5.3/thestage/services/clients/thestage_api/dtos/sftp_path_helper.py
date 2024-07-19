from pydantic import BaseModel, Field


class SftpPathHelper(BaseModel):

    tmp_container_path: str = Field(None)
    tmp_instance_path: str = Field(None)
    tmp_folder_path: str = Field(None)
    item_name: str = Field(None)

    def tmp_container_path_with_name(self) -> str:
        return f"{self.tmp_container_path}/{self.item_name}"

    def tmp_instance_path_with_name(self) -> str:
        return f"{self.tmp_instance_path}/{self.item_name}"
