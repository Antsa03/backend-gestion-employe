from sqlalchemy import Column, Integer, String, Float
from database import Base


class Employe(Base):
    __tablename__ = "employe"

    num_emp = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    nbr_jours = Column(Integer, index=True)
    taux_journalier = Column(Float, index=True)
