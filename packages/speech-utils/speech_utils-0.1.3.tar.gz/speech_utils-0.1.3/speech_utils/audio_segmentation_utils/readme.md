# data-models for audio segmentation
## motivation
- conventional approach (no data-validation at all)
- `segments: list[tuple[float,float]]= [(1.0, 2.0),(1.0, 1.0), (2.0, 3.0)]`
- issue: might be unordered, overlapping, empty duration, etc.
### data-validating data-models to the rescue
- guarantee that segments are "valid" comply with certain constraints
- example `NeMsTimeSpanNeTextNeNoSeg`
```python
@dataclass
class NeMsTimeSpanNeTextNeNoSeg(TextNeNoSeg[NeMsTimeSpanNeText]):
    segments: NeSequence[
        NeMsTimeSpanNeText
    ]  # necessary to trigger beartypes type checking
```
- `NeMsTimeSpan` -> non empty Millisecond Time Span
- `NeText` -> non empty text-attribute
- `NeNoSeg` -> non empty non overlapping segments