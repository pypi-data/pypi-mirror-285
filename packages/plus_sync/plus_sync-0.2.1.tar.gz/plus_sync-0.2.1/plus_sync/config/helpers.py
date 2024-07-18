from attrs import field
from attrs.validators import and_
from attrs_strict import type_validator


def validated_field(*args, validator=None, **kwargs):
    validators = and_(type_validator(), validator) if validator else type_validator()

    return field(*args, validator=validators, **kwargs)


def validate_duplicate_names(instance, attribute, value):
    all_names = instance.get_all_config_names()
    if not all_names:
        return
    if len(all_names) != len(set(all_names)):
        raise ValueError('Duplicate names are not allowed.')
