from app.extensions import Base
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class DashboardAluno(Base):
    __tablename__ = "dashboard_aluno"

    id_aluno: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_curso: Mapped[int] = mapped_column(Integer, primary_key=True)
    area: Mapped[str] = mapped_column(String(100), primary_key=True)
    limite_horas: Mapped[int] = mapped_column(Integer)
    horas_aprovadas: Mapped[int] = mapped_column(Integer)