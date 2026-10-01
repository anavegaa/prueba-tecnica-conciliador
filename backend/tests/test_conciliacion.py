from services.conciliacion import (
    calcular_iva,
    validar_iva,
    validar_total,
    detectar_duplicados,
    leer_csv,
    conciliar_facturas,
)


def test_calcular_iva():
    resultado = calcular_iva(3_800_000, 0.05)

    assert resultado == 190_000


def test_validar_iva_correcto():
    resultado = validar_iva(3_800_000, 0.05, 190_000)

    assert resultado["es_correcto"] is True
    assert resultado["diferencia"] == 0


def test_validar_iva_incorrecto():
    resultado = validar_iva(3_800_000, 0.05, 215_000)

    assert resultado["es_correcto"] is False
    assert resultado["iva_esperado"] == 190_000
    assert resultado["diferencia"] == 25_000


def test_validar_total_incorrecto():
    resultado = validar_total(
        1_760_000,
        0,
        70_400,
        1_691_100,
    )

    assert resultado["es_correcto"] is False
    assert resultado["total_esperado"] == 1_689_600
    assert resultado["diferencia"] == 1_500


def test_detectar_duplicados():
    registros = [
        {"id_factura": "FAC-0001"},
        {"id_factura": "FAC-0002"},
        {"id_factura": "FAC-0001"},
        {"id_factura": "FAC-0003"},
        {"id_factura": "FAC-0002"},
    ]

    duplicados = detectar_duplicados(registros)

    assert duplicados == {"FAC-0001", "FAC-0002"}


def test_leer_csv_detecta_columnas_faltantes():
    contenido = (
        "id_factura,nit_proveedor,fecha_factura\n"
        "FAC-0001,900123456,2026-01-01\n"
    ).encode("utf-8")

    try:
        leer_csv(contenido, "facturas")
        assert False, "Debía generar un error por columnas faltantes"
    except ValueError as error:
        assert "columnas requeridas" in str(error)
        assert "base_gravable" in str(error)


def test_conciliacion_completa():
    facturas = [
        {
            "id_factura": "FAC-0001",
            "nit_proveedor": "900123456",
            "fecha_factura": "2026-01-01",
            "concepto": "Servicio",
            "base_gravable": "1000000",
            "tarifa_iva": "0.19",
            "valor_iva": "190000",
            "tarifa_retencion": "0.04",
            "valor_retencion": "40000",
            "total_factura": "1150000",
        },
        {
            "id_factura": "FAC-0002",
            "nit_proveedor": "900654321",
            "fecha_factura": "2026-01-02",
            "concepto": "Servicio",
            "base_gravable": "1000000",
            "tarifa_iva": "0.19",
            "valor_iva": "200000",
            "tarifa_retencion": "0.04",
            "valor_retencion": "40000",
            "total_factura": "1160000",
        },
    ]

    contabilidad = [
        {
            "id_factura": "FAC-0001",
            "fecha_contabilizacion": "2026-01-02",
            "cuenta_contable": "510505",
            "centro_costo": "CC01",
            "valor_debito": "1150000",
            "valor_credito": "0",
            "estado": "Contabilizado",
        }
    ]

    resultado = conciliar_facturas(facturas, contabilidad)

    assert resultado["resumen"]["total_facturas"] == 2
    assert resultado["resumen"]["correctas"] == 1
    assert resultado["resumen"]["inconsistencias"] == 1

    assert resultado["resultados"][0]["estado"] == "Correcta"
    assert resultado["resultados"][1]["estado"] == "Con inconsistencia"