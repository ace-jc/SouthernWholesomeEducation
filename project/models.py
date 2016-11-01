# pylint: disable=E1101, R0913, R0903
"""Implements the models that will be used in database"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

APP = Flask(__name__)
APP.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ec2-user:ec2-user@localhost/swe'

DB = SQLAlchemy(APP)

MAJORTOCITY = DB.Table('MAJORTOCITY',
                       DB.Column('city_id', DB.Integer,
                                 DB.ForeignKey('CITY.id_num')),
                       DB.Column('major_id', DB.Integer,
                                 DB.ForeignKey('MAJOR.id_num')))

ETHNICITYTOCITY = DB.Table('ETHNICITYTOCITY',
                           DB.Column('city_id', DB.Integer,
                                     DB.ForeignKey('CITY.id_num')),
                           DB.Column('ethnicity_id', DB.Integer,
                                     DB.ForeignKey('ETHNICITY.id_num')))

# ETHNICITYTOUNIVERSITY = DB.Table('ETHNICITYTOUNIVERSITY',
#                                  DB.Column('university_id', DB.Integer,
#                                            DB.ForeignKey('UNIVERSITY.id_num')),
#                                  DB.Column('ethnicity_id', DB.Integer,
#                                            DB.ForeignKey('ETHNICITY.id_num')))

# MAJORTOUNIVERSITY = DB.Table('MAJORTOUNIVERSITY',
#                              DB.Column('university_id', DB.Integer,
#                                        DB.ForeignKey('UNIVERSITY.id_num')),
#                              DB.Column('major_id', DB.Integer,
#                                        DB.ForeignKey('MAJOR.id_num')))

def create_unique(model, **args):
    is_exist = model.query.filter_by(**args).first()
    if not is_exist:
        is_exist = model(**args)
        DB.session.add(is_exist)
        DB.session.commit()
    return is_exist

def add_unique(obj):
    is_exist = obj.__class__.query.filter_by(**obj.attributes()).first()
    if not is_exist:
        DB.session.add(obj)
        DB.session.commit()

class AssociationMajor(DB.Model):
    __tablename__ = 'associationmajor'
    university_id = DB.Column(DB.Integer, DB.ForeignKey('UNIVERSITY.id_num'), primary_key=True)
    major_id = DB.Column(DB.Integer, DB.ForeignKey('MAJOR.id_num'), primary_key=True)
    num_students = DB.Column(DB.Integer)
    major = DB.relationship('Major', backref=DB.backref('university_associations', lazy='dynamic'))
    university = DB.relationship('University', backref=DB.backref('major_associations', lazy='dynamic'))
    def __init__(self, university, major, num_students):
        self.university = university
        self.major = major
        self.num_students = num_students

class AssociationEthnicity(DB.Model):
    __tablename__ = 'associationethnicity'
    university_id = DB.Column(DB.Integer, DB.ForeignKey('UNIVERSITY.id_num'), primary_key=True)
    ethnicity_id = DB.Column(DB.Integer, DB.ForeignKey('ETHNICITY.id_num'), primary_key=True)
    num_students = DB.Column(DB.Integer)
    ethnicity = DB.relationship('Ethnicity', backref=DB.backref('university_associations', lazy='dynamic'))
    university = DB.relationship('University', backref=DB.backref('ethnicity_associations', lazy='dynamic'))
    def __init__(self, university, ethnicity, num_students):
        self.university = university
        self.ethnicity = ethnicity
        self.num_students = num_students

class University(DB.Model):
    '''
    Class for University pillar. The name, numUndergrads, costToAttend, gradRate
    , and publicOrPrivate variables will be set from API data and the
    ethnicityList and major_list will be created from relationships. A city
    variable will also be included from a backref with the City class.
    '''
    __tablename__ = 'UNIVERSITY'
    id_num = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(80))
    num_undergrads = DB.Column(DB.Integer)
    cost_to_attend = DB.Column(DB.Integer)
    grad_rate = DB.Column(DB.Float)
    public_or_private = DB.Column(DB.String(80))
    ethnicity_list = DB.relationship('Ethnicity', secondary='associationethnicity')
    major_list = DB.relationship('Major', secondary='associationmajor')
    
    city_id = DB.Column(DB.Integer, DB.ForeignKey('CITY.id_num'))

    def __init__(self, name, numundergrads, costtoattend, gradrate, publicorprivate):
        self.name = name
        self.num_undergrads = numundergrads
        self.cost_to_attend = costtoattend
        self.grad_rate = gradrate
        self.public_or_private = publicorprivate

    def __repr__(self):
        return '<University ' + self.name + '>'

    def attributes(self):
        return {'name': self.name, 'num_undergrads': self.num_undergrads, 'cost_to_attend': self.cost_to_attend,
            'grad_rate': self.grad_rate, 'public_or_private': self.public_or_private}

    # These functions create relationships between Universities and Majors and
    # Ethnicities.
    def add_major(self, maj, num):
        """Appends new major to major_list"""
        maj = create_unique(Major, name=maj)
        AssociationMajor(self, maj, num)

    def add_ethnicity(self, eth, num):
        """Appends new ethnicity to ethnicityList"""
        eth = create_unique(Ethnicity, name=eth)
        AssociationEthnicity(self, eth, num)


class City(DB.Model):
    '''
    Class for City pillar. The name and urbanOrRural variables will be set from API data and the
    universityList, major_list, and ethnicityList will be created from relationships. The population
    and avgTuition variables will be aggregated from university data in universityList.
    '''
    __tablename__ = 'CITY'
    id_num = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(80))
    population = DB.Column(DB.Integer)
    major_list = DB.relationship('Major', secondary=MAJORTOCITY,
                                 backref=DB.backref('city', lazy='dynamic'))
    ethnicity_list = DB.relationship('Ethnicity', secondary=ETHNICITYTOCITY,
                                     backref=DB.backref('city', lazy='dynamic'))
    university_list = DB.relationship(
        'University', backref='city', lazy='dynamic')
    avg_tuition = DB.Column(DB.Integer)
    urban_or_rural = DB.Column(DB.String(80))

    def __init__(self, name):
        self.name = name
        self.population = 0
        self.avg_tuition = 0

    def __repr__(self):
        return '<City ' + self.name + '>'

    def attributes(self):
        return {'name': self.name}

    # These functions create relationships between Cities and Majors,
    # Ethnicities, and Universities.
    def add_university(self, uni):
        """Appends university to universityList"""
        self.university_list.append(uni)

    def add_major(self, maj):
        """Appends major to major_list"""
        self.major_list.append(Major(maj))

    def add_ethnicity(self, eth):
        """Adds new ethnicity to ethnicity_list"""
        self.ethnicity_list.append(Ethnicity(eth))


class Major(DB.Model):
    '''
    Class for Major pillar. The name variable is passed in initially and
    the numUndergrads, gradRate, and avgPercentage are calculated based
    on relationships. This class will include a backref table
    from University (university) and City (city).
    '''
    __tablename__ = 'MAJOR'
    id_num = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(80))
    num_undergrads = DB.Column(DB.Integer)
    top_city = DB.Column(DB.String(80))
    avg_percentage = DB.Column(DB.Float)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Major ' + self.name + '>'

    def attributes(self):
        return {'name': self.name}


class Ethnicity(DB.Model):
    '''
    Class for Ethnicity pillar. The name variable is passed in initially and the totalCount variable
    is calculated based on the University relationship. This class will include a backref table
    from University (university) and City (city).
    '''
    __tablename__ = 'ETHNICITY'
    id_num = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(80))
    total_count = DB.Column(DB.Integer)

    def __init__(self, name):
        self.name = name
        self.total_count = 0

    def __repr__(self):
        return '<Ethnicity ' + self.name + '>'

    def attributes(self):
        return {'name': self.name}
