import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';

import {
  ResultadoConciliacion,
  RespuestaConciliacion
} from './models/conciliacion.model';

import { ConciliacionService } from './services/conciliacion.service';

@Component({
  selector: 'app-root',
  imports: [FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {

  private readonly conciliacionService = inject(ConciliacionService);
  private readonly changeDetectorRef = inject(ChangeDetectorRef);

  archivoFacturas: File | null = null;
  archivoContabilidad: File | null = null;

  respuesta: RespuestaConciliacion | null = null;

  filtroEstado = 'Todos';

  cargando = false;
  error = '';

  seleccionarFacturas(event: Event): void {
    const input = event.target as HTMLInputElement;

    if (input.files && input.files.length > 0) {
      this.archivoFacturas = input.files[0];
      this.error = '';
    }
  }

  seleccionarContabilidad(event: Event): void {
    const input = event.target as HTMLInputElement;

    if (input.files && input.files.length > 0) {
      this.archivoContabilidad = input.files[0];
      this.error = '';
    }
  }

  conciliar(): void {
    if (!this.archivoFacturas || !this.archivoContabilidad) {
      this.error = 'Debes seleccionar los dos archivos CSV.';
      return;
    }

    this.cargando = true;
    this.error = '';
    this.respuesta = null;

    this.conciliacionService
      .conciliar(this.archivoFacturas, this.archivoContabilidad)
      .subscribe({
        next: (resultado) => {
          this.respuesta = resultado;
          this.cargando = false;

          this.changeDetectorRef.detectChanges();

        },

        error: (error) => {

          if (error.error?.detail) {
            this.error = error.error.detail;
          } else {
            this.error =
              'No fue posible procesar los archivos. Verifica que el backend esté funcionando.';
          }
          this.cargando = false;
          this.changeDetectorRef.detectChanges();
        }
      });
  }

  get resultadosFiltrados(): ResultadoConciliacion[] {
    if (!this.respuesta) {
      return [];
    }

    if (this.filtroEstado === 'Todos') {
      return this.respuesta.resultados;
    }

    return this.respuesta.resultados.filter(
      resultado => resultado.estado === this.filtroEstado
    );
  }

  formatearValor(valor: number | null): string {
    if (valor === null || valor === undefined) {
      return '—';
    }

    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      maximumFractionDigits: 0
    }).format(valor);
  }
}