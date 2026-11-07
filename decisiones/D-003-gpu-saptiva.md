## D-003 — Entrenar en la GPU de Saptiva; Colab como respaldo

**Fecha:** 5 de noviembre 2026
**Fase:** 3
**Estado:** Tomada

### Contexto
En la Ibero tengo acceso a una fracción de GPU equivalente a 24 GB de VRAM podría usarse para la fase de entrenamiento del modelo podríamos usar un modelo un poco más grande, como de 4B de parámetros holgado o un poco más grandes, pero cuantizados. 

### Opciones

| Opción                      | A favor                                                                                                                                 | En contra                                       |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| Usar el GPU de Saptiva      | Entrenamiento de modelos más grandes para poder hacer comparaciones. Corre sobre Kubeflow, la misma base que Agent Platform Pipelines (antes Vertex AI Pipelines). | Recurso compartido: la disponibilidad depende de otros usuarios. El entrenamiento queda fuera de GCP. |
| Seguir con el plan de Colab | No hace falta esperar para pedir permiso.                                                                                               | El modelo tendría que ser de 1B, 4B con trabajo |

### Decisión
Usaré la GPU de Saptiva para la fase de entrenamiento (fase 3); Colab queda como respaldo. El permiso para este proyecto ya está dado. El tamaño del modelo se sigue decidiendo en la fase 2.

### Por qué
Tener acceso a modelos más grandes para poder hacer comparaciones en la fase de comparación al igual que tener acceso a una experiencia que es similar a lo que sería usar Agent Studio es demasiado valioso como para que no sea la decisión obvia. 

### Trade-offs
Gano tamaño de modelos y diferentes modelos al igual que velocidad de computo. Pierdo: el entrenamiento sigue fuera de GCP (igual que con Colab) y dependo de un recurso compartido. Además, poder *entrenar* un modelo más grande no significa poder *servirlo*: el despliegue sigue siendo Cloud Run con CPU, donde la latencia y el costo crecen con el tamaño del modelo.

### Evidencia
Los LLMs están pensados para poder correr en GPU con procesamiento paralelo de operaciones. El tamaño del modelo te dice más o menos cuanta memoria necesitas para cada uno, por ejemplo: un modelo Qwen3.5:4B necesita alrededor 4.5 GB de memoria solo para cargar los parámetros, un Qwen3.5:9B cuantizado con nvfp4 necesita alrededor de 7.5GB también de puros parámetros. A estos casos todavía hay que sumarles el contexto que también agrega ocupación de memoria con el KV cache. Para el entrenamiento se tienen que procesar una cantidad de datos bastante grande y esto es más rápido y plausible usando procesamiento en GPU que en CPU. 

### ¿Qué me haría cambiar de opinión?
Esto dejaría de ser viable si en algún momento me dejaran de dar acceso a la cantidad de GPU necesaria para correr los modelos o si por alguna razón pudiera usar los servicios de Agent Studio de GCP. 

### Lo que aprendí
Tener acceso a una GPU te da las mejores herramientas para hacer el entrenamiento necesario para que un modelo tenga fine-tuning. También que Saptiva corre sobre Kubeflow, y Agent Platform Pipelines (antes Vertex AI Pipelines) usa el SDK de Kubeflow Pipelines. Pendiente: confirmar si Saptiva expone Pipelines o solo notebooks (JupyterLab/VSCode).

### Para la entrevista
The free trial gave me zero GPU quota, so instead of waiting on a quota request I moved training to my university's GPU cluster (24 GB of VRAM on a Kubeflow-based platform) and kept Colab as a fallback. That let me fine-tune larger models, with the trade-off that training lives outside GCP and model size is still capped by CPU serving on Cloud Run.