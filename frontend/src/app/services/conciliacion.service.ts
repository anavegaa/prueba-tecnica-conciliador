import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { RespuestaConciliacion } from '../models/conciliacion.model';

@Injectable({
  providedIn: 'root'
})
export class ConciliacionService {

  private readonly http = inject(HttpClient);

  private readonly apiUrl = 'http://127.0.0.1:8000/api/conciliar';

  conciliar(
    facturas: File,
    contabilidad: File
  ): Observable<RespuestaConciliacion> {

    const formData = new FormData();

    formData.append('facturas', facturas);
    formData.append('contabilidad', contabilidad);

    return this.http.post<RespuestaConciliacion>(
      this.apiUrl,
      formData
    );
  }
}