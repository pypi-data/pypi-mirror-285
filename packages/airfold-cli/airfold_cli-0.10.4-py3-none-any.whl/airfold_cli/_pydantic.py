from pydantic.version import VERSION as PYDANTIC_VERSION

PYDANTIC_V2 = PYDANTIC_VERSION.startswith("2.")

if PYDANTIC_V2:
    from pydantic.v1 import (  # type: ignore[assignment]
        BaseModel,
        Extra,
        Field,
        SecretStr,
        validator,
    )
else:
    from pydantic import (  # type: ignore[assignment]
        BaseModel,
        Extra,
        Field,
        SecretStr,
        validator,
    )
