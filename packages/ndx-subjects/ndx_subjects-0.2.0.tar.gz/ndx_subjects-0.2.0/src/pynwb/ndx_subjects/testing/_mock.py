from typing import Literal

import ndx_subjects


def mock_CElegansSubject(
    *,
    subject_id: str = "subject_1",
    description: str = "A description about this particular subject.",
    c_elegans_sex: Literal["XX", "XO"] = "XX",
    growth_stage: Literal[
        "two-fold",
        "three-fold",
        "L1",
        "L2",
        "L3",
        "L4",
        "YA",
        "OA",
        "dauer",
        "post-dauer L4",
        "post-dauer YA",
        "post-dauer OA",
    ] = "YA",
    growth_stage_time: str = "P0DT2H30M0S",
    cultivation_temp: float = 20.0,
) -> ndx_subjects.CElegansSubject:
    """A mock generator of an ndx_subjects.CElegansSubject object for rapid testing."""
    c_elegans_subject = ndx_subjects.CElegansSubject(
        subject_id=subject_id,
        description=description,
        c_elegans_sex=c_elegans_sex,
        growth_stage=growth_stage,
        growth_stage_time=growth_stage_time,
        cultivation_temp=cultivation_temp,
    )

    return c_elegans_subject
