from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_session
from app.modules.ventas.schemas import VentaCreate, VentaRead, VentaDetalleRead
from app.modules.ventas.service import crear_venta, obtener_ventas, obtener_venta_por_id

router = APIRouter(prefix="/ventas", tags=["Ventas"])

@router.post("/", response_model=VentaRead, status_code=201)
async def registrar_venta(venta_in: VentaCreate, session: AsyncSession = Depends(get_session)):
    # NOTA PARA TIZIANO: 
    # Acá tenés que inyectar BackgroundTasks en los parámetros de la función
    # y agregar tu aviso en segundo plano justo antes del return.
    
    venta_creada = await crear_venta(session, venta_in)
    return venta_creada

@router.get("/", response_model=List[VentaRead])
async def leer_ventas(
    limit: int = 20, 
    offset: int = 0, 
    session: AsyncSession = Depends(get_session)
):
    return await obtener_ventas(session, limit, offset)

@router.get("/{id}", response_model=VentaDetalleRead)
async def leer_venta_detalle(
    id: int, 
    session: AsyncSession = Depends(get_session)
):
    # Esto devuelve la venta con su cliente y sus renglones resueltos de una vez
    return await obtener_venta_por_id(session, id)