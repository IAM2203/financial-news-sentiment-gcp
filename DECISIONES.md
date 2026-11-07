# Bitácora de decisiones

Registro de cada decisión del proyecto que tuvo alternativas reales: qué opciones había, qué elegí y por qué. Cada decisión vive en su propio archivo dentro de `decisiones/`. Este archivo es solo el índice.

## Cómo usarla

1. **Una decisión, un archivo.** Copia `decisiones/_plantilla.md` y nómbralo `D-XXX-titulo-corto.md` (por ejemplo, `D-004-eleccion-de-dataset.md`).
2. **Solo decisiones con opciones reales.** Instalar una librería no cuenta; elegir entre dos datasets sí.
3. **Escríbela en el momento,** no al final de la fase. En 10 minutos queda.
4. **Lo mínimo indispensable:** Contexto, Opciones, Decisión y Por qué. El resto llénalo cuando aplique.
5. **Agrega la fila al índice** en cuanto crees el archivo.
6. **Si cambias de opinión,** no borres la decisión vieja: márcala como _Reemplazada por D-XXX_ (en su archivo y en el índice) y crea una nueva.

## Índice

| ID | Decisión | Fecha | Fase | Estado |
|---|---|---|---|---|
| [[D-001-ruta-sin-gpus\|D-001]] | Ruta de cómputo sin GPUs en GCP | 2026-11-04 | 0 | Tomada |
| [[D-002-proyecto-sin-organizacion\|D-002]] | Proyecto de GCP sin organización | 2026-11-04 | 0 | Tomada |
| [[D-003-gpu-saptiva\|D-003]] | Entrenar en la GPU de Saptiva; Colab como respaldo | 2026-11-05 | 3 | Tomada |
| [[D-004-eleccion-de-dataset\|D-004]] | Elección del dataset | 2026-11-05 | 1 | Propuesta |

**Estados posibles:** Propuesta · Tomada · Reemplazada por D-XXX