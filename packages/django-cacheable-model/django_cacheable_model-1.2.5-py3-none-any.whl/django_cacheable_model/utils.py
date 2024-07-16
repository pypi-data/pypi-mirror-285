from typing import Iterable

from django.conf import settings
from django.core.cache import caches
from django.db import models

cache_set_many_limit = getattr(settings, 'CACHE_SET_MANY_LIMIT', 5)
default_cache_alias = getattr(settings, 'DEFAULT_CACHE_ALIAS', 'default')


def chunked_list(long_list, chunk_size=20):
    """Break a long list into chunks"""
    for i in range(0, len(long_list), chunk_size):
        yield long_list[i : i + chunk_size]


def all_ins_from_cache(
    model_cls,
    order_by_fields=None,
    select_related=(None,),
    prefetch_objs=(None,),
    cache_alias=default_cache_alias,
) -> Iterable:
    """
    For Model class model_cls get 'all' instances from cache or get from DB and update cache.
    Depending on the size of the table, this may become unviable. So use on small tables.
    @param model_cls: Django model class
    @param order_by_fields: as it would work in Django queryset doc.
    @param select_related: tuple of fields to apply to queryset select_related
    @param prefetch_objs: tuple of Prefetch class objects. *WARNING* on size of prefetched rows. Bring in only needed
    columns using .only on Prefetch queryset. Ensure .only also has foreign keys.
    Example: PageWordCount.objects.all().only('id', 'created_at', 'web_page').order_by('-created_at')
    Ref: https://docs.djangoproject.com/en/4.2/ref/models/querysets/#prefetch-objects
    @param cache_alias: name of cache in Django's CACHES settings
    @return: list of all instances of model_cls currently in db
    """
    assert model_cls is not None
    assert issubclass(model_cls, models.Model)
    cache = caches[cache_alias]
    cache_key = model_cls.cache_key_all()

    instances = cache.get(cache_key)
    if instances is None:
        if not order_by_fields:
            order_by_fields = (model_cls._meta.pk.name,)
        instances = list(
            model_cls.objects.all()
            .select_related(*select_related)
            .prefetch_related(*prefetch_objs)
            .order_by(*order_by_fields)
        )
        each_ins_dict = {}
        if len(instances):
            # loop in chunked lists
            for chunk in chunked_list(instances, chunk_size=cache_set_many_limit):
                # For each model instance set the cache entries by pk
                each_ins_dict.update(
                    {
                        instance.ins_cache_key_on_fields(): (instance,)
                        for instance in chunk
                    }
                )
                cache.set_many(each_ins_dict)
                each_ins_dict.clear()
            # set the cache entry for all
            cache.set(cache_key, instances)
    return instances


def model_ins_from_cache(
    model_cls,
    fields: dict,
    latest_field_name: str = None,
    select_related: Iterable = (None,),
    prefetch_objs: Iterable = (None,),
    cache_alias=default_cache_alias,
) -> Iterable:
    """
    Try to get cached model instance with primary key pk. If not get from db and store in cache.
    @param model_cls: Django model class
    @param fields: dict key value pairs
    @param latest_field_name: model with most recent value of this field will be fetched.
    @param select_related: Tuple (iterable) of fields to apply to queryset select_related
    @param prefetch_objs: Tuple (iterable) of Prefetch class objects. *WARNING* on size of prefetched rows. Bring in only needed
    columns using .only on Prefetch queryset. Ensure .only also has foreign keys.
    Example: Choice.objects.all().only('id', 'created_at', 'question').order_by('-created_at')
    Ref: https://docs.djangoproject.com/en/4.2/ref/models/querysets/#prefetch-objects
    @param cache_alias: name of cache in Django's CACHES settings
    @return: Tuple of model instances that match or (None, ) if not found
    """
    assert model_cls is not None
    assert issubclass(model_cls, models.Model)
    assert len(fields) > 0

    cache = caches[cache_alias]
    cache_key = model_cls.ins_cache_key_with_field_values(fields)
    model_ins = cache.get(cache_key)
    if model_ins is None:
        try:
            # queryset
            model_ins = (
                model_cls.objects.filter(**fields)
                .select_related(*select_related)
                .prefetch_related(*prefetch_objs)
            )
            if latest_field_name:
                model_ins = (model_ins.latest(latest_field_name),)
            else:
                model_ins = tuple(model_ins)

            if model_ins:
                cache.set(cache_key, model_ins)
            else:
                model_ins = (None,)
        except Exception:
            return (None,)

    return model_ins
