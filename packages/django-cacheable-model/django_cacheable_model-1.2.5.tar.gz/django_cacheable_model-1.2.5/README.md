# django cacheable model
A cacheable model for django.

* A generic way of creating cache keys from Django model fields
* Retrieve django models from cache with field values (cache on the way if cache missed)
* Retrieve all the model instances (suitable for small set of models)
* Support for cache aliases

See usage example below

# 1. Install
pip install django_cacheable_model

# 2. Configuration
* `DEFAULT_CACHE_ALIAS` the default cache name to use from `settings.CACHES`. 
   If not set default alias is name `"default"` and must be configured in CACHES.
* `CACHE_SET_MANY_LIMIT` is chunk size for calls to `cache.set_many`.  
   when `all_ins_from_cache` brings in all entries from cache, it will set each object  
   in chunks to control request size. Default is `5` i.e if there are 10 instances of a model  
   from db this config will set each of the models to the cache in two groups of `5`
```python
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CACHE_DEFAULT_ALIAS = 'example_cache_alias'
CACHE_SET_MANY_LIMIT = 10
CACHES = {
   ...,
    'example_cache_alias': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': 'memcached:11211',
    },
    ...
}
```

# 3. Usage

See samples in  `example_django_project` views.py and models.py.

### 3.1. Create a model that inherits from CacheableModel
```python
class Question(CacheableModel):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')


class Choice(CacheableModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
```

### 3.2. Use cache operations from django_cacheable_model.utils

```python
from django_cacheable_model.utils import all_ins_from_cache, model_ins_from_cache

# Get all instances of model from cache (use for smaller set of models)
context['choices'] = all_ins_from_cache(Choice)

# Get all instances with select_related and order_by
choices = all_ins_from_cache(Choice,
                             select_related=('question',),
                             order_by_fields=('-id',))

# Get a single model. Note this method returns a list of matching objects
context['choice'] = model_ins_from_cache(Choice, {'id': 5})[-1]
```

# 4. License
Apache2 License
