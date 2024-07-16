# data models based on `DataValidationCoopMixinBase`
- one should use `composition above inheritance` but what about `multi-inheritance as composition`?
  - maybe its a little crazy but its interesting!
  - well actually one really goes straight into multi-inheritance hell! but one can partially get out of it by using protocols
### motivation
#### conventional approach -> one dataclass for every "data-model"
- data-validation in `__post_init__` (or via pydantic)
```python
@dataclass
class NeTimeSpanNeTextConventional:
    """
    konventional way with data-validation in __post_init__
    """
    start: float
    end: float
    text: str

    def __post_init__(self):
        if self.start < 0 or self.end <= self.start:
            raise ValueError(f"{self.start=} > {self.end=}")
        if len(self.text) == 0:
            raise ValueError(f"{self.text=} is empty")

```
- issues: 
  - what if I wanted a class with some more attributes like `audio_array` -> inheritance? copy-paste everything?
  - what if I wanted a class with `start`, `end` and `audio_array` but NOT `text` -> inheritance? copy-paste everything?

#### composition
- issue: is annoying to instantiate: `NeTimeSpanNeTextComposition(NeText("bla"), NeTimeSpan(0, 1))`  
```python
@dataclass
class NeTimeSpan:
    """NonEmpty TimeSpan"""

    start: float
    end: float

    def __post_init__(self):
        if self.start < 0 or self.end <= self.start:
            raise ValueError(f"{self.start=} > {self.end=}")

@dataclass
class NeText:
    text: str

    def __post_init__(self) -> None:
        if len(self.text) == 0:
            raise ValueError(f"{self.text=} is empty")


@dataclass
class NeTimeSpanNeTextComposition:
    """
    time-span AND text are non-empty!
    """
    ne_text: NeText
    ne_time_span: NeTimeSpan
    
```
#### cooperative multiple inheritance
- instantiation looks like: `NeTimeSpanNeText(start=0.0, end=1.0, text="foo")`
- pro: one can "compose" data-models via multi-inheritance
- con: multi-inheritance!
```python

@dataclass
class NeTimeSpan(DataValidationCoopMixinBase):
    """NonEmpty TimeSpan"""

    start: float
    end: float

    def _parse_validate_data(self) -> None:
        if self.start < 0 or self.end <= self.start:
            raise CoopDataValidationError(f"{self.start=} > {self.end=}")
        super()._parse_validate_data() # calling super means being cooperative!


@dataclass
class NeText(DataValidationCoopMixinBase):
    text: str

    def _parse_validate_data(self) -> None:
        # in theory one could also call super()._parse_validate_data() here, which would change the order of validation
        if len(self.text) == 0:
            raise CoopDataValidationError(f"{self.text=} is empty")
        super()._parse_validate_data()


@dataclass
class NeTimeSpanNeText(NeText, NeTimeSpan): # multi-inheritance here! every parent implements "_parse_validate_data"-method, these are called following pythons MRO
    """
    time-span AND text are non-empty!
    """

```