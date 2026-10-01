from decimal import Decimal


def calcular_iva(base_gravable, tarifa_iva):
    """
    Calcula el IVA esperado de una factura.

    La tarifa_iva se recibe como decimal:
    0.19 = 19%
    0.05 = 5%
    """
    base = Decimal(str(base_gravable))
    tarifa = Decimal(str(tarifa_iva))

    return base * tarifa


def validar_iva(base_gravable, tarifa_iva, valor_iva):
    """
    Compara el IVA registrado en la factura
    contra el IVA esperado según la base y la tarifa.
    """
    iva_esperado = calcular_iva(base_gravable, tarifa_iva)
    iva_registrado = Decimal(str(valor_iva))

    diferencia = iva_registrado - iva_esperado

    return {
        "iva_esperado": iva_esperado,
        "iva_registrado": iva_registrado,
        "diferencia": diferencia,
        "es_correcto": abs(diferencia) <= Decimal("0.01")
    }

def calcular_total(base_gravable, tarifa_iva, valor_retencion):
    """
    Calcula el total esperado de la factura.

    Fórmula:
    base gravable + IVA esperado - retención
    """
    base = Decimal(str(base_gravable))
    retencion = Decimal(str(valor_retencion))
    iva = calcular_iva(base_gravable, tarifa_iva)

    return base + iva - retencion


def validar_total(base_gravable, tarifa_iva, valor_retencion, total_factura):
    """
    Compara el total registrado en la factura
    contra el total esperado.
    """
    total_esperado = calcular_total(
        base_gravable,
        tarifa_iva,
        valor_retencion
    )

    total_registrado = Decimal(str(total_factura))
    diferencia = total_registrado - total_esperado

    return {
        "total_esperado": total_esperado,
        "total_registrado": total_registrado,
        "diferencia": diferencia,
        "es_correcto": abs(diferencia) <= Decimal("0.01")
    }


import csv
import io


COLUMNAS_FACTURAS = {
    "id_factura",
    "nit_proveedor",
    "fecha_factura",
    "concepto",
    "base_gravable",
    "tarifa_iva",
    "valor_iva",
    "tarifa_retencion",
    "valor_retencion",
    "total_factura",
}

COLUMNAS_CONTABILIDAD = {
    "id_factura",
    "fecha_contabilizacion",
    "cuenta_contable",
    "centro_costo",
    "valor_debito",
    "valor_credito",
    "estado",
}


def leer_csv(contenido, tipo_archivo):
    """
    Lee el contenido de un archivo CSV y valida sus columnas.
    """

    try:
        texto = contenido.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError(
            f"El archivo de {tipo_archivo} debe estar codificado en UTF-8."
        )

    lector = csv.DictReader(io.StringIO(texto))

    if lector.fieldnames is None:
        raise ValueError(
            f"El archivo de {tipo_archivo} está vacío o no tiene encabezados."
        )

    columnas_actuales = set(lector.fieldnames)

    if tipo_archivo == "facturas":
        columnas_requeridas = COLUMNAS_FACTURAS
    else:
        columnas_requeridas = COLUMNAS_CONTABILIDAD

    columnas_faltantes = columnas_requeridas - columnas_actuales

    if columnas_faltantes:
        faltantes = ", ".join(sorted(columnas_faltantes))
        raise ValueError(
            f"El archivo de {tipo_archivo} no contiene las columnas requeridas: "
            f"{faltantes}"
        )

    filas = list(lector)

    if not filas:
        raise ValueError(
            f"El archivo de {tipo_archivo} no contiene registros."
        )

    return filas

def convertir_decimal(valor, campo):
    """
    Convierte un valor del CSV a Decimal.
    Genera un error claro si el valor no es numérico.
    """
    try:
        return Decimal(str(valor).strip())
    except (ValueError, TypeError, ArithmeticError):
        raise ValueError(
            f"El campo '{campo}' contiene un valor numérico inválido: '{valor}'."
        )

from collections import Counter


def detectar_duplicados(registros):
    """
    Identifica IDs de factura que aparecen más de una vez.
    """
    ids = [registro["id_factura"].strip() for registro in registros]

    conteo = Counter(ids)

    return {
        id_factura
        for id_factura, cantidad in conteo.items()
        if id_factura and cantidad > 1
    }

def agrupar_contabilidad(registros_contabilidad):
    """
    Agrupa los registros contables por ID de factura.

    Un mismo ID puede tener:
    - ningún registro
    - un registro
    - varios registros
    """
    agrupados = {}

    for registro in registros_contabilidad:
        id_factura = registro["id_factura"].strip()

        if not id_factura:
            continue

        if id_factura not in agrupados:
            agrupados[id_factura] = []

        agrupados[id_factura].append(registro)

    return agrupados

def conciliar_factura(factura, registros_contables, factura_duplicada=False):
    """
    Analiza una factura individual y determina si presenta inconsistencias.
    """

    causas = []

    id_factura = factura["id_factura"].strip()

    # ---------------------------------------------------------
    # 1. Validación de campos obligatorios
    # ---------------------------------------------------------

    campos_obligatorios = [
        "id_factura",
        "nit_proveedor",
        "fecha_factura",
        "concepto",
        "base_gravable",
        "tarifa_iva",
        "valor_iva",
        "tarifa_retencion",
        "valor_retencion",
        "total_factura",
    ]

    for campo in campos_obligatorios:
        if not factura.get(campo, "").strip():
            causas.append(f"Campo obligatorio vacío: {campo}")

    # ---------------------------------------------------------
    # 2. Factura duplicada
    # ---------------------------------------------------------

    if factura_duplicada:
        causas.append("Factura duplicada en el archivo de facturas")

    # ---------------------------------------------------------
    # 3. Validación de IVA y total
    # ---------------------------------------------------------

    iva_esperado = None
    iva_registrado = None
    diferencia_iva = None

    total_esperado = None
    total_registrado = None
    diferencia_total = None

    try:
        base_gravable = convertir_decimal(
            factura["base_gravable"],
            "base_gravable"
        )

        tarifa_iva = convertir_decimal(
            factura["tarifa_iva"],
            "tarifa_iva"
        )

        valor_iva = convertir_decimal(
            factura["valor_iva"],
            "valor_iva"
        )

        valor_retencion = convertir_decimal(
            factura["valor_retencion"],
            "valor_retencion"
        )

        total_factura = convertir_decimal(
            factura["total_factura"],
            "total_factura"
        )

        resultado_iva = validar_iva(
            base_gravable,
            tarifa_iva,
            valor_iva
        )

        iva_esperado = resultado_iva["iva_esperado"]
        iva_registrado = resultado_iva["iva_registrado"]
        diferencia_iva = resultado_iva["diferencia"]

        if not resultado_iva["es_correcto"]:
            causas.append(
                "El IVA registrado no coincide con el IVA esperado"
            )

        resultado_total = validar_total(
            base_gravable,
            tarifa_iva,
            valor_retencion,
            total_factura
        )

        total_esperado = resultado_total["total_esperado"]
        total_registrado = resultado_total["total_registrado"]
        diferencia_total = resultado_total["diferencia"]

        if not resultado_total["es_correcto"]:
            causas.append(
                "El total de la factura no coincide con el total esperado"
            )

    except ValueError as error:
        causas.append(str(error))

    # ---------------------------------------------------------
    # 4. Validación del registro contable
    # ---------------------------------------------------------

    if not registros_contables:
        causas.append("Factura sin registro contable")

        estado_contabilidad = "Sin registro"

    else:
        estados = [
            registro.get("estado", "").strip()
            for registro in registros_contables
        ]

        estado_contabilidad = ", ".join(estados)

        if len(registros_contables) > 1:
            causas.append("Registros contables duplicados")

        if any(estado == "Pendiente" for estado in estados):
            causas.append("Registro contable en estado Pendiente")

    # ---------------------------------------------------------
    # 5. Resultado final
    # ---------------------------------------------------------

    estado = (
        "Correcta"
        if not causas
        else "Con inconsistencia"
    )

    return {
        "id_factura": id_factura,
        "estado": estado,
        "causas": causas,
        "iva_esperado": iva_esperado,
        "iva_registrado": iva_registrado,
        "diferencia_iva": diferencia_iva,
        "total_esperado": total_esperado,
        "total_registrado": total_registrado,
        "diferencia_total": diferencia_total,
        "estado_contabilidad": estado_contabilidad,
    }

def conciliar_facturas(facturas, registros_contables):
    """
    Ejecuta la conciliación completa de todas las facturas.
    """

    duplicadas_facturas = detectar_duplicados(facturas)
    contabilidad_agrupada = agrupar_contabilidad(registros_contables)

    resultados = []

    for factura in facturas:
        id_factura = factura["id_factura"].strip()

        resultado = conciliar_factura(
            factura=factura,
            registros_contables=contabilidad_agrupada.get(
                id_factura,
                []
            ),
            factura_duplicada=id_factura in duplicadas_facturas,
        )

        resultados.append(resultado)

    total_facturas = len(resultados)

    inconsistencias = sum(
        1
        for resultado in resultados
        if resultado["estado"] == "Con inconsistencia"
    )

    correctas = total_facturas - inconsistencias

    return {
        "resumen": {
            "total_facturas": total_facturas,
            "correctas": correctas,
            "inconsistencias": inconsistencias,
        },
        "resultados": resultados,
    }