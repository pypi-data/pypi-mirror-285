import typing

from pg_table_builder.exceptions import IncompatibleParameters


class CommonTypes:
    def __init__(self,
                 default_expression=None,
                 primary_key=False,
                 unique=False,
                 not_null=False,
                 ) -> None:
        if primary_key and unique:
            raise IncompatibleParameters('PRIMARY KEY and UNIQUE incompatible')
        self.default = (' default {}'.format(default_expression)
                        if default_expression is not None else '')
        self.primary_key = ' PRIMARY KEY' if primary_key else ''
        self.unique = ' UNIQUE' if unique else ''
        self.not_null = ' NOT NULL' if not_null else ''

    def __str__(self) -> str:

        return '{}{}{}{}'.format(self.default, self.primary_key,
                         self.unique, self.not_null)

class Table:
    def __init__(self, name: str, *columns) -> None:
        self.name: str = name
        self.columns = ',\n\t'.join(f"{key}" for key in columns)
    
    def __str__(self) -> str:
        self.query = """CREATE TABLE IF NOT EXISTS {} (\n\t{}\n);""".format(str(self.name),
                                                                            str(self.columns))
        return self.query


class Varchar(CommonTypes):
    def __init__(self,
                 limit_size: int = 15,
                 default_expression=None,
                 primary_key=False,
                 unique=False,
                 not_null=False,) -> None:
        CommonTypes.__init__(self, default_expression,
                             primary_key, unique, not_null)
        self.limit_size = ' ({})'.format(int(limit_size))

    def __str__(self) -> str:
        params = super().__str__()
        str_type = 'VARCHAR{}{}'.format(self.limit_size, params)
        return str_type


class Timestamptz(CommonTypes):
    def __init__(self,
                 default_expression=None,
                 primary_key=False,
                 unique=False,
                 not_null=False) -> None:
        CommonTypes.__init__(self, default_expression,
                             primary_key, unique, not_null)
    
    def __str__(self) -> str:
        params = super().__str__()
        str_type = 'timestamptz{}'.format(params)
        return str_type


class Bool(CommonTypes):
    def __init__(self, default_expression=None,
                 primary_key=False, unique=False,
                 not_null=False) -> None:
        super().__init__(default_expression, primary_key,
                         unique, not_null)

    def __str__(self) -> str:
        return 'bool{}'.format(super().__str__())


class Column:
    def __init__(self, name: str,
                 _type: CommonTypes) -> None:
        self.name = name
        self._type = _type

    def __str__(self) -> str:
        return '{} {}'.format(self.name, self._type)


class Float(CommonTypes):
    def __init__(self, default_expression=None, primary_key=False,
                 unique=False, not_null=False) -> None:
        super().__init__(default_expression, primary_key, unique, not_null)

    def __str__(self) -> str:
        return 'float{}'.format(super().__str__())


class Text(CommonTypes):
    def __init__(self, default_expression=None, primary_key=False,
                 unique=False, not_null=False) -> None:
        super().__init__(default_expression, primary_key, unique, not_null)
    
    def __str__(self) -> str:
        return 'TEXT{}'.format(super().__str__())


class Serial(CommonTypes):
    def __init__(self, primary_key=False,
                 unique=False, not_null=False) -> None:
        super().__init__(None, primary_key, unique, not_null)

    def __str__(self) -> str:
        return 'SERIAL{}'.format(super().__str__())


class ForeignKey:
    def __init__(self, column_name: str,
                 ref: typing.Tuple[str, str]) -> None:
        self.column_name = column_name

        self.ref_table_name, self.ref_column_name = ref
        
    def __str__(self) -> str:
        return 'FOREIGN KEY ({}) REFERENCES {} ({})'.format(self.column_name,
                                                            self.ref_table_name,
                                                            self.ref_column_name)


class DoublePrecision(CommonTypes):
    def __init__(self, default_expression=None, primary_key=False,
                 unique=False, not_null=False) -> None:
        super().__init__(default_expression, primary_key, unique, not_null)
    
    def __str__(self) -> str:
        return 'double precision{}'.format(super().__str__())
