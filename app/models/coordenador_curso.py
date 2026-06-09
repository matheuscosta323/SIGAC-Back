from app.extensions import Base
from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column


class CoordenadorCurso(Base):
    __tablename__ = "coordenador_curso"

    id_coordenador: Mapped[int] = mapped_column(ForeignKey("usuario.id"), nullable=False)
    id_curso: Mapped[int] = mapped_column(ForeignKey("curso.id"), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("id_coordenador", "id_curso"),
    )