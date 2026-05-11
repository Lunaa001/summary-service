"""Summary model for storing generated summaries"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from datetime import datetime
from .base import Base


class Summary(Base):
    """Summary model for storing document summaries"""
    __tablename__ = "resumenes"
    
    id = Column(Integer, primary_key=True, index=True)
    documento_id = Column(Integer, nullable=False, index=True)
    texto_original = Column(Text, nullable=False)
    resumen = Column(Text, nullable=False)
    longitud_resumen = Column(Integer, nullable=False)
    tokens_utilizados = Column(Integer, nullable=True)
    modelo = Column(String(100), nullable=True, default="gemma4-26b-16g")
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Summary(id={self.id}, documento_id={self.documento_id}, longitud={self.longitud_resumen})>"
