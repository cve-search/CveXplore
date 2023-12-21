from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Float,
    JSON,
    Text,
    BigInteger,
)

from sqlalchemy.orm import declarative_base

CveXploreBase = declarative_base()


class Info(CveXploreBase):
    __tablename__ = "info"
    id = Column(Integer, primary_key=True)
    db = Column(String(25))
    lastModified = Column(DateTime)

    def __repr__(self):
        return f"<< Info: {self.db} >>"


class Schema(CveXploreBase):
    __tablename__ = "schema"
    id = Column(Integer, primary_key=True)
    rebuild_needed = Column(Boolean, default=False)
    version = Column(Float)

    def __repr__(self):
        return f"<< Schema: {self.id} >>"


class Capec(CveXploreBase):
    __tablename__ = "capec"
    id = Column(Integer, primary_key=True, unique=True, index=True)
    loa = Column(String(25), index=True)
    name = Column(String(250), index=True)
    prerequisites = Column(Text)
    solutions = Column(Text)
    summary = Column(Text)
    typical_severity = Column(String(25), index=True)
    execution_flow = Column(JSON, default={})
    related_capecs = Column(JSON, default=[])
    related_weakness = Column(JSON, default=[])
    taxonomy = Column(JSON, default=[])

    def __repr__(self):
        return f"<< Capec: {self.id} >>"


class Cpe(CveXploreBase):
    __tablename__ = "cpe"
    _id = Column(BigInteger, primary_key=True, unique=True, index=True)
    id = Column(String(50), unique=True, index=True)
    cpeName = Column(String(50), index=True)
    cpeNameId = Column(String(50))
    created = Column(DateTime)
    deprecated = Column(Boolean, default=False, index=True)
    deprecatedBy = Column(String(50))
    lastModified = Column(DateTime, index=True)
    padded_version = Column(String(50), index=True)
    product = Column(String(50), index=True)
    stem = Column(String(50), index=True)
    title = Column(String(150), index=True)
    vendor = Column(String(50), index=True)
    version = Column(String(50))

    def __repr__(self):
        return f"<< Cpe: {self.id} >>"


class Cves(CveXploreBase):
    __tablename__ = "cves"
    _id = Column(BigInteger, primary_key=True, unique=True, index=True)
    id = Column(String(50), unique=True, index=True)
    access = Column(JSON, default={})
    assigner = Column(String(50), index=True)
    cvss = Column(Float, index=True)
    cvss3 = Column(Float, index=True)
    cvssSource = Column(String(50))
    cvssTime = Column(DateTime)
    cvssVector = Column(String(100))
    cwe = Column(String(50), index=True)
    epss = Column(Float, index=True)
    epssMetric = Column(JSON)
    exploitabilityScore = Column(Float)
    impact = Column(JSON)
    impactScore = Column(Float)
    lastModified = Column(DateTime, index=True)
    modified = Column(DateTime, index=True)
    products = Column(JSON, default=[])
    published = Column(DateTime, index=True)
    references = Column(JSON)
    status = Column(String(25), index=True)
    summary = Column(Text)
    vendors = Column(JSON, default=[])
    vulnerable_configuration = Column(JSON, default=[])
    vulnerable_configuration_cpe_2_2 = Column(JSON, default=[])
    vulnerable_configuration_stems = Column(JSON, default=[])
    vulnerable_product = Column(JSON, default=[])
    vulnerable_product_stems = Column(JSON, default=[])

    def __repr__(self):
        return f"<< Cves: {self.id} >>"


class Cwe(CveXploreBase):
    __tablename__ = "cwe"
    id = Column(Integer, primary_key=True, unique=True, index=True)
    description = Column(Text)
    name = Column(String(250), index=True)
    status = Column(String(25), index=True)
    weaknessabs = Column(String(25))
    related_weaknesses = Column(JSON, default=[])

    def __repr__(self):
        return f"<< Cwe: {self.id} >>"


class Via4(CveXploreBase):
    __tablename__ = "via4"
    _id = Column(Integer, primary_key=True, unique=True, index=True)
    id = Column(String(50), index=True)
    db = Column(String(25))
    searchables = Column(JSON, default=[])
    sources = Column(JSON, default=[])
    msbulletin = Column(JSON, default=[])
    redhat = Column(JSON, default={})
    refmap = Column(JSON, default={})

    def __repr__(self):
        return f"<< Via4: {self.db} >>"


class Cpeother(CveXploreBase):
    __tablename__ = "cpeother"
    id = Column(Integer, primary_key=True, unique=True, index=True)

    def __repr__(self):
        return f"<< Cpeother: {self.id} >>"


class MgmtBlacklist(CveXploreBase):
    __tablename__ = "mgmt_blacklist"
    id = Column(Integer, primary_key=True, unique=True, index=True)

    def __repr__(self):
        return f"<< MgmtBlacklist: {self.id} >>"


class MgmtWhitelist(CveXploreBase):
    __tablename__ = "mgmt_whitelist"
    id = Column(Integer, primary_key=True, unique=True, index=True)

    def __repr__(self):
        return f"<< MgmtWhitelist: {self.id} >>"
