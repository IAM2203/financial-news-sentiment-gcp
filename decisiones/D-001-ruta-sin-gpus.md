## D-001 — Ruta de cómputo sin GPUs en GCP

**Fecha:** 4 de noviembre 2026
**Fase:** 0
**Estado:** Tomada

### Contexto
Cree una cuenta grátis de Google Cloud con $300 USD en créditos para poder explorar las avenidas posibles en cuanto a donde se va a correr el agente, donde se hará el fine-tuning y el resto del proceso de manipulación del modelo open-source. Activando la API de Agent Studio y checando las cuotas disponibles sobre los GPUs de Google encontré que no tengo acceso a estos con este tipo de cuenta. Para este proyecto es importante tener acceso a un GPU porque es el tipo de memoria que usan los LLMs para correr de la forma más eficiente, se puede correr en CPU, pero es sustancialmente más lento. 

### Opciones 
| Opción                              | A favor                                                                                                                         | En contra                                                                                                                                          |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Cuenta de pago y pedir cuota de GPU | Todo vive en GCP, una historia más completa. Entrenamiento y endpoint con servicios administrados. Uso de modelos más grandes.  | Pagar no garantiza cuota de uso de GPU. Errores que pueden salir caros. Hay que esperar aprobaciones sin saber si van a llegar o no.               |
| Prueba gratuita, Colab y Cloud Run  | No hay cobros. No hay que esperar nada. Todavía hay que usar más partes de GCP. Se hace el diseño alrededor de una restricción. | Flujo de entrenamiento fuera de la nube. Modelo más chico. Colab no siempre tiene la GPU disponible. Movimiento manual de pesos de Colab a Cloud.  |

### Decisión *(obligatorio)*
Nuestro camino principal será la opción de prueba gratuita ya que con el nuevo development de que si podemos usar la infraestructura de Saptiva para hacer el entrenamiento podemos usar Cloud Run para correr los modelos, aunque la velocidad sea baja.

### Por qué *(obligatorio)*
Tener acceso a Saptiva que tiene una interfaz muy parecida a la que tiene Google Cloud permite que sea la herramienta perfecta sin necesidad de que tengamos que pagar la cuenta y pedir cuota de GPU. 

### Trade-offs
A pesar de que no es el servicio nativo de Google para hacer el entrenamiento, es muy parecido y servirá para poder aprender algo similar. 

### Evidencia

### ¿Qué me haría cambiar de opinión?

### Lo que aprendí

### Para la entrevista
