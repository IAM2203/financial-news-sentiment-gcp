## D-004 — Elección del dataset

**Fecha:** 5 de noviembre 2026 (tomada el 7 de noviembre 2026)
**Fase:** 1
**Estado:** Tomada

### Contexto
Necesitamos elegir el dataset que vamos a usar para hacer el fine-tuning del modelo con "notas" financieras y se respectiva etiqueta de sentimiento. Hay dos opciones de datasets a usar: Financial Phrase Bank y Twitter Financial News Sentiment. Y un candidato sorpresa, Alpaca, que solo viene con la pura noticia. 

### Opciones 

| Opción     | A favor                                                                                             | En contra                                                                                                                               |
| ---------- | --------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| PhraseBank | La licencia permite la distribución siempre y cuando no sea de uso comercial.                       |                                                                                                                                         |
| Twitter    | La licencia es de MIT, una de las más permisivas.                                                   |                                                                                                                                         |
| Alpaca     | Profundidad de hasta +10 años. Alrededor de 130 noticias por día. Puede haber fuente de la noticia. | No tiene un valor de sentimiento para hacer el entrenamiento supervisado. La licencia de los datos no permite la distribución de estos. |

### Criterios (fijados el 7 nov 2026, antes de medir)

**Eliminatorios** (se aplican a cada dataset por separado)

* **Tamaño.** El test necesita al menos ~700 textos únicos para medir F1 con una precisión de ±3 puntos (2·√(p(1−p)/n) ≤ 0.03 con p ≈ 0.8). Con un test del 15%, el dataset limpio necesita ~4,700 textos. Si no llega, queda eliminado.
* **Licencia.** Si los pesos entrenados con PhraseBank no se pueden publicar en el portafolio (pendiente: opinión de mi papá), PhraseBank queda eliminado.

**Limpieza de duplicados (M2)**, con la llave normalizada; en PhraseBank, dentro de un solo nivel

* Si un texto se repite con la misma etiqueta, se queda una sola copia.
* Si se repite con etiquetas distintas, se quitan todas sus copias.
* La limpieza se hace sobre todo el dataset, antes de partir. No se conserva la partición del autor de Twitter: la partición es propia (paso 5).
* Si más del 10% de los textos repetidos tienen etiquetas en conflicto, se leen 20 para distinguir errores de anotación de textos ambiguos. Esto no elimina el dataset; entra en el desempate.
* Se reporta qué porcentaje de `valid` ya está en `train`. Si pasa del 5%, el README advierte que los resultados publicados sobre esa partición pueden estar inflados.

**Anidamiento de PhraseBank (M5)**

* Si está anidado (sin oraciones faltantes ni cambios de etiqueta), se usa solo 50Agree, con una columna `max_agreement` que guarda el nivel más alto en el que aparece cada oración.
* Si hay oraciones que cambian de etiqueta entre niveles y son ≤ 1% del nivel, se quitan y se documenta. Si son más, se usa un solo nivel sin `max_agreement` y PhraseBank pierde en limpieza.
* Si faltan oraciones de un nivel estricto en el más laxo, primero se compara con la llave normalizada. Si siguen faltando ≤ 1%, se aceptan como pérdida y se documenta; si son más, se aplica lo mismo que en el punto anterior.
* Nunca se apilan niveles, para que la misma oración no termine en train y en test.

**Decisión entre datasets**

* Si solo uno pasa los eliminatorios, ese es el elegido.
* Si pasan los dos, gana el que tenga menor porcentaje de textos repetidos con etiquetas en conflicto, siempre que la diferencia sea de al menos 5 puntos porcentuales. Si quedan más cerca, gana el que tenga la mediana de palabras (M4) más cercana a la de un titular de referencia: **[PENDIENTE: fijar este número antes de correr M4]**.
* Si ninguno pasa, se relaja el test al 20% (mínimo ~3,600 textos limpios) y se documenta como limitación. Si aun así ninguno pasa, se reabre D-004.

### Decisión

Uso **Twitter Financial News Sentiment**, limpiado con la política M2-1 sobre el dataset completo (11,776 textos) y con una partición propia en el paso 5. No conservo la partición del autor: no está documentada, no trae test, y así los dos datasets siguen el mismo procedimiento. PhraseBank queda como trabajo futuro, por ejemplo como prueba de generalización a otro tipo de texto.

### Por qué

- **Tamaño (eliminatorio).** Twitter tiene 11,776 textos limpios y PhraseBank 50Agree tiene 4,836. Los dos pasan; PhraseBank, con solo 136 de margen.
- **Licencia de PhraseBank (eliminatorio, pendiente).** Es CC BY-NC-SA; falta confirmar si el uso en el portafolio y la publicación de los pesos LoRA son compatibles. No bloquea la decisión: si PhraseBank queda eliminado, gana Twitter por ser el único que pasa, y si pasa, Twitter gana el desempate.
- **Desempate.** Porcentaje de textos repetidos con etiquetas en conflicto: Twitter 3.1% (3 de 98) y PhraseBank 25% (2 de 8). La diferencia es de 22 puntos, por encima del umbral de 5, así que gana Twitter.
- **Sensibilidad.** El 25% de PhraseBank sale de solo 2 de 8 llaves (±15 puntos de error estándar). Medidos sobre todos los textos únicos, los dos conflictos son despreciables (0.03% y 0.04%), y con ese criterio el desempate habría pasado a M4, que no se midió. Decido con el criterio tal como se fijó antes de medir y dejo documentada esta fragilidad.

### Trade-offs

**Qué gano**

- Más del doble de datos limpios (11,776 contra 4,836). Con un test del 15% quedan ~1,770 textos, así que el intervalo del F1 es más estrecho que con el mínimo de ~700.
- Una licencia (MIT) sin la restricción no comercial ni el *share-alike* de PhraseBank.

**Qué pierdo**

- Los niveles de acuerdo de PhraseBank, que habrían permitido medir el F1 por dificultad (`max_agreement`).
- Etiquetas hechas por anotadores con conocimiento financiero; en Twitter el proceso de etiquetado no está documentado.

**Qué se vuelve más difícil**

- **Autoría del texto.** No está claro de quién es el texto de los tweets. No subo el texto crudo al repo; se descarga con el script y el commit fijado.
- **Cambio de distribución.** Los textos son de finales de 2019 a principios de 2020 y el endpoint va a recibir noticias actuales, así que el F1 en test probablemente sobreestima el desempeño real. Una prueba de drift con titulares de Alpaca queda como trabajo futuro.
- **Etiquetas ambiguas y texto sucio:** casos como "$hdge shorts getting killed" etiquetado como bullish, URLs `t.co` y saltos de línea.
- **Casi duplicados sin medir (M3).** La limpieza exacta no los detecta; pueden dejar fuga en la partición propia. Se revisan en el paso 5 con `quality.nearest_neighbors`.
- **Partición temporal sin revisar (M6).** Por ahora la partición será aleatoria estratificada.
- **Desempate frágil.** El 25% de PhraseBank sale de 2 de 8 llaves (ver Por qué).

### Evidencia

- **Criterios fijados antes de medir:** commit `eca8351`.
- **Código:** `src/quality.py` (`normalize_text`, `exact_duplicates`, `cross_overlap`, `check_nesting`) y `notebooks/02_d004_measurements.ipynb`.
- **Duplicados exactos (M2)**, con la llave normalizada (minúsculas, sin URLs, espacios colapsados):

| Dataset | Filas | Llaves únicas | Llaves repetidas | Filas en repetidos | Conflictos | % conflicto | Limpio |
|---|---|---|---|---|---|---|---|
| Twitter | 11,931 | 11,779 | 98 | 250 | 3 | 3.1% | 11,776 |
| PhraseBank 50Agree | 4,846 | 4,838 | 8 | 16 | 2 | 25.0% | 4,836 |
| PhraseBank 66Agree | 4,217 | 4,211 | 6 | 12 | 0 | 0% | 4,211 |
| PhraseBank 75Agree | 3,453 | 3,448 | 5 | 10 | 0 | 0% | 3,448 |
| PhraseBank AllAgree | 2,264 | 2,259 | 5 | 10 | 0 | 0% | 2,259 |

- **Fuga en la partición del autor de Twitter:** 39 de 2,388 filas de `valid` (1.6%) ya están en `train`. Está por debajo del umbral del 5%, así que no va advertencia en el README. Desaparece con la limpieza antes de partir.
- **Conflictos de PhraseBank 50Agree (leídos los 2):** "TELECOMWORLDWIRE-7 April 2006-TJ Group Plc sells stake in Morning Digital Design Oy…" (neutral / positive) y "The Group 's business is balanced by its broad portfolio of sports…" (positive / neutral). Los dos están en la frontera neutral–positivo: son textos ambiguos, no errores. Se quitan con M2-1.
- **Conflictos de Twitter:** 3.1%, debajo del 10%, así que no se leyeron (criterio M2-2).
- **Sensibilidad:** conflictos sobre todos los textos únicos: Twitter 3 / 11,779 ≈ 0.03%, PhraseBank 2 / 4,838 ≈ 0.04%.
- **No medido:** M5 (anidamiento; ya no decide), M1, M3, M4 y M6.

### ¿Qué me haría cambiar de opinión?

- Si encuentro un dataset etiquetado más grande que Twitter y, al compararlo con una muestra de titulares de Alpaca (lo que va a recibir el endpoint), sus textos se parecen más a ellos, usaría ese dataset en lugar de Twitter.
- Si M3 muestra tantos casi duplicados que, al quitarlos, Twitter queda debajo del mínimo de ~4,700 textos limpios.

### Lo que aprendí
Un criterio expresado en porcentaje necesita un tamaño mínimo de muestra, si no, decide el ruido.

### Para la entrevista
Choosing between two datasets taught me that an unbiased decision needs acceptance criteria fixed before running any measurement.