try:
    # NOTE: Supported since API v2.22
    from byteblowerll.byteblower import (
        UnsupportedFeature as CompatUnsupportedFeature,
    )
except ImportError:
    from byteblowerll.byteblower import DomainError as CompatUnsupportedFeature

__all__ = ('CompatUnsupportedFeature',)
