from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from typing import List
from app.modules.ventas.schemas import VentaCreate, VentaRead, VentaDetalleRead
from app.modules.ventas.service import crear_venta, obtener_ventas, obtener_venta_por_id
from app.modules.ventas.schemas import VentaCreate, VentaRead
from app.modules.ventas.service import crear_venta

router = APIRouter(prefix="/ventas", tags=["Ventas"])

@router.post("/", response_model=VentaRead, status_code=201)
async def registrar_venta(venta_in: VentaCreate, session: AsyncSession = Depends(get_session)):
    # NOTA PARA TIZIANO: 
    # Acá tenés que inyectar BackgroundTasks en los parámetros de la función
    # y agregar tu aviso en segundo plano justo antes del return.
    
    venta_creada = await crear_venta(session, venta_in)
    return venta_creada