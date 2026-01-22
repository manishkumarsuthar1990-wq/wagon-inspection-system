import os
from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

app = FastAPI(title="Wagon Inspection System")

# ------------------ MODELS ------------------

class Wagon(Base):
    __tablename__ = "wagons"
    id = Column(Integer, primary_key=True, index=True)
    wagon_number = Column(String, index=True)
    inspection_date = Column(Date)
    owner = Column(String)
    overall_status = Column(String)


class Checkpoint(Base):
    __tablename__ = "checkpoints"
    id = Column(Integer, primary_key=True)
    section = Column(String)
    serial_no = Column(Integer)
    text = Column(String)
    type = Column(String)
    exclude_from_reports = Column(Integer)


class InspectionResult(Base):
    __tablename__ = "inspection_results"
    id = Column(Integer, primary_key=True)
    wagon_id = Column(Integer, ForeignKey("wagons.id"))
    checkpoint_id = Column(Integer, ForeignKey("checkpoints.id"))
    status = Column(String)
    remarks = Column(String)

# Create tables
Base.metadata.create_all(bind=engine)

# ------------------ API ------------------

@app.get("/")
def root():
    return {"message": "Wagon Inspection API running"}

@app.post("/api/inspection")
def save_inspection(data: dict):
    db = SessionLocal()

    wagon = Wagon(
        wagon_number=data["wagon_number"],
        inspection_date=data["inspection_date"],
        owner=data["owner"],
        overall_status="OK"
    )
    db.add(wagon)
    db.commit()
    db.refresh(wagon)

    overall_status = "OK"

    for item in data["results"]:
        res = InspectionResult(
            wagon_id=wagon.id,
            checkpoint_id=item["checkpoint_id"],
            status=item.get("status"),
            remarks=item.get("remarks", "")
        )
        db.add(res)

        st = item.get("status")
        if st == "NO ACTION TAKEN":
            overall_status = "NO ACTION TAKEN"
        elif st == "NOT OK" and overall_status != "NO ACTION TAKEN":
            overall_status = "NOT OK"
        elif st == "RECTIFIED" and overall_status == "OK":
            overall_status = "RECTIFIED"

    wagon.overall_status = overall_status
    db.commit()
    db.close()

    return {
        "message": "Inspection saved",
        "wagon_id": wagon.id,
        "overall_status": overall_status
    }
