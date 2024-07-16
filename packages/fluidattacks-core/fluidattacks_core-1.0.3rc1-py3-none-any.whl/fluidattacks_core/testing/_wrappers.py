from _pytest.mark.structures import (
    MarkGenerator,
)
import pytest as _pytest

# Custom fixture object for replacing the pytest.fixture element.
injectable = _pytest.fixture

# Custom tag object for replacing the pytest.mark element.
tag = MarkGenerator(_ispytest=True)

# Tag is passed as reference, so any modification will be reflected in the
# pytest.mark element.
_pytest.mark = tag
