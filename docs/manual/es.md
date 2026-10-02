# Manual de Codex Model Gate

Codex Model Gate organiza las tareas ejecutadas por Codex CLI. Le ayuda a preparar la solicitud, revisar el modelo y las skills recomendadas, autorizar la ejecución y encontrar los resultados posteriormente.

## Comience aquí

1. En la pestaña **Tarea**, elija dónde se guardarán los proyectos.
2. Escriba lo que desea hacer y, si es necesario, use **Adjuntar archivos...**.
3. Seleccione **Analizar tarea**. El Gate recomienda un modelo, nivel de razonamiento y skills.
4. Revise la decisión. Puede ajustar la selección de skills antes de continuar.
5. Seleccione **Confirmar y ejecutar**. Los archivos se guardan en la carpeta exclusiva de la tarea.
6. Al terminar, revise el resultado, abra los archivos creados y registre su calidad.

### Modo simple y plantillas de tareas

El programa se abre en **modo simple**, con los controles esenciales para preparar, analizar y ejecutar una tarea. Justo debajo de la descripción, la búsqueda web y los adjuntos aparecen **1. Analizar tarea** y **2. Confirmar y ejecutar**, seguidos del resumen del modelo, nivel, riesgo y skills. La biblioteca detallada y el seguimiento aparecen más abajo. Use `Ctrl+Enter` para analizar y `Ctrl+Shift+Enter` para ejecutar. Active **Mostrar opciones avanzadas** cuando quiera elegir la política, el modelo, el nivel, la biblioteca de skills o consultar los detalles técnicos de la ejecución.

Los botones usan los colores existentes de la interfaz para mostrar el progreso: **Analizar tarea** se vuelve azul cuando hay una descripción preparada. Tras el análisis se vuelve verde con una marca de confirmación y **Confirmar y ejecutar** se vuelve azul. Al iniciar la ejecución, el segundo botón también se vuelve verde. Si cambia la descripción o los archivos adjuntos, los controles vuelven al estado de preparación; analice de nuevo antes de ejecutar.

Al seleccionar **Confirmar y ejecutar**, el cuadro de autorización se abre sobre la ventana principal. La consulta de versión de Codex CLI se realiza en segundo plano, sin abrir otra ventana.

En **Comenzar con una plantilla**, elija un punto de partida para crear un documento, analizar un archivo, generar una imagen, buscar referencias u organizar datos. Sustituya los campos entre corchetes por su contexto antes de analizar.

## Modelo y nivel de razonamiento

El Gate recomienda los modelos principales de la familia GPT-6 según la **complejidad del resultado solicitado**, no por la cantidad de palabras. **Luna — Bajo** atiende consultas y transformaciones delimitadas, como una fecha pública o un tipo de cambio actual, con una fuente adecuada cuando sea necesario. **Sol — Bajo** atiende verificaciones explícitas de hechos; **Sol — Medio/Alto** atiende investigación, síntesis, creación, criterio especializado y trabajos de impacto relevante. **Astra — Medio/Alto** atiende entregas amplias con etapas y decisiones interdependientes, con mayor revisión si el impacto es alto. La evaluación también muestra riesgo, herramientas, especialización, verificabilidad y ambigüedad. La elección final del modelo y nivel sigue en manos del usuario en las opciones avanzadas. Los modelos heredados aparecen en un selector separado **Modelo heredado** para uso manual; los registros antiguos de Terra siguen disponibles.

Bajo, Medio, Alto, Extra alto y Máximo dependen del modelo. Ultra requiere declaración explícita en el catálogo público local de la misma versión del CLI y no se recomienda automáticamente.

### Agilidad de la interfaz

Al concluir una tarea, el Gate abre la respuesta antes de actualizar los archivos y el historial. El panel de consumo reutiliza los registros ya cargados, y la estimación de duración usa los mismos datos. La versión del Codex CLI comprobada en la sesión se reutiliza al autorizar, y los mensajes de progreso se agrupan para mantener la ventana ágil. Estas mejoras reducen las esperas de la interfaz; el tiempo de generación del modelo depende de la tarea, el nivel elegido y Codex CLI.

### Consumo y costo estimado

En conversaciones con varias respuestas, el registro muestra el tiempo y los tokens de cada ejecución por separado. La pestaña **Consumo** suma los tokens informados por esas ejecuciones. Los registros antiguos sin este desglose conservan el total disponible.

Después de la ejecución, el Gate muestra los tokens de entrada, entrada en caché, salida y razonamiento informados por Codex CLI, además del costo estimado para el modelo seleccionado. El importe se presenta con dos decimales y en la moneda asociada al idioma de la interfaz. Si el CLI no informa el uso, la estimación no está disponible. Es una estimación, no un cargo: no incluye tarifas de herramientas, modalidades especiales, contexto largo, procesamiento prioritario ni cambios de divisa más allá de la tasa de referencia del Gate.

Precios de referencia estándar para tokens de texto en USD por millón, para solicitudes de hasta 272 mil tokens de entrada: GPT-6 Luna, entrada US$ 0,10, caché US$ 0,01 y salida US$ 0,50; GPT-6 Sol, US$ 2, US$ 0,20 y US$ 10; GPT-6 Astra, US$ 10, US$ 1 y US$ 50. El modelo heredado GPT-5.6 Terra sigue disponible para selección manual y conserva las tarifas configuradas en el Gate: entrada US$ 2, caché US$ 0,20 y salida US$ 12. Los precios pueden cambiar; consulte la [tabla oficial de precios de OpenAI](https://developers.openai.com/api/docs/pricing).

## Skills

Mantenga activada la selección automática para que el Gate elija las skills relacionadas con la tarea. Para elegirlas usted mismo, active **Usar selección manual** y busque por una parte del nombre; no es necesario escribirlo completo. Las skills mostradas en **Skills recomendadas para esta tarea** son las que se usarán en esa tarea. Quitar una de la tarea no la elimina de la biblioteca.

La selección automática utiliza Codex CLI con Sol 6.1 — Medio para analizar la solicitud, el contenido de los adjuntos y el catálogo completo de competencias. La memoria incremental guarda descripciones completas, títulos y fragmentos de alcance, actualizados cuando cambian los archivos. La IA compara capacidades, elige skills complementarias en orden de uso y justifica cada contribución. Las nuevas skills participan por su alcance sin registrar rutas fijas. La cantidad depende de la biblioteca; nombres duplicados usan la versión instalada más recientemente.

El análisis es una llamada al modelo y consume tokens. Los perfiles y el contenido relevante de los adjuntos se envían mediante el CLI autenticado. Se ejecuta en segundo plano, en sandbox de solo lectura, antes de autorizar la ejecución. Texto, DOCX, PDF con texto y XLSX tienen vistas previas locales limitadas; PNG, JPEG y WebP se envían como imágenes. La IA puede leer los originales indicados cuando sea necesario. Los PDF escaneados y formatos sin lector pueden requerir OCR u otras herramientas; sus limitaciones deben aparecer en la recomendación.

Revise las skills, justificaciones y limitaciones antes de confirmar. Puede cancelar el análisis o ajustar la selección manualmente. Un fallo del CLI no cuenta como análisis completo ni provoca una sustitución silenciosa por reglas locales. Si cambia un adjunto, analícelo de nuevo. El registro guarda la decisión y los tokens del análisis por separado de los turnos de la tarea. El campo opcional antiguo `gate_outcomes` sigue siendo legible, pero no se exige para la selección inteligente.

Al usar **Programar tarea...**, introduzca la fecha y hora local en formato `DD/MM/AAAA HH:MM`. El Gate solicita su confirmación a la hora prevista.

## Tareas anteriores y archivos

En **Tareas anteriores**, use **Buscar tarea** para localizar una ejecución por solicitud, tema, respuesta o nombre de archivo. La búsqueda se actualiza mientras escribe, ignora diferencias de mayúsculas y acentos y también está disponible con `Ctrl+F`. Use los filtros adicionales para restringir por fecha, modelo, estado o skill. Seleccione una tarea y abra **Archivos** para ver únicamente sus archivos. Las fechas visibles y el filtro de fecha usan `DD/MM/AAAA` y la hora local; el archivo del registro conserva las fechas originales para auditoría.

A la derecha de la búsqueda aparece únicamente la cantidad de registros mostrados. Consulte los totales de tokens y costos en **Consumo**.

Las tareas ejecutadas por esta versión conservan la sesión de Codex. Seleccione una y use **Continuar conversación** para solicitar ajustes, revisar la entrega o continuar el análisis en la misma sesión y carpeta. En **Tareas anteriores**, los cuatro filtros están en una fila. La barra muestra **Actualizar registros**, **Continuar conversación** y **Evaluar registro**. **Lista** agrupa los registros sin evaluar y el informe; **Abrir / exportar** agrupa la lectura, la exportación TXT/PDF y la carpeta; **Paquetes .gate** agrupa exportación e importación de tareas. Todas las funciones siguen disponibles. La barra permanece en una fila y se desplaza horizontalmente cuando es necesario. La lista de tareas y **Detalles del registro seleccionado** dividen por igual la altura disponible. Cada mensaje nuevo se incorpora al registro. Los registros antiguos sin identificador de sesión siguen disponibles para lectura, pero no pueden recuperar de forma retroactiva un contexto que no se guardó.

## Consumo

Abra la pestaña **Consumo** para consultar costos estimados y tokens agregados de hoy, los últimos siete días, este mes, este año o todo el período. Seleccione **Personalizado** para indicar las fechas inicial y final en formato `DD/MM/AAAA`. Filtre por todos los modelos o por Luna, Terra, Sol y Astra. La tabla identifica el modelo y muestra tareas, entrada, caché, salida, razonamiento y costo por hora, día o mes según el período. En español, las fechas usan día/mes/año, los meses se muestran como `MM/AAAA`, los millares llevan punto y los importes usan coma decimal y dos cifras. Elija la moneda automática del idioma de la interfaz o USD, BRL y EUR. Use **Exportar CSV...** para guardar las filas visibles y abrirlas en una hoja de cálculo.

En la tabla **Desglose**, los encabezados y valores están centrados en cada columna, incluidos modelo, tokens y costo estimado.

El aviso junto al resumen indica que el total es una estimación, no un cargo de la cuenta. El panel agrega registros locales con tokens y un modelo identificable; muestra cuántos registros hay en el período, cuántos se incluyen y cuántos se excluyen por falta de datos. Los costos usan los precios y el tipo de cambio de referencia configurados en el Gate, se muestran con dos decimales y pueden recalcularse con las tarifas actuales: los registros guardan modelo y tokens, no una factura ni el precio vigente en la fecha de ejecución.

## Enlaces en las respuestas

Las direcciones de páginas mostradas en una respuesta aparecen como hipervínculos azules y subrayados. Seleccione uno para abrirlo en el navegador predeterminado de Windows. El Gate reconoce URLs escritas directamente y enlaces con título en Markdown, y solo abre direcciones `http` o `https` válidas.

## Búsqueda web controlada

Para fechas públicas, encuestas electorales o tareas que usan la skill de fuentes fiables, el Gate habilita la búsqueda web en directo de Codex. La tarea comienza directamente en Codex, que puede consultar fuentes actuales y citar sus enlaces. Compruebe fechas y cifras en la fuente original antes de utilizarlas.

Las explicaciones de mecanismos técnicos también habilitan la búsqueda web en directo y reciben al menos **Sol — Medio**, incluso con preguntas cortas en portugués, inglés o español. En todas las tareas, el Gate indica a Codex que abra cada página citada, compruebe que respalda directamente la afirmación y utilice una sección específica si es posible. Esta regla se aplica automáticamente. Si no puede acceder a la página, debe indicarlo en vez de inventar la referencia.

Marque **Permitir navegador visual del Gate (Edge)** para poner a disposición de Codex un navegador visible y aislado. Marcar la casilla no inicia una búsqueda: la tarea comienza en Codex y Edge se abre solo si este decide usar la herramienta. La sesión no reutiliza automáticamente sus accesos ni su historial personal. Sin la casilla marcada, **Términos para buscar en Edge (opcional)** queda desactivado y no afecta la tarea.

Este campo acepta **palabras de búsqueda**, por ejemplo `calendario elecciones México 2027`. Son una sugerencia, no una orden: Codex puede usar otros términos o no usar Edge. Si se deja vacío, la descripción de la tarea se envía como consulta sugerida. Cuando se usa, el navegador visual busca en Google y Bing y solo puede abrir páginas que aparezcan entre los resultados. Pegar `https://ejemplo.com/articulo` en este campo busca esa URL como texto; **no abre la página directamente**. Para solicitar el análisis de un enlace específico, inclúyalo en la descripción principal de la tarea, por ejemplo `Lea y resuma https://ejemplo.com/articulo`. Codex puede intentar acceder a la página con las herramientas disponibles y debe avisar si no lo logra. Las consultas delimitadas sobre fechas de elecciones o competiciones deportivas reciben Luna — Bajo y búsqueda web en vivo; las solicitudes de comparación o análisis se califican por la complejidad del resultado.

Cuando está habilitado, el Gate ofrece su navegador visual a Codex mediante herramientas MCP locales. La búsqueda web en vivo de Codex funciona independientemente de esta opción.

## Pantalla de respuesta

Al finalizar una tarea, el Gate abre automáticamente **Respuesta**, incluso en modo simple. El panel técnico continúa limitado a las opciones avanzadas, pero nunca es necesario activarlo solo para leer la respuesta final.

## Copia de seguridad y datos

Use **Crear copia...** en la pestaña Tarea para guardar proyectos, skills, registros y configuración en un archivo ZIP. Las nuevas copias usan una estructura interna compacta para evitar el error de rutas largas de Windows. El archivo `backup-manifest.json` dentro del ZIP relaciona cada elemento con su ruta original.

### Copia completa ZIP y paquete de tarea `.gate`

La **copia completa ZIP** y el **paquete `.gate`** tienen finalidades distintas. El ZIP creado con **Crear copia...** reúne los datos del Gate: proyectos, biblioteca de skills, registros y configuración. Úselo para una copia general o para migrar estos datos a otro equipo. Para restaurarlo, seleccione **Restaurar copia...**, elija el ZIP y revise la vista previa de archivos y categorías. Elija **Sí** para sustituir archivos actuales que coincidan con la copia; **No** para conservar los actuales y restaurar los elementos con nombres alternativos; **Cancelar** para detenerse. Nunca se eliminan archivos ajenos a la copia. Restaurar la configuración de otro equipo puede requerir reiniciar el Gate.

El paquete **`.gate`** contiene solamente una tarea seleccionada: su registro y los archivos de su carpeta de trabajo, como adjuntos y resultados. No incluye la biblioteca completa, la configuración ni otros proyectos y registros. En **Tareas anteriores**, seleccione la tarea y pulse **Exportar tarea como paquete...**. En la otra instalación, use **Importar paquete `.gate`...**. El Gate restaura los archivos en una carpeta exclusiva y crea un registro local. Después, analice la tarea importada para iniciar una conversación nueva con ese contexto. El paquete no transfiere la sesión autenticada ni el identificador de la conversación original; por tanto, no reanuda la sesión anterior. También sirve como copia portátil aislada de una tarea.

Para migrar a otro equipo, instale y abra el Gate y seleccione **Restaurar copia...**. Elija el ZIP copiado del equipo anterior. Si el nuevo equipo aún no tiene datos, elija **Sí** para restaurarlos normalmente. Si ya contiene datos que desea conservar, elija **No**: el Gate mantiene los archivos actuales y añade los restaurados con un sufijo de restauración.

Los datos del programa se guardan en una carpeta propia del Gate. **Abrir datos del Gate** muestra esa carpeta en el Explorador de archivos. Las actualizaciones normales preservan estos datos.

## Codex CLI

El Gate necesita Codex CLI instalado y autenticado para ejecutar tareas. El área **Codex CLI** muestra su estado y ofrece instrucciones de instalación. El Gate busca el ejecutable tanto en PATH como en la instalación de la aplicación Codex en Windows. Puede analizar y organizar una tarea sin el CLI, pero no podrá ejecutarla. **Decisión lista** significa que el análisis terminó y que la ejecución aún necesita autorización; no significa que el modelo haya respondido. Después de **2. Confirmar y ejecutar**, espere la fase **Codex iniciado** y abra **Respuesta** al finalizar. Si no se encuentra el CLI, la tarea no comienza y la pantalla indica el motivo.

Si falla la preparación o la interfaz, el Gate muestra el error en vez de dejar la tarea esperando indefinidamente. Para el diagnóstico, abra la carpeta de la tarea y consulte `.codex-model-gate/startup-status.txt`; los errores de interfaz también se registran en `gui-error.txt`. Crear una carpeta o confirmar la autorización no demuestra, por sí solo, que Codex haya comenzado.

La versión 2.6.5 corrige el cronómetro de inicio y duración. Después de autorizar una tarea nueva o continuar una conversación, compruebe la fase **Codex iniciado** antes de considerar que el proceso comenzó.

El Gate identifica la versión instalada del CLI. Sol 6.1 (`gpt-6.1-sol`) requiere CLI 0.159.1 o posterior; Sol 6 anterior y Luna requieren 0.156.1 o posterior. Use **Descarga / actualización oficial** para abrir las instrucciones oficiales de instalación y actualización y después **Comprobar de nuevo**. **Consultar nuevas versiones** lee el changelog oficial al pulsar el botón, sin descargar ni ejecutar instaladores. El catálogo público local complementa los modelos cuando coincide con la versión identificada. El acceso depende también de la cuenta y del workspace. Los rechazos muestran el diagnóstico; el Gate conserva el modelo autorizado.

## Idioma

Use **Idioma** en la parte superior de la pestaña Tarea. La elección se guarda en la configuración del Gate, se incluye en las copias y permanece en la unidad de la edición portátil. El cambio de idioma reinicia el programa para cargar la interfaz completa de forma coherente. El idioma de la interfaz no cambia automáticamente el idioma de la tarea o de la respuesta de Codex.

## Consejos

- Indique un resultado deseado claro, por ejemplo: “cree un informe PDF con estas secciones”.
- Revise los adjuntos, las skills y la carpeta de destino antes de autorizar.
- Si Codex hace una pregunta, use **Responder pregunta pendiente** para mantener la misma tarea y el mismo contexto.
- El Gate no elimina los archivos producidos al cancelar una ejecución; abra la carpeta de la tarea para revisar lo que ya se creó.


## Cambios de la versión 2.7

Analizar, ejecutar y cancelar permanecen en la barra inferior durante el desplazamiento. El modo simple oculta la biblioteca detallada y los controles técnicos. Las tarjetas distinguen modelo recomendado y seleccionado. Los controles se ajustan al ancho; las tablas tienen desplazamiento horizontal y el historial un divisor ajustable. Copie o exporte la respuesta y abra los diagnósticos directamente. No se permite cambiar idioma durante actividad; al salir se guarda un borrador del pedido y los adjuntos locales disponibles.

Preparación, copia de adjuntos, lectura del historial, indexación de skills, importación/exportación, backups y validación de documentos utilizan trabajos en segundo plano. Las respuestas se muestran antes de actualizar el historial; los archivos no se abren automáticamente. Cancelar termina el árbol de procesos y conserva resultados parciales. Esto reduce bloqueos locales; el tiempo del modelo depende del CLI, la red y la tarea.

Los paquetes incluyen adjuntos activos y remapean resultados a la nueva carpeta. Los backups incluyen carpetas externas de tareas gestionadas; restaurar remapea rutas sin transferir sesiones autenticadas. No se recuperan archivos ausentes en el origen. Restaurar sin sustituir conserva los registros legibles con extensión `.md`. Las credenciales del CLI se excluyen de paquetes y backups. Las escrituras son atómicas, conservan la revisión anterior y muestran errores.

El consumo se agrupa por fecha de cada turno. Los nuevos turnos conservan tarifas y cambio de referencia; **Recalcular con tarifas y cambio actuales** es opcional. Los registros antiguos usan total y fecha disponibles, y tarifas actuales cuando faltan precios históricos. Los registros antiguos de Sol conservan Sol 6 anterior. El esfuerzo se filtra por modelo; Ultra solo aparece cuando lo declara el catálogo público local de la misma versión del CLI.

La apertura automática es opcional, desactivada por defecto, y limitada a tres PDF/imágenes tras validar y guardar correctamente.
