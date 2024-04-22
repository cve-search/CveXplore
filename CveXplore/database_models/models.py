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
    """
    Information about the time the last update was made to a db table.
    """

    __tablename__ = "info"
    id = Column(Integer, primary_key=True, doc="ID of the record")
    db = Column(String(25), doc="Database name")
    lastModified = Column(DateTime, doc="Last modified time")

    def __repr__(self):
        return f"<< Info: {self.db} >>"


class Schema(CveXploreBase):
    """
    Holds information about the current database schema.
    """

    __tablename__ = "schema"
    id = Column(Integer, primary_key=True, doc="ID of the record")
    rebuild_needed = Column(
        Boolean, default=False, doc="Flag to indicate if a rebuild is needed"
    )
    version = Column(Float, doc="Version of the database schema")

    def __repr__(self):
        return f"<< Schema: {self.id} >>"


class Capec(CveXploreBase):
    """
    CAPEC database table.
    """

    __tablename__ = "capec"
    id = Column(
        Integer, primary_key=True, unique=True, index=True, doc="ID of the CAPEC"
    )
    loa = Column(String(25), index=True, doc="Likelihood Of Attack")
    name = Column(String(250), index=True, doc="Name of the CAPEC")
    prerequisites = Column(Text, doc="Prerequisites of the CAPEC")
    solutions = Column(Text, doc="Solutions related to the CAPEC")
    summary = Column(Text, doc="Summary of the CAPEC")
    typical_severity = Column(
        String(25), index=True, doc="Typical severity of the CAPEC"
    )
    execution_flow = Column(JSON, default={}, doc="Execution flow of the CAPEC")
    related_capecs = Column(JSON, default=[], doc="Related CAPECs")
    related_weakness = Column(JSON, default=[], doc="Related weakness of the CAPEC")
    taxonomy = Column(JSON, default=[], doc="Taxonomy of the CAPEC")

    def __repr__(self):
        return f"<< Capec: {self.id} >>"


class Cpe(CveXploreBase):
    """
    CPE database table.
    """

    __tablename__ = "cpe"
    _id = Column(
        BigInteger, primary_key=True, unique=True, index=True, doc="ID of the record"
    )
    id = Column(String(50), unique=True, index=True, doc="ID of the CPE")
    cpeName = Column(String(50), index=True, doc="Name of the CPE")
    cpeNameId = Column(String(50), doc="Unique ID number of the CPE")
    created = Column(DateTime, doc="Creation time of the CPE")
    deprecated = Column(
        Boolean,
        default=False,
        index=True,
        doc="Flag to indicate if a CPE is deprecated",
    )
    deprecatedBy = Column(String(50), doc="Organization that deprecated the CPE")
    lastModified = Column(DateTime, index=True, doc="Last modified time of the CPE")
    padded_version = Column(
        String(50), index=True, doc="Left zero padded version of the CPE"
    )
    product = Column(String(50), index=True, doc="Product of the CPE")
    stem = Column(String(50), index=True, doc="Stem of the CPE")
    title = Column(String(150), index=True, doc="Title of the CPE")
    vendor = Column(String(50), index=True, doc="Vendor of the CPE")
    version = Column(String(50), doc="Version of the CPE")

    def __repr__(self):
        return f"<< Cpe: {self.id} >>"


class Cves(CveXploreBase):
    """
    CVE database table.
    """

    __tablename__ = "cves"
    _id = Column(
        BigInteger, primary_key=True, unique=True, index=True, doc="ID of the record"
    )
    id = Column(String(50), unique=True, index=True, doc="ID of the CVE")
    access = Column(JSON, default={}, doc="Access information of the CVE")
    assigner = Column(
        String(50), index=True, doc="Organization name that assigned the CVE"
    )
    cvss = Column(Float, index=True, doc="CVSS of the CVE")
    cvss3 = Column(Float, index=True, doc="CVSS3 of the CVE")
    cvssSource = Column(String(50), doc="Source of the CVSS of the CVE")
    cvssTime = Column(DateTime, doc="Time of the CVSS of the CVE")
    cvssVector = Column(String(100), doc="Vector of the CVSS of the CVE")
    configurations = Column(JSON, doc="Vulnerable configurations of the CVE")
    cwe = Column(String(50), index=True, doc="Related CWEs to the CVE")
    epss = Column(Float, index=True, doc="Epss of the CVE")
    epssMetric = Column(JSON, doc="Epss metric of the CVE")
    exploitabilityScore = Column(Float, doc="Exploitability Score of the CVE")
    impact = Column(JSON, doc="Impact of the CVE")
    impactScore = Column(Float, doc="Impact score of the CVE")
    lastModified = Column(DateTime, index=True, doc="Last modified time of the CVE")
    modified = Column(DateTime, index=True, doc="Modified time of the CVE")
    products = Column(JSON, default=[], doc="Related products to the CVE")
    published = Column(DateTime, index=True, doc="Published time of the CVE")
    references = Column(JSON, doc="References associated to the CVE")
    status = Column(String(25), index=True, doc="Status of the CVE")
    summary = Column(Text, doc="Summary of the CVE")
    vendors = Column(JSON, default=[], doc="Related vendors of the CVE")
    vulnerable_configuration = Column(
        JSON, default=[], doc="Vulnerable configurations to the CVE"
    )
    vulnerable_configuration_cpe_2_2 = Column(
        JSON, default=[], doc="Vulnerable configurations to the CVE"
    )
    vulnerable_configuration_stems = Column(
        JSON, default=[], doc="Vulnerable configuration stems to the CVE"
    )
    vulnerable_product = Column(JSON, default=[], doc="Vulnerable products to the CVE")
    vulnerable_product_stems = Column(
        JSON, default=[], doc="Vulnerable product stems to the CVE"
    )

    def __repr__(self):
        return f"<< Cves: {self.id} >>"


class Cwe(CveXploreBase):
    """
    CWE database table.
    """

    __tablename__ = "cwe"
    id = Column(
        Integer, primary_key=True, unique=True, index=True, doc="ID of the record"
    )
    description = Column(Text, doc="Description of the CWE")
    name = Column(String(250), index=True, doc="Name of the CWE")
    status = Column(String(25), index=True, doc="Status of the CWE")
    weaknessabs = Column(String(25), doc="Weaknessabs of the CWE")
    related_weaknesses = Column(JSON, default=[], doc="Related weaknesses to the CWE")

    def __repr__(self):
        return f"<< Cwe: {self.id} >>"


class Via4(CveXploreBase):
    """
    VIA4 database table.
    """

    __tablename__ = "via4"
    _id = Column(
        Integer, primary_key=True, unique=True, index=True, doc="ID of the record"
    )
    id = Column(String(50), index=True, doc="ID of the Via4")
    db = Column(String(25), doc="Database name")
    searchables = Column(JSON, default=[], doc="VIA4 searchables")
    sources = Column(JSON, default=[], doc="VIA4 sources")
    msbulletin = Column(JSON, default=[], doc="VIA4 msbulletin")
    redhat = Column(JSON, default={}, doc="VIA4 redhat")
    refmap = Column(JSON, default={}, doc="VIA4 refmap")

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
