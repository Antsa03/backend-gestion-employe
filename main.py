from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


class EmployeBase(BaseModel):
    nom: str
    nbr_jours: int
    taux_journalier: float


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.post("/employes/")
async def create_employe(employe: EmployeBase, db: db_dependency):
    db_employe = models.Employe(
        nom=employe.nom,
        nbr_jours=employe.nbr_jours,
        taux_journalier=employe.taux_journalier,
    )
    db.add(db_employe)
    db.commit()
    db.refresh(db_employe)
    return {
        "num_emp": db_employe.num_emp,
        "nom": db_employe.nom,
        "nbr_jours": db_employe.nbr_jours,
        "taux_journalier": db_employe.taux_journalier,
    }


@app.get("/employes/statistiques")
async def get_statistiques(db: db_dependency):
    employes = db.query(models.Employe).all()

    if not employes:
        return {
            "total_salaire": 0,
            "salaire_min": 0,
            "salaire_max": 0,
        }

    salaires = [emp.nbr_jours * emp.taux_journalier for emp in employes]
    return {
        "total_salaire": sum(salaires),
        "salaire_min": min(salaires),
        "salaire_max": max(salaires),
    }


@app.get("/employes/{num_emp}")
async def read_employe(num_emp: int, db: db_dependency):
    result = db.query(models.Employe).filter(models.Employe.num_emp == num_emp).first()
    if not result:
        raise HTTPException(status_code=404, detail="Question not found")
    return result


@app.get("/employes/")
async def read_employes(db: db_dependency):
    employes = db.query(models.Employe).all()
    return employes


@app.put("/employes/{num_emp}")
async def update_employe(num_emp: int, employe: EmployeBase, db: db_dependency):
    db_employe = (
        db.query(models.Employe).filter(models.Employe.num_emp == num_emp).first()
    )
    if not db_employe:
        raise HTTPException(status_code=404, detail="Employe not found")
    db_employe.nom = employe.nom
    db_employe.nbr_jours = employe.nbr_jours
    db_employe.taux_journalier = employe.taux_journalier
    db.commit()
    return {
        "num_emp": db_employe.num_emp,
        "nom": db_employe.nom,
        "nbr_jours": db_employe.nbr_jours,
        "taux_journalier": db_employe.taux_journalier,
    }


@app.delete("/employes/{num_emp}")
async def delete_employe(num_emp: int, db: db_dependency):
    db_employe = (
        db.query(models.Employe).filter(models.Employe.num_emp == num_emp).first()
    )
    if not db_employe:
        raise HTTPException(status_code=404, detail="Employe not found")
    db.delete(db_employe)
    db.commit()
    return {"message": "L'employé a été supprimé avec succès"}
