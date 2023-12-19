from CveXplore.database.helpers.generic_db import GenericDatabaseFieldsFunctions

class CvesDatabaseFunctions:
    id: GenericDatabaseFieldsFunctions
    cvss: GenericDatabaseFieldsFunctions
    cvss3: GenericDatabaseFieldsFunctions
    summary: GenericDatabaseFieldsFunctions
    vendors: GenericDatabaseFieldsFunctions
    products: GenericDatabaseFieldsFunctions
    lastModified: GenericDatabaseFieldsFunctions
    modified: GenericDatabaseFieldsFunctions
    published: GenericDatabaseFieldsFunctions
    status: GenericDatabaseFieldsFunctions
    assigner: GenericDatabaseFieldsFunctions
    cwe: GenericDatabaseFieldsFunctions
    epss: GenericDatabaseFieldsFunctions

    def __init__(self, collection: str): ...

class CpeDatabaseFunctions:
    id: GenericDatabaseFieldsFunctions
    title: GenericDatabaseFieldsFunctions
    cpeName: GenericDatabaseFieldsFunctions
    vendor: GenericDatabaseFieldsFunctions
    product: GenericDatabaseFieldsFunctions
    stem: GenericDatabaseFieldsFunctions

    def __init__(self, collection: str): ...

class CapecDatabaseFunctions:
    id: GenericDatabaseFieldsFunctions
    name: GenericDatabaseFieldsFunctions
    summary: GenericDatabaseFieldsFunctions
    prerequisites: GenericDatabaseFieldsFunctions
    solutions: GenericDatabaseFieldsFunctions
    loa: GenericDatabaseFieldsFunctions
    typical_severity: GenericDatabaseFieldsFunctions

    def __init__(self, collection: str): ...

class CWEDatabaseFunctions:
    id: GenericDatabaseFieldsFunctions
    name: GenericDatabaseFieldsFunctions
    status: GenericDatabaseFieldsFunctions
    description: GenericDatabaseFieldsFunctions

    def __init__(self, collection: str): ...
