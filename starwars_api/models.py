from urlparse import urlparse

from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError

api_client = SWAPIClient()


class BaseModel(object):

    def __init__(self, json_data):
        """
        Dynamically assign all attributes in `json_data` as instance
        attributes of the Model.
        """
        for key, value in json_data.items():
            setattr(self, key, value)

    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        """
        resource = getattr(cls, 'RESOURCE_NAME')
        return cls(getattr(api_client, 'get_' + resource)(resource_id))

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        resource = getattr(cls, 'RESOURCE_NAME')
        return globals()[resource.capitalize() + 'QuerySet'](getattr(api_client, 'get_' + resource)(page=1), resource)


class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'

    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        return 'Person: {0}'.format(self.name)


class Films(BaseModel):
    RESOURCE_NAME = 'films'

    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        return 'Film: {0}'.format(self.title)


class BaseQuerySet(object):

    def __init__(self, json_data, resource):
        self.current = 0
        self.page = 1
        self.json_data = json_data
        self.count_total = json_data['count']
        self.objects = json_data['results']
        self.resource = resource

    def __iter__(self):
        """
        Resets the iterable elements back to their original values
        """
        self.current = 0
        self.page = 1
        self.objects = self.json_data['results']
        return self

    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        if self.current == self.count():
            raise StopIteration()
        
        if len(self.objects) == 0:
            new_data = api_client.get_people(page=self.page)
            self.objects = new_data["results"]
            self.current += 1
            return globals()[self.resource.capitalize()](self.objects.pop(0))
        else:
            self.current += 1
            return globals()[self.resource.capitalize()](self.objects.pop(0))

    next = __next__

    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        return self.count_total


class PeopleQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'people'

    def __init__(self, json_data, resource):
        super(PeopleQuerySet, self).__init__(json_data, resource)

    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(len(self.objects)))


class FilmsQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'films'

    def __init__(self, json_data, resource):
        super(FilmsQuerySet, self).__init__(json_data, resource)

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(len(self.objects)))
