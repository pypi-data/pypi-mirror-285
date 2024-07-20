class BaseDBRequestError(ValueError): pass

class ConfigError(BaseDBRequestError): pass
class InternalError(BaseDBRequestError): pass
class SchemaError(BaseDBRequestError): pass
class TypeConverterError(BaseDBRequestError): pass
class FactoryError(BaseDBRequestError): pass

class SQLArgsError(BaseDBRequestError): pass

