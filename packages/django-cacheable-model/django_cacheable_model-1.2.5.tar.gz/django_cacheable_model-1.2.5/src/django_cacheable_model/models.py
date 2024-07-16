from django.db import models


class CacheableModel(models.Model):
    # Update this version when model changes (migrations) to differentiate model versions in cache
    version = 1

    """
    When model appears as a Foreignkey or one-to-one, 'related_cache_fieldname' is the model field from which the value
    is taken for cache key. For example: as cache key for Player totals may need to indicate the player (foreign key)
    whose total is cached. We need the id of the Player (foreign key field player) in the cache key for PlayerTotals.
    Example key: PlayerTotals.10.player.<related_cache_fieldname>
    """

    related_cache_fieldname = 'id'

    @classmethod
    def cache_key_all(cls) -> str:
        return f'{cls.__name__}.v{cls.version}.all'

    @classmethod
    def ins_cache_key_with_field_values(cls, fields: dict) -> str:
        """
        Calling code has iterable of field, value pairs. It needs the cache key for the model
        based on those fields, values pairs.
        @param fields: a dict. key is usually model field's name. value is model field's value.
                    It can be anything that works with objects.filter(**fields).
        """
        # To maintain cache key consistency, key is made from sorted field names
        fields_values = sorted(
            [(field, value) for field, value in fields.items()],
            key=lambda entry: entry[0],
        )
        key_parts = [f'{cls.__name__}.v{cls.version}']
        # For each pair, check if the value is again a model
        for index, (field, value) in enumerate(fields_values):
            if issubclass(value.__class__, models.Model):
                # use the model's (field's) related_cache_fieldname for value
                key_parts.append(
                    f'{field}.{getattr(value, value.related_cache_fieldname)}'
                )
            else:
                # Value is a python object
                key_parts.append(f'{field}.{value}')

        return '.'.join(key_parts).replace(' ', '')

    def ins_cache_key_on_fields(self, fields=('id',)) -> str:
        """
        Make a cache key using this instance's values for 'fields'. Defaults to just using 'id' field.
        @param fields: iterable list or tuple of field names.
        @return: cache key.
        """
        field_values = {field: getattr(self, field) for field in fields}
        return self.__class__.ins_cache_key_with_field_values(field_values)

    class Meta:
        abstract = True
