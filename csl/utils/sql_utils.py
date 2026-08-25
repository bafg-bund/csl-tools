from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float, create_engine
from sqlalchemy.schema import Table
from sqlalchemy.pool import NullPool


def create_session(path_csl):
    # Create engine using path of CSL and bind it to session
    engine = create_engine(f"sqlite:///{path_csl}", poolclass=NullPool)
    Base.metadata.bind = engine
    db_session = sessionmaker(bind=engine)
    session = db_session()
    return session


def close_session_remove_file(path_csl, session):
    """Safely closes the session and removes the database file."""
    import os
    session.close()
    session.bind.dispose()  # Dispose of the engine (closes the connection to the file)
    os.remove(path_csl)


# Map relationships of the database (Collective Spectral Library [CSL])
# See Jewell et al., 2019 (https://doi.org/10.1002/rcm.8541) for a schematic of the database.
class Base(DeclarativeBase):
    # The Declarative Base refers to a MetaData collection (created automatically) which is then accessible via the
    # DeclarativeBase.metadata class-level attribute. When we create new mapped classes, they each will reference a
    # table within this metaData collection.
    pass


# Define table links with many-to-many relationships
# compound_group <-N-> compound
CompoundGroupMap = Table('compound_group_map', Base.metadata,
                      Column('compound_group_id', Integer, ForeignKey('compound_group.compound_group_id')),
                      Column('compound_id', Integer, ForeignKey('compound.compound_id')), extend_existing=True)


# Map each table and their respective columns and relationships
class Experiment(Base):
    # This is the central table in the database.
    __tablename__ = 'experiment'
    # Primary key: experiment_id
    experiment_id = Column(Integer, primary_key=True)
    # Many-to-one relationship with compound
    compound_id = Column(Integer, ForeignKey('compound.compound_id'), nullable=False)
    compound = relationship("Compound", back_populates='experiments')
    # Many-to-one relationship with parameter
    parameter_id = Column(Integer, ForeignKey('parameter.parameter_id'), nullable=False)
    parameter = relationship("Parameter")
    # One-to-many relationship with fragment (Each experiment has a certain number of fragments)
    fragments = relationship("Fragment", back_populates='experiment', cascade="save-update, merge, delete")
    # Many-to-one relationship with data_source
    data_source_id = Column(Integer, ForeignKey('data_source.data_source_id'), nullable=True)
    data_source = relationship("DataSource", back_populates="experiments")
    # Other columns
    mz = Column(Float, nullable=False)  # m/z (u)
    time_added = Column(DateTime, nullable=True)  # Timestamp when the experiment was added
    adduct = Column(String, nullable=True)  # Adduct notation
    isotope = Column(String, nullable=True)  # Type of molecular mass

    def __repr__(self):  # Define output
        return (f"experiment_id={self.experiment_id}, compound_id={self.compound_id}, compound={self.compound}, "
                f"parameter_id={self.parameter_id}, parameter={self.parameter}, mz={self.mz}, time={self.time_added}, "
                f"adduct={self.adduct}, isotope={self.isotope}, data_source_id={self.data_source_id}")


class Fragment(Base):
    __tablename__ = 'fragment'
    # Primary key: fragment_id
    fragment_id = Column(Integer, primary_key=True)
    # Many-to-one relationship with experiment
    experiment_id = Column(Integer, ForeignKey('experiment.experiment_id'), nullable=True)
    experiment = relationship("Experiment", back_populates='fragments')
    # Other columns
    mz = Column(Float, nullable=False)  # m/z (u)
    int = Column(Float, nullable=False)  # Intensity (-)

    def __repr__(self):
        return (f"fragment_id={self.fragment_id}, experiment_id={self.experiment_id}, experiment={self.experiment}, "
                f"mz={self.mz}, int={self.int}")


class Parameter(Base):
    __tablename__ = 'parameter'
    # Primary key: parameter_id
    parameter_id = Column(Integer, primary_key=True)
    # Other columns
    instrument = Column(String, nullable=False)  # Instrument type and name
    polarity = Column(String, nullable=False)  # Polarity
    ionisation = Column(String, nullable=False)  # Ionization type
    ce = Column(Float, nullable=True)  # Collision energy
    ces = Column(Float, nullable=True)  # Collision energy spread
    ce_unit = Column(String, nullable=True)  # Collision energy units
    collision_type = Column(String, nullable=False)  # Collision type
    electron_energy = Column(Float, nullable=True)  # Electron energy
    electron_energy_unit = Column(String, nullable=True)  # Collision energy units

    def __repr__(self):
        return (f"parameter_id={self.parameter_id}, instrument={self.instrument}, polarity={self.polarity}, "
                f"ionisation={self.ionisation}, ce={self.ce}, ces={self.ces}, ce_unit={self.ce_unit}, "
                f"collision_type={self.collision_type}, ee={self.electron_energy}, ee_unit={self.electron_energy_unit}")


class Compound(Base):
    __tablename__ = 'compound'
    # Primary key: compound_id
    compound_id = Column(Integer, primary_key=True)
    # Many-to-many relationship with compound_group
    compound_groups = relationship("CompoundGroup", secondary=CompoundGroupMap, back_populates='compounds')
    # One-to-many relationship with experiment
    experiments = relationship("Experiment", back_populates='compound', cascade="save-update, merge, delete")
    # One-to-many relationship with retention_time
    retention_times = relationship('RetentionTime', back_populates='compound', cascade="save-update, merge, delete")
    # Other columns
    cas = Column(String, nullable=True)  # CAS (Chemical Abstracts Service) registry number (CAS RN)
    formula = Column(String, nullable=False)  # Chemical formula
    smiles = Column(String, nullable=True)  # SMILES (Simplified Molecular Input Line Entry System)-code
    name = Column(String, nullable=False, unique=True)  # Compound identifier name
    inchi = Column(String, nullable=True)  # InChI
    inchikey = Column(String, nullable=True)  # InChIKey
    pubchem_id = Column(Integer, nullable=True)  # PubChem Identifier

    def __repr__(self):
        return (f"compound_id={self.compound_id}, name={self.name}, cas={self.cas}, inchikey={self.inchikey}, "
                f"formula={self.formula}, smiles={self.smiles}, inchi={self.inchi}, pubchem_id={self.pubchem_id}")


class RetentionTime(Base):
    __tablename__ = 'retention_time'
    # Primary key: retention_time_id
    retention_time_id = Column(Integer, primary_key=True)
    # Many-to-one relationship with compound
    compound_id = Column(Integer, ForeignKey('compound.compound_id'), nullable=True)
    compound = relationship('Compound', back_populates='retention_times')
    # Other columns
    rt = Column(Float, nullable=True)  # Retention time (min)
    chrom_method = Column(String, nullable=True)  # Chromatographic method identifier name
    predicted = Column(String, nullable=True)  # FALSE: experimental value; TRUE: modeled value

    def __repr__(self):
        return (f"retention_time_id={self.retention_time_id}, compound_id={self.compound_id}, compound={self.compound}, rt={self.rt},"
                f"chrom_method={self.chrom_method}, predicted={self.predicted}")


class CompoundGroup(Base):
    # This table is for compound groups, e.g., Pesticide, Pharmaceutical, etc ...
    __tablename__ = 'compound_group'
    # Primary key: compound_group_id
    compound_group_id = Column(Integer, primary_key=True)
    # Many-to-many relationship with compound
    compounds = relationship("Compound", secondary=CompoundGroupMap, back_populates='compound_groups')
    # Other columns
    name = Column(String, nullable=False)  # Compound group identifier name

    def __repr__(self):
        return f"compound_group_id={self.compound_group_id}, name={self.name}, no. of compounds={len(self.compounds)}"


class DataSource(Base):
    # This table is for data sources, e.g., bfg, uba, lfuby, lanuk, lubw, etc ...
    __tablename__ = 'data_source'
    # Primary key: data_source_id
    data_source_id = Column(Integer, primary_key=True)
    # One-to-many relationship with experiment
    experiments = relationship("Experiment", back_populates='data_source')
    # Other columns
    name = Column(String, nullable=False)  # Data source identifier name
    long_name = Column(String, nullable=True)  # Author affiliation
    authors = Column(String, nullable=True)  # Author name(s)

    def __repr__(self):
        return (f"data_source_id={self.data_source_id}, name={self.name}, long_name={self.long_name}, "
                f"authors={self.authors}, no. of experiments={len(self.experiments)}")
