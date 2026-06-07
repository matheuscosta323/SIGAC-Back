from app.extensions import Base
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


class CoordenadorCurso(Base):
    __tablename__ = "coordenador_curso"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_coordenador: Mapped[int] = mapped_column(ForeignKey("usuario.id"), nullable=False)
    id_curso: Mapped[int] = mapped_column(ForeignKey("curso.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("id_coordenador", "id_curso", name="uq_coordenador_curso"),
    )
