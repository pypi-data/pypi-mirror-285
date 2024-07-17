from typing import ClassVar, Optional

from .exceptions import MissingEqualityImplementation, ObjectIsInvalid, RawRequestEndpointMissing


class ReadonlyApiObject:
    def __init__(self, allspice_client):
        self.allspice_client = allspice_client
        self.deleted = False  # set if .delete was called, so that an exception is risen

    def __str__(self):
        return "AllSpiceObject (%s):" % (type(self))

    def __eq__(self, other):
        """Compare only fields that are part of the gitea-data identity"""
        raise MissingEqualityImplementation()

    def __hash__(self):
        """Hash only fields that are part of the gitea-data identity"""
        raise MissingEqualityImplementation()

    _fields_to_parsers: ClassVar[dict] = {}

    @classmethod
    def request(cls, allspice_client):
        if hasattr("API_OBJECT", cls):
            return cls._request(allspice_client)
        else:
            raise RawRequestEndpointMissing()

    @classmethod
    def _request(cls, allspice_client, args):
        result = cls._get_gitea_api_object(allspice_client, args)
        api_object = cls.parse_response(allspice_client, result)
        return api_object

    @classmethod
    def _get_gitea_api_object(cls, allspice_client, args):
        """Retrieving an object always as GET_API_OBJECT"""
        return allspice_client.requests_get(cls.API_OBJECT.format(**args))

    @classmethod
    def parse_response(cls, allspice_client, result) -> "ReadonlyApiObject":
        # allspice_client.logger.debug("Found api object of type %s (id: %s)" % (type(cls), id))
        api_object = cls(allspice_client)
        cls._initialize(allspice_client, api_object, result)
        return api_object

    @classmethod
    def _initialize(cls, allspice_client, api_object, result):
        for name, value in result.items():
            if name in cls._fields_to_parsers and value is not None:
                parse_func = cls._fields_to_parsers[name]
                value = parse_func(allspice_client, value)
            cls._add_read_property(name, value, api_object)
        # add all patchable fields missing in the request to be writable
        for name in cls._fields_to_parsers.keys():
            if not hasattr(api_object, name):
                cls._add_read_property(name, None, api_object)

    @classmethod
    def _add_read_property(cls, name, value, api_object):
        if not hasattr(api_object, name):
            setattr(api_object, "_" + name, value)
            prop = property((lambda n: lambda self: self._get_var(n))(name))
            setattr(cls, name, prop)
        else:
            raise AttributeError(f"Attribute {name} already exists on api object.")

    def _get_var(self, name):
        if self.deleted:
            raise ObjectIsInvalid()
        return getattr(self, "_" + name)


class ApiObject(ReadonlyApiObject):
    _patchable_fields: ClassVar[set[str]] = set()

    def __init__(self, allspice_client):
        super().__init__(allspice_client)
        self._dirty_fields = set()

    def _commit(self, route_fields: dict, dirty_fields: Optional[dict] = None):
        if self.deleted:
            raise ObjectIsInvalid()
        if not hasattr(self, "API_OBJECT"):
            raise RawRequestEndpointMissing()

        if dirty_fields is None:
            dirty_fields = self.get_dirty_fields()

        self.allspice_client.requests_patch(
            self.API_OBJECT.format(**route_fields),
            dirty_fields,
        )
        self._dirty_fields = set()

    def commit(self):
        raise NotImplementedError()

    _parsers_to_fields: ClassVar[dict] = {}

    def get_dirty_fields(self):
        dirty_fields_values = {}
        for field in self._dirty_fields:
            value = getattr(self, field)
            if field in self._parsers_to_fields:
                dirty_fields_values[field] = self._parsers_to_fields[field](value)
            else:
                dirty_fields_values[field] = value
        return dirty_fields_values

    @classmethod
    def _initialize(cls, allspice_client, api_object, result):
        super()._initialize(allspice_client, api_object, result)
        for name in cls._patchable_fields:
            cls._add_write_property(name, None, api_object)

    @classmethod
    def _add_write_property(cls, name, value, api_object):
        if not hasattr(api_object, "_" + name):
            setattr(api_object, "_" + name, value)
        prop = property(
            (lambda n: lambda self: self._get_var(n))(name),
            (lambda n: lambda self, v: self.__set_var(n, v))(name),
        )
        setattr(cls, name, prop)

    def __set_var(self, name, i):
        if self.deleted:
            raise ObjectIsInvalid()
        self._dirty_fields.add(name)
        setattr(self, "_" + name, i)
