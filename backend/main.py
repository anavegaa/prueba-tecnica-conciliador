from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from services.conciliacion import leer_csv, conciliar_facturas


app = FastAPI(
    title="Conciliador de Facturas y Retenciones",
    description="API para la conciliación de facturas y registros contables.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "mensaje": "API del Conciliador de Facturas funcionando correctamente"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/api/conciliar")
async def conciliar(
    facturas: UploadFile = File(...),
    contabilidad: UploadFile = File(...),
):
    """
    Recibe los archivos facturas.csv y contabilidad.csv
    y ejecuta la conciliación.
    """

    if not facturas.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="El archivo de facturas debe ser un CSV.",
        )

    if not contabilidad.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="El archivo de contabilidad debe ser un CSV.",
        )

    try:
        contenido_facturas = await facturas.read()
        contenido_contabilidad = await contabilidad.read()

        registros_facturas = leer_csv(
            contenido_facturas,
            "facturas",
        )

        registros_contabilidad = leer_csv(
            contenido_contabilidad,
            "contabilidad",
        )

        resultado = conciliar_facturas(
            registros_facturas,
            registros_contabilidad,
        )

        return resultado

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al procesar los archivos: {error}",
        )