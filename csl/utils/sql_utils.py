from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.schema import Table


def inst_code_csl_mapping():
    """
    Provides mapping of institution code to institution notation as they appear in the CSL.
    Needs to be updates when new institution notations are added, or when existing ones are updated.

    Returns:
        dict: Dictionary mapping institution codes to CSL institution notation.
    """
    # Todo: LUBW not in CSL yet
    return {'bfg': 'BfG', 'uba': 'UBA', 'lfuby': 'LfU', 'lanuv': 'LANUV', 'lubw': 'LUBW'}


def create_session(path_csl):
    # Create engine using path of CSL and bind it to session
    engine = create_engine(f"sqlite:///{path_csl}")
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
# compoundGroup <-N-> compound
compGroupComp = Table('compGroupComp', Base.metadata,
                      Column('compoundGroup_id', Integer, ForeignKey('compoundGroup.compoundGroup_id')),
                      Column('compound_id', Integer, ForeignKey('compound.compound_id')), extend_existing=True)

# experimentGroup <-N-> experiment
expGroupExp = Table('expGroupExp', Base.metadata,
                    Column('experimentGroup_id', Integer, ForeignKey('experimentGroup.experimentGroup_id')),
                    Column('experiment_id', Integer, ForeignKey('experiment.experiment_id')), extend_existing=True)


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
    # Many-to-many relationship with experimentGroup
    groups = relationship("ExperimentGroup", secondary=expGroupExp, back_populates='experiments')
    # One-to-many relationship with fragment (Each experiment has a certain number of fragments)
    fragments = relationship("Fragment", back_populates='experiment', cascade="save-update, merge, delete")
    # Other columns
    mz = Column(Float, nullable=False)  # m/z (u)
    time_added = Column(DateTime)
    adduct = Column(String)
    isotope = Column(String)

    def __repr__(self):  # Define output
        return "\nid={}, mz={}, para={}, comp={}, adduct={}, time={}".format(self.experiment_id, self.mz,
                                                                             self.parameter_id, self.compound_id,
                                                                             self.adduct, self.time_added)


class Fragment(Base):
    __tablename__ = 'fragment'
    # Primary key: fragment_id
    fragment_id = Column(Integer, primary_key=True)
    # Many-to-one relationship with experiment
    experiment_id = Column(Integer, ForeignKey('experiment.experiment_id'))
    experiment = relationship("Experiment", back_populates='fragments')
    # Other columns
    mz = Column(Float, nullable=False)  # m/z (u)
    int = Column(Float, nullable=False)

    def __repr__(self):
        return "\nmz={}, int={}, exp_id={}".format(self.mz, self.int, self.experiment_id)


class Parameter(Base):
    __tablename__ = 'parameter'
    # Primary key: parameter_id
    parameter_id = Column(Integer, primary_key=True)
    # Todo: One-to-many relationship with Experiment missing?
    # Other columns
    instrument = Column(String, nullable=False)
    polarity = Column(String, nullable=False)
    ionisation = Column(String, nullable=False)
    CE = Column(Float, nullable=False)  # Collision energy
    CES = Column(Float)  # Collision energy spread
    ce_unit = Column(String, nullable=False)  # Collision energy units
    col_type = Column(String, nullable=False)  # Collision type

    def __repr__(self):
        return '\ninstrument={}, pol={}, CE={}, CES={}, ce_unit={}, col_type={}'.format(self.instrument,
                                                                                        self.polarity,
                                                                                        self.CE, self.CES,
                                                                                        self.ce_unit, self.col_type)


class Compound(Base):
    __tablename__ = 'compound'
    # Primary key: compound_id
    compound_id = Column(Integer, primary_key=True)
    # Many-to-many relationship with compoundGroup
    groups = relationship("CompoundGroup", secondary=compGroupComp, back_populates='compounds')
    # One-to-many relationship with experiment
    experiments = relationship("Experiment", back_populates='compound', cascade="save-update, merge, delete")
    # One-to-many relationship with retention_time
    retention_times = relationship('RetentionTime', back_populates='compound', cascade="save-update, merge, delete")
    # Other columns
    CAS = Column(String)  # CAS (Chemical Abstracts Service) registry number (CAS RN)
    formula = Column(String, nullable=False)
    SMILES = Column(String)  # SMILES (Simplified Molecular Input Line Entry System) -code
    name = Column(String, nullable=False, unique=True)
    chem_list_id = Column(Integer)
    inchi = Column(String)
    inchikey = Column(String)

    def __repr__(self):
        return "\nname={}, CAS={}, id={}, smiles={}".format(self.name, self.CAS, self.compound_id, self.SMILES)


class RetentionTime(Base):
    __tablename__ = 'retention_time'
    # Primary key: ret_time_id
    ret_time_id = Column(Integer, primary_key=True)
    # Many-to-one relationship with compound
    compound_id = Column(Integer, ForeignKey('compound.compound_id'))
    compound = relationship('Compound', back_populates='retention_times')
    # Other columns
    rt = Column(Float)  # retention time (min)
    chrom_method = Column(String)  # name of method, refer to documentation for details
    predicted = Column(String)

    def __repr__(self):
        return '\nrt={}, chromatographic method={}'.format(self.rt, self.chrom_method)


class CompoundGroup(Base):
    # This table is for compound groups, e.g. FRAME list, Rhein-Non-target
    __tablename__ = 'compoundGroup'
    # Primary key: compoundGroup_id
    compoundGroup_id = Column(Integer, primary_key=True)
    # Many-to-many relationship with compound
    compounds = relationship("Compound", secondary=compGroupComp, back_populates='groups')
    # Other columns
    name = Column(String, nullable=False)

    def __repr__(self):
        return '\nname={}'.format(self.name)


class ExperimentGroup(Base):
    # This table is for experiment groups, e.g. BfG, MassBank, Stoff-Ident
    __tablename__ = 'experimentGroup'
    # Primary key: experimentGroup_id
    experimentGroup_id = Column(Integer, primary_key=True)
    # Many-to-many relationship with experiment
    experiments = relationship("Experiment", secondary=expGroupExp, back_populates='groups')
    # Other columns
    name = Column(String, nullable=False)

    def __repr__(self):
        return '\nname={}'.format(self.name)
