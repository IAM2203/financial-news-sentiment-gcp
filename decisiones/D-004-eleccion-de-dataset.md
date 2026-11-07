## D-004 — Elección del dataset

**Fecha:** 5 de noviembre 2026
**Fase:** 1
**Estado:** Propuesta

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
 * Voy a rehacer la partición de datos de Twitter por falta de documentación de partición, no trae test propio e implica que los dos datasets llevan el mismo procedimiento y son comparables. 

### Por qué 
El razonamiento: qué pesó más y por qué.

### Trade-offs
Qué gano, qué pierdo y qué se vuelve más difícil después.

### Evidencia
Datos, métricas, capturas o documentación que lo respaldan.

### ¿Qué me haría cambiar de opinión?
La condición concreta bajo la cual revisaría esta decisión.

### Lo que aprendí

### Para la entrevista
Cómo lo contaría en una o dos frases, en inglés.