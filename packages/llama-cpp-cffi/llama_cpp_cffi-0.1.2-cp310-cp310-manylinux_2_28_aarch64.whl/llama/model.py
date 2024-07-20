__all__ = ['Model']

from attrs import define, field


@define
class Model:
    creator_hf_repo: str
    hf_repo: str
    hf_file: str


    def __str__(self):
        return f'{creator_hf_repo}:{hf_repo}:{hf_file}'
