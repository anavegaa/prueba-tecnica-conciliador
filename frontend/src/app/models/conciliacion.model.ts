export interface ResultadoConciliacion {
  id_factura: string;
  estado: string;
  causas: string[];
  iva_esperado: number | null;
  iva_registrado: number | null;
  diferencia_iva: number | null;
  total_esperado: number | null;
  total_registrado: number | null;
  diferencia_total: number | null;
  estado_contabilidad: string;
}

export interface ResumenConciliacion {
  total_facturas: number;
  correctas: number;
  inconsistencias: number;
}

export interface RespuestaConciliacion {
  resumen: ResumenConciliacion;
  resultados: ResultadoConciliacion[];
}