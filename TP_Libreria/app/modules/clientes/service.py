from app.modules.ventas.models import Venta, RenglonVenta
from app.modules.ventas.schemas import VentaCreate
from sqlalchemy.orm import selectinload, joinedload
from typing import List

from app.modules.libros.models import Libro 

async def crear_venta(session: AsyncSession, venta_in: VentaCreate) -> Venta:
    # 1. Extraer los IDs de los libros que el cliente quiere comprar
    libros_ids = [r.libro_id for r in venta_in.renglones]
    
    # 2. Ir a buscar esos libros a la base de datos (ignoramos cualquier precio del cliente)
    stmt = select(Libro).where(Libro.id.in_(libros_ids))
    resultado = await session.execute(stmt)
    libros_db = {libro.id: libro for libro in resultado.scalars().all()}
    
    # 3. Validar que no nos estén mandando un libro fantasma
    if len(libros_db) != len(libros_ids):
        raise HTTPException(
            status_code=409, 
            detail="Error: Uno o más libros solicitados no existen en el catálogo."
        )
        
    # 4. Procesar renglones y calcular la matemática exacta
    renglones_nuevos = []
    total_venta = 0
    
    for renglon_in in venta_in.renglones:
        libro_real = libros_db[renglon_in.libro_id]
        precio_real = libro_real.precio
        
        # Armamos el renglón copiando el precio oficial de la base de datos
        nuevo_renglon = RenglonVenta(
            libro_id=renglon_in.libro_id,
            cantidad=renglon_in.cantidad,
            precio_unitario=precio_real
        )
        renglones_nuevos.append(nuevo_renglon)
        
        # Sumamos al total matemático
        total_venta += (precio_real * renglon_in.cantidad)
        
    # 5. Instanciar la venta final
    nueva_venta = Venta(
        cliente_id=venta_in.cliente_id,
        fecha=datetime.now(timezone.utc),
        total=total_venta,
        renglones=renglones_nuevos
    )
    
    # 6. Guardar todo como una única transacción
    session.add(nueva_venta)
    try:
        await session.commit()
        await session.refresh(nueva_venta)
        return nueva_venta
    except IntegrityError:
        await session.rollback()
        # Si falla por un cliente_id que no existe, devolvemos 409 según la consigna C-05
        raise HTTPException(
            status_code=409, 
            detail="Error de integridad: el cliente no existe."
        )

async def obtener_ventas(session: AsyncSession, limit: int = 20, offset: int = 0) -> List[Venta]:
    # RN-10: Listado paginado
    stmt = select(Venta).offset(offset).limit(limit)
    resultado = await session.execute(stmt)
    return resultado.scalars().all()

async def obtener_venta_por_id(session: AsyncSession, venta_id: int) -> Venta:
    # Ejercicio 6: Carga anticipada sin N+1
    stmt = (
        select(Venta)
        .where(Venta.id == venta_id)
        .options(
            joinedload(Venta.cliente),
            selectinload(Venta.renglones)
        )
    )
    resultado = await session.execute(stmt)
    venta = resultado.scalars().first()
    
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta
