"""Small, dependency-free language packs for the Codex Model Gate UI."""
from __future__ import annotations

import locale
import re


LANGUAGES = {
    "pt-BR": "Português (Brasil)",
    "en": "English",
    "es": "Español",
}


EN = {
    "Codex Model Gate — Decisão Confiável de IA": "Codex Model Gate — Reliable AI Decisions",
    "Tarefa": "Task", "Resposta": "Response", "Tarefas anteriores": "Previous tasks",
    "Arquivos": "Files", "Consumo": "Usage", "Manual": "Guide", "Resposta final da tarefa": "Final task response",
    "Esta tela é aberta automaticamente quando a execução termina.": "This screen opens automatically when execution finishes.",
    "Abrir leitura em tela cheia": "Open full-screen reader", "Fluxo da tarefa": "Task workflow",
    "1. Preparar": "1. Prepare", "2. Descrever": "2. Describe", "3. Conferir decisão": "3. Review decision",
    "4. Autorizar": "4. Approve", "5. Conferir resultado": "5. Review result",
    "Você mantém a decisão final: revise modelo, skills e destino antes de executar.": "You keep the final decision: review the model, skills, and destination before running.",
    "Modo de uso:": "Usage mode:", "Mostrar opções avançadas": "Show advanced options",
    "Como funciona?": "How does it work?", "Instalar Codex CLI...": "Install Codex CLI...",
    "Abrir instruções oficiais": "Open official instructions", "Verificar novamente": "Check again",
    "Armazenamento da versão portátil": "Portable version storage",
    "Pasta de projetos (cada tarefa cria uma subpasta exclusiva):": "Projects folder (each task creates its own subfolder):",
    "Escolher...": "Choose...", "Abrir projetos": "Open projects", "Abrir dados do Gate": "Open Gate data",
    "Fazer backup...": "Create backup...", "Restaurar backup...": "Restore backup...",
    "Biblioteca de conhecimentos (skills)": "Knowledge library (skills)", "Vincular biblioteca...": "Link library...",
    "Abrir biblioteca": "Open library", "Atualizar skills": "Refresh skills", "Começar com um modelo:": "Start from a template:",
    "O que você quer fazer?": "What do you want to do?", "Pesquisa web controlada": "Controlled web research",
    "Pesquisar Google e Bing com o navegador do Gate": "Search Google and Bing with the Gate browser",
    "Permitir navegador visual do Gate (Edge)": "Allow Gate visual browser (Edge)",
    "O Codex inicia imediatamente. O Edge abre apenas se o Codex usar o navegador visual.": "Codex starts immediately. Edge opens only if Codex uses the visual browser.",
    "Consulta (opcional):": "Query (optional):", "Se ficar vazia, o Gate usa a descrição da tarefa. O Edge abre em uma sessão isolada e visível.": "If left blank, the Gate uses the task description. Edge opens in an isolated, visible session.",
    "Termos para busca no Edge (opcional):": "Edge search terms (optional):",
    "Este campo só sugere termos ao Codex: não inicia pesquisa nem abre links. Para analisar uma URL específica, cole-a na descrição da tarefa. O Edge abre apenas se o Codex usar o navegador visual.": "This field only suggests search terms to Codex; it does not start a search or open links. To analyze a specific URL, paste it into the task description. Edge opens only if Codex uses the visual browser.",
    "Arquivos anexados à tarefa": "Files attached to the task", "Anexar arquivos...": "Attach files...",
    "Remover anexo": "Remove attachment", "Abrir anexo": "Open attachment",
    "Conhecimentos especializados (skills):": "Specialized knowledge (skills):",
    "Usar seleção manual (desmarcado: Gate escolhe automaticamente)": "Use manual selection (off: Gate chooses automatically)",
    "Pesquisar skill por nome:": "Search skill by name:", "Limpar busca": "Clear search",
    "Skills recomendadas para esta tarefa": "Skills recommended for this task", "Abrir skill para conferir": "Open skill to review",
    "Instalar skill": "Install skill", "Adicionar skill à tarefa": "Add skill to task", "Remover skill selecionada": "Remove selected skill",
    "Ações principais": "Main actions", "1. Analisar tarefa": "1. Analyze task", "2. Confirmar e executar": "2. Confirm and run",
    "Continuar conversa": "Continue conversation", "Cancelar execução": "Cancel execution",
    "Resumo da decisão": "Decision summary", "Modelo": "Model", "Nível": "Level", "Risco": "Risk", "Skills": "Skills",
    "Política:": "Policy:", "Modelo:": "Model:", "Nível:": "Level:", "Acompanhamento simples:": "Simple progress:",
    "Detalhes técnicos da execução": "Technical execution details", "Progresso": "Progress",
    "Modo Leitura (Tela Cheia)": "Reading Mode (Full Screen)", "Resultados e arquivos criados": "Results and created files",
    "Prévia": "Preview", "Selecione um arquivo": "Select a file", "Abrir arquivo": "Open file",
    "Atualizar lista": "Refresh list", "Registrar resultado": "Record result", "Tarefas anteriores:": "Previous tasks:",
    "Buscar tarefa": "Search tasks", "Palavra ou assunto:": "Word or topic:", "Buscar": "Search",
    "Outros filtros": "Other filters", "Data:": "Date:", "Status:": "Status:", "Skill:": "Skill:",
    "Aplicar filtros": "Apply filters", "Limpar filtros": "Clear filters", "Atualizar registros": "Refresh records",
    "Registros sem avaliação": "Unrated records", "Qualificar registro selecionado": "Rate selected record",
    "Qualificar registro": "Rate record", "Lista ▾": "List ▾",
    "Abrir / exportar ▾": "Open / export ▾", "Pacotes .gate ▾": ".gate packages ▾",
    "Abrir registro em texto": "Open record as text", "Exportar registro TXT/PDF": "Export record TXT/PDF",
    "Gerar relatório dos registros": "Generate records report", "Abrir pasta registro": "Open records folder",
    "Detalhes do registro selecionado": "Selected record details", "Arquivos de tarefas anteriores:": "Files from previous tasks:",
    "Selecionar tarefa anterior...": "Select previous task...", "Abrir pasta da tarefa": "Open task folder",
    "Abrir arquivo selecionado": "Open selected file", "Arquivos gerados ou alterados": "Created or modified files",
    "Manual do Codex Model Gate": "Codex Model Gate Guide",
    "Consulte este guia sempre que quiser entender o fluxo do programa.": "Use this guide whenever you want to understand the application workflow.",
    "Analise a tarefa": "Analyze the task", "Aguardando você descrever uma tarefa.": "Waiting for you to describe a task.",
    "Nenhuma tarefa analisada.": "No task analyzed.", "Aguardando autorização": "Waiting for approval",
    "Tempo decorrido: 00:00": "Elapsed time: 00:00", "Tempo restante: ainda não estimado": "Remaining time: not estimated yet",
    "Modelo legado:": "Legacy model:", "Selecionar...": "Select...",
    "Não avaliado": "Not rated", "Aprovado": "Approved", "Precisou de ajustes": "Needed adjustments", "Falhou": "Failed",
    "Escolha um modelo...": "Choose a template...", "Criar documento": "Create a document", "Analisar arquivo": "Analyze a file",
    "Gerar imagem": "Generate an image", "Pesquisar referências": "Research references", "Organizar dados": "Organize data",
    "Nenhuma biblioteca de skills vinculada.": "No skill library linked.", "Carregando registros...": "Loading records...",
    "Selecione uma tarefa na aba “Tarefas anteriores” para ver seus arquivos.": "Select a task in the “Previous tasks” tab to see its files.",
    "Consumo de tokens e custos": "Token usage and costs", "Resumo calculado a partir dos registros locais de execução. Os valores são estimativas.": "Summary based on local execution records. Values are estimates.",
    "Período e moeda": "Period and currency", "Período:": "Period:", "Hoje": "Today", "Últimos 7 dias": "Last 7 days", "Este mês": "This month", "Este ano": "This year", "Todo o período": "All time", "Personalizado": "Custom",
    "Moeda:": "Currency:", "Automática": "Automatic", "Atualizar": "Refresh", "De (DD/MM/AAAA):": "From (YYYY-MM-DD):", "Até (DD/MM/AAAA):": "To (YYYY-MM-DD):", "Totais do período": "Period totals", "Por intervalo": "Breakdown",
    "Custo total estimado": "Total estimated cost", "Tarefas com uso informado": "Tasks with reported usage", "Tokens": "Tokens", "entrada": "input", "cache": "cache", "saída": "output", "raciocínio": "reasoning", "registro(s) sem dados suficientes para calcular o custo": "record(s) without enough data to calculate cost", "Informe um intervalo válido no formato AAAA-MM-DD.": "Enter a valid date range in YYYY-MM-DD format.", "Tarefas": "Tasks", "Custo estimado": "Estimated cost",
    "Todos os modelos": "All models", "Registros no período": "Records in period", "Incluídos nos totais": "Included in totals", "Excluídos por falta de dados de tokens ou modelo": "Excluded due to missing token or model data", "Exportar CSV...": "Export CSV...", "Exportar consumo": "Export usage", "Resumo exportado com sucesso.": "Summary exported successfully.",
    "Período": "Period", "Entrada": "Input", "Cache": "Cache", "Saída": "Output", "Raciocínio": "Reasoning",
    "Sem dados para estimar o custo": "Records without enough data to estimate cost",
    "Informe um intervalo válido no formato DD/MM/AAAA.": "Enter a valid date range in YYYY-MM-DD format.",
    "execução": "run", "execuções": "runs",
    "Consumo estimado": "Estimated usage", "Consumo desta tarefa": "This task's usage",
    "Custo estimado indisponível: modelo ou uso não identificado.": "Estimated cost unavailable: model or usage not identified.",
    "Alterado em": "Modified on",
    "de": "of", "registro exibido": "record shown", "registros exibidos": "records shown",
    "arquivo": "file", "arquivos": "files",
    "Quando preparar esta tarefa?": "When should this task be prepared?",
    "Use DD/MM/AAAA HH:MM (horário local).": "Use YYYY-MM-DD HH:MM (local time).",
    "Informe data e hora no formato DD/MM/AAAA HH:MM.": "Enter date and time in YYYY-MM-DD HH:MM format.",
}

ES = {
    "Codex Model Gate — Decisão Confiável de IA": "Codex Model Gate — Decisiones confiables de IA",
    "Tarefa": "Tarea", "Resposta": "Respuesta", "Tarefas anteriores": "Tareas anteriores",
    "Arquivos": "Archivos", "Consumo": "Consumo", "Manual": "Manual", "Resposta final da tarefa": "Respuesta final de la tarea",
    "Esta tela é aberta automaticamente quando a execução termina.": "Esta pantalla se abre automáticamente cuando finaliza la ejecución.",
    "Abrir leitura em tela cheia": "Abrir lectura en pantalla completa", "Fluxo da tarefa": "Flujo de la tarea",
    "1. Preparar": "1. Preparar", "2. Descrever": "2. Describir", "3. Conferir decisão": "3. Revisar decisión",
    "4. Autorizar": "4. Autorizar", "5. Conferir resultado": "5. Revisar resultado",
    "Você mantém a decisão final: revise modelo, skills e destino antes de executar.": "Usted mantiene la decisión final: revise el modelo, las skills y el destino antes de ejecutar.",
    "Modo de uso:": "Modo de uso:", "Mostrar opções avançadas": "Mostrar opciones avanzadas", "Como funciona?": "¿Cómo funciona?",
    "Instalar Codex CLI...": "Instalar Codex CLI...", "Abrir instruções oficiais": "Abrir instrucciones oficiales",
    "Verificar novamente": "Comprobar de nuevo", "Armazenamento da versão portátil": "Almacenamiento de la versión portátil",
    "Pasta de projetos (cada tarefa cria uma subpasta exclusiva):": "Carpeta de proyectos (cada tarea crea su propia subcarpeta):",
    "Escolher...": "Elegir...", "Abrir projetos": "Abrir proyectos", "Abrir dados do Gate": "Abrir datos del Gate",
    "Fazer backup...": "Crear copia...", "Restaurar backup...": "Restaurar copia...",
    "Biblioteca de conhecimentos (skills)": "Biblioteca de conocimientos (skills)", "Vincular biblioteca...": "Vincular biblioteca...",
    "Abrir biblioteca": "Abrir biblioteca", "Atualizar skills": "Actualizar skills", "Começar com um modelo:": "Comenzar con una plantilla:",
    "O que você quer fazer?": "¿Qué quiere hacer?", "Pesquisa web controlada": "Búsqueda web controlada",
    "Pesquisar Google e Bing com o navegador do Gate": "Buscar en Google y Bing con el navegador del Gate",
    "Permitir navegador visual do Gate (Edge)": "Permitir navegador visual del Gate (Edge)",
    "O Codex inicia imediatamente. O Edge abre apenas se o Codex usar o navegador visual.": "Codex comienza de inmediato. Edge solo se abre si Codex usa el navegador visual.",
    "Consulta (opcional):": "Consulta (opcional):", "Se ficar vazia, o Gate usa a descrição da tarefa. O Edge abre em uma sessão isolada e visível.": "Si queda vacía, el Gate usa la descripción de la tarea. Edge se abre en una sesión aislada y visible.",
    "Termos para busca no Edge (opcional):": "Términos para buscar en Edge (opcional):",
    "Este campo só sugere termos ao Codex: não inicia pesquisa nem abre links. Para analisar uma URL específica, cole-a na descrição da tarefa. O Edge abre apenas se o Codex usar o navegador visual.": "Este campo solo sugiere términos a Codex: no inicia una búsqueda ni abre enlaces. Para analizar una URL específica, péguela en la descripción de la tarea. Edge se abre solo si Codex utiliza el navegador visual.",
    "Arquivos anexados à tarefa": "Archivos adjuntos a la tarea", "Anexar arquivos...": "Adjuntar archivos...",
    "Remover anexo": "Quitar adjunto", "Abrir anexo": "Abrir adjunto", "Conhecimentos especializados (skills):": "Conocimientos especializados (skills):",
    "Usar seleção manual (desmarcado: Gate escolhe automaticamente)": "Usar selección manual (desactivado: Gate elige automáticamente)",
    "Pesquisar skill por nome:": "Buscar skill por nombre:", "Limpar busca": "Limpiar búsqueda",
    "Skills recomendadas para esta tarefa": "Skills recomendadas para esta tarea", "Abrir skill para conferir": "Abrir skill para revisar",
    "Instalar skill": "Instalar skill", "Adicionar skill à tarefa": "Añadir skill a la tarea", "Remover skill selecionada": "Quitar skill seleccionada",
    "Ações principais": "Acciones principales", "1. Analisar tarefa": "1. Analizar tarea", "2. Confirmar e executar": "2. Confirmar y ejecutar",
    "Continuar conversa": "Continuar conversación", "Cancelar execução": "Cancelar ejecución",
    "Resumo da decisão": "Resumen de la decisión", "Modelo": "Modelo", "Nível": "Nivel", "Risco": "Riesgo", "Skills": "Skills",
    "Política:": "Política:", "Modelo:": "Modelo:", "Nível:": "Nivel:", "Acompanhamento simples:": "Seguimiento simple:",
    "Detalhes técnicos da execução": "Detalles técnicos de la ejecución", "Progresso": "Progreso",
    "Modo Leitura (Tela Cheia)": "Modo lectura (pantalla completa)", "Resultados e arquivos criados": "Resultados y archivos creados",
    "Prévia": "Vista previa", "Selecione um arquivo": "Seleccione un archivo", "Abrir arquivo": "Abrir archivo",
    "Atualizar lista": "Actualizar lista", "Registrar resultado": "Registrar resultado", "Tarefas anteriores:": "Tareas anteriores:",
    "Buscar tarefa": "Buscar tarea", "Palavra ou assunto:": "Palabra o tema:", "Buscar": "Buscar",
    "Outros filtros": "Otros filtros", "Data:": "Fecha:", "Status:": "Estado:", "Skill:": "Skill:",
    "Aplicar filtros": "Aplicar filtros", "Limpar filtros": "Limpiar filtros", "Atualizar registros": "Actualizar registros",
    "Registros sem avaliação": "Registros sin evaluar", "Qualificar registro selecionado": "Evaluar registro seleccionado",
    "Qualificar registro": "Evaluar registro", "Lista ▾": "Lista ▾",
    "Abrir / exportar ▾": "Abrir / exportar ▾", "Pacotes .gate ▾": "Paquetes .gate ▾",
    "Abrir registro em texto": "Abrir registro como texto", "Exportar registro TXT/PDF": "Exportar registro TXT/PDF",
    "Gerar relatório dos registros": "Generar informe de registros", "Abrir pasta registro": "Abrir carpeta de registros",
    "Detalhes do registro selecionado": "Detalles del registro seleccionado", "Arquivos de tarefas anteriores:": "Archivos de tareas anteriores:",
    "Selecionar tarefa anterior...": "Seleccionar tarea anterior...", "Abrir pasta da tarefa": "Abrir carpeta de la tarea",
    "Abrir arquivo selecionado": "Abrir archivo seleccionado", "Arquivos gerados ou alterados": "Archivos creados o modificados",
    "Manual do Codex Model Gate": "Manual de Codex Model Gate",
    "Consulte este guia sempre que quiser entender o fluxo do programa.": "Consulte esta guía cuando quiera entender el flujo del programa.",
    "Analise a tarefa": "Analice la tarea", "Aguardando você descrever uma tarefa.": "Esperando que describa una tarea.",
    "Nenhuma tarefa analisada.": "Ninguna tarea analizada.", "Aguardando autorização": "Esperando autorización",
    "Tempo decorrido: 00:00": "Tiempo transcurrido: 00:00", "Tempo restante: ainda não estimado": "Tiempo restante: aún no estimado",
    "Modelo legado:": "Modelo heredado:", "Selecionar...": "Seleccionar...",
    "Não avaliado": "Sin evaluar", "Aprovado": "Aprobado", "Precisou de ajustes": "Necesitó ajustes", "Falhou": "Falló",
    "Escolha um modelo...": "Elija una plantilla...", "Criar documento": "Crear un documento", "Analisar arquivo": "Analizar un archivo",
    "Gerar imagem": "Generar una imagen", "Pesquisar referências": "Buscar referencias", "Organizar dados": "Organizar datos",
    "Nenhuma biblioteca de skills vinculada.": "Ninguna biblioteca de skills vinculada.", "Carregando registros...": "Cargando registros...",
    "Selecione uma tarefa na aba “Tarefas anteriores” para ver seus arquivos.": "Seleccione una tarea en la pestaña “Tareas anteriores” para ver sus archivos.",
    "Consumo de tokens e custos": "Consumo de tokens y costos", "Resumo calculado a partir dos registros locais de execução. Os valores são estimativas.": "Resumen calculado a partir de los registros locales de ejecución. Los valores son estimaciones.",
    "Período e moeda": "Período y moneda", "Período:": "Período:", "Hoje": "Hoy", "Últimos 7 dias": "Últimos 7 días", "Este mês": "Este mes", "Este ano": "Este año", "Todo o período": "Todo el período", "Personalizado": "Personalizado",
    "Moeda:": "Moneda:", "Automática": "Automática", "Atualizar": "Actualizar", "De (DD/MM/AAAA):": "Desde (DD/MM/AAAA):", "Até (DD/MM/AAAA):": "Hasta (DD/MM/AAAA):", "Totais do período": "Totales del período", "Por intervalo": "Desglose",
    "Custo total estimado": "Costo total estimado", "Tarefas com uso informado": "Tareas con uso informado", "Tokens": "Tokens", "entrada": "entrada", "cache": "caché", "saída": "salida", "raciocínio": "razonamiento", "registro(s) sem dados suficientes para calcular o custo": "registro(s) sin datos suficientes para calcular el costo", "Informe um intervalo válido no formato AAAA-MM-DD.": "Introduzca un intervalo válido en formato AAAA-MM-DD.", "Tarefas": "Tareas", "Custo estimado": "Costo estimado",
    "Todos os modelos": "Todos los modelos", "Registros no período": "Registros en el período", "Incluídos nos totais": "Incluidos en los totales", "Excluídos por falta de dados de tokens ou modelo": "Excluidos por falta de datos de tokens o modelo", "Exportar CSV...": "Exportar CSV...", "Exportar consumo": "Exportar consumo", "Resumo exportado com sucesso.": "Resumen exportado correctamente.",
    "Período": "Período", "Entrada": "Entrada", "Cache": "Caché", "Saída": "Salida", "Raciocínio": "Razonamiento",
    "Sem dados para estimar o custo": "Registros sin datos suficientes para estimar el costo",
    "Informe um intervalo válido no formato DD/MM/AAAA.": "Introduzca un intervalo válido en formato DD/MM/AAAA.",
    "execução": "ejecución", "execuções": "ejecuciones",
    "Consumo estimado": "Consumo estimado", "Consumo desta tarefa": "Consumo de esta tarea",
    "Custo estimado indisponível: modelo ou uso não identificado.": "Costo estimado no disponible: modelo o consumo no identificado.",
    "Alterado em": "Modificado el",
    "de": "de", "registro exibido": "registro mostrado", "registros exibidos": "registros mostrados",
    "arquivo": "archivo", "arquivos": "archivos",
    "Quando preparar esta tarefa?": "¿Cuándo se debe preparar esta tarea?",
    "Use DD/MM/AAAA HH:MM (horário local).": "Use DD/MM/AAAA HH:MM (hora local).",
    "Informe data e hora no formato DD/MM/AAAA HH:MM.": "Introduzca la fecha y hora en formato DD/MM/AAAA HH:MM.",
}

# Text that appears after the window has been built (status messages, dialogs,
# counters and secondary controls). Keeping it in the same packs prevents a
# translated shell from falling back to Portuguese during normal use.
EN.update({
    "Decisão clara. Execução sob seu controle.": "Clear decisions. Execution under your control.",
    "equilibrada": "balanced", "cautelosa": "cautious", "rigorosa": "strict",
    "Leve": "Low", "Médio": "Medium", "Alto": "High", "Extra alto": "Extra high", "Máximo": "Maximum", "Ultra": "Ultra",
    "Nenhuma": "None", "nenhuma": "none", "nenhum": "none",
    "Idioma / Language:": "Language:", "Automático é recomendado: o Gate explica abaixo por que cada instrução especializada foi escolhida. Use a seleção manual apenas quando quiser substituir a recomendação.": "Automatic selection is recommended: the Gate explains why each specialized instruction was chosen. Use manual selection only when you want to replace the recommendation.",
    "Selecione uma skill para conferir as instruções completas. A explicação após o travessão informa a relevância identificada.": "Select a skill to review its complete instructions. The explanation after the dash shows its identified relevance.",
    "Responder pergunta pendente": "Answer pending question", "Ctrl+Enter: analisar  •  Ctrl+Shift+Enter: executar": "Ctrl+Enter: analyze  •  Ctrl+Shift+Enter: run",
    "Resumo antes de executar": "Review before running", "MODELO RECOMENDADO": "RECOMMENDED MODEL", "NÍVEL": "LEVEL", "RISCO": "RISK", "SKILLS RELEVANTES": "RELEVANT SKILLS",
    "Analise a tarefa para ver justificativa, risco e controles.": "Analyze the task to see the rationale, risk, and controls.",
    "Depois de analisar a tarefa, confirme o resultado esperado, os anexos e a pasta de destino.": "After analyzing the task, confirm the expected result, attachments, and destination folder.",
    "Modo simples ativado: mostro apenas o necessário para concluir a tarefa.": "Simple mode enabled: only what is needed to complete the task is shown.",
    "Modo avançado ativado: você pode ajustar os controles técnicos.": "Advanced mode enabled: you can adjust the technical controls.",
    "Selecione um resultado para ver tipo, tamanho e data.": "Select a result to see its type, size, and date.",
    "Continuar conversa": "Continue conversation", "Registros sem avaliação": "Unrated records", "Qualificar resultado": "Rate result",
    "Como você avalia o resultado desta tarefa?": "How do you rate the result of this task?", "Salvar avaliação": "Save rating", "Cancelar": "Cancel",
    "Boas-vindas ao Codex Model Gate": "Welcome to Codex Model Gate", "Comece em poucos passos": "Get started in a few steps", "Entendi, começar": "Got it, start",
    "Resposta Final da Tarefa": "Final Task Response", "Conversar nesta tarefa": "Continue this task", "Última resposta do Codex:": "Latest Codex response:", "Nova mensagem:": "New message:",
    "Abrir arquivos da tarefa": "Open task files", "Enviar e continuar conversa": "Send and continue conversation",
    "Link inválido": "Invalid link", "Este endereço não pode ser aberto com segurança.": "This address cannot be opened safely.", "Não foi possível abrir o link": "Could not open the link", "Confira se existe um navegador padrão configurado no Windows.": "Check that a default browser is configured in Windows.",
    "Continuar conversa": "Continue conversation", "Continuação pendente": "Pending continuation", "Conversa indisponível": "Conversation unavailable", "Tarefas anteriores": "Previous tasks", "Arquivos anteriores": "Previous files", "Registros": "Records",
    "Exportar registro": "Export record", "Resultado": "Result", "Pasta": "Folder", "Biblioteca de skills": "Skill library", "Adicionar skill": "Add skill", "Remover skill": "Remove skill", "Anexos": "Attachments",
    "Continuação": "Continuation", "Nova mensagem": "New message", "Sua resposta": "Your response", "Codex CLI ausente": "Codex CLI missing", "Autorização": "Approval", "Decisão": "Decision",
    "Confirmação reforçada": "Additional confirmation", "Confirmar execução": "Confirm execution", "Cancelar execução": "Cancel execution", "Falha na execução": "Execution failed", "Validação de documento": "Document validation", "Arquivo": "File", "Atividade em andamento": "Activity in progress",
    "Usar modelo de tarefa": "Use task template", "Substituir o texto atual pelo modelo escolhido?": "Replace the current text with the selected template?",
    "Selecione um registro antes de exportar.": "Select a record before exporting.", "Selecione um arquivo da lista.": "Select a file from the list.", "Descreva a tarefa primeiro.": "Describe the task first.",
    "Mostrar todos os registros": "Show all records", "Nenhum registro corresponde aos filtros atuais.": "No records match the current filters.",
    "Nenhum registro persistente encontrado ainda. Os próximos resultados executados pelo Gate serão salvos aqui, mesmo após fechar o programa.": "No saved records were found yet. Future results run by the Gate will be saved here, even after the application is closed.",
    "Analise uma tarefa antes de executar.": "Analyze a task before running it.", "Escolha um modelo e um nível válidos.": "Choose a valid model and reasoning level.",
    "O Codex CLI não foi encontrado.": "Codex CLI was not found.", "A execução foi mantida bloqueada.": "Execution remains blocked.",
    "Selecione um arquivo da lista para remover.": "Select a file from the list to remove.", "Selecione um arquivo da lista para abrir.": "Select a file from the list to open.",
    "Aguarde a análise ou a execução terminar antes de fechar o Codex Model Gate.": "Wait for analysis or execution to finish before closing Codex Model Gate.",
    "Crie um documento sobre [tema], com [seções desejadas], em formato [DOCX/PDF]. Use linguagem [tom] e salve o resultado final na pasta da tarefa.": "Create a document about [topic], with [desired sections], in [DOCX/PDF] format. Use a [tone] style and save the final result in the task folder.",
    "Analise os arquivos anexados. Explique os principais achados, apresente pontos de atenção e crie um resumo em [formato desejado].": "Analyze the attached files. Explain the main findings, highlight points that require attention, and create a summary in [desired format].",
    "Crie uma imagem de [assunto], para uso em [finalidade], com estilo [estilo], proporção [proporção] e texto [se houver]. Salve o arquivo final na pasta da tarefa.": "Create an image of [subject] for [purpose], using [style], [aspect ratio], and [text, if any]. Save the final file in the task folder.",
    "Pesquise referências confiáveis sobre [tema]. Entregue uma síntese objetiva e uma lista de fontes verificáveis em [formato de citação].": "Research reliable references about [topic]. Deliver a concise synthesis and a list of verifiable sources in [citation format].",
    "Organize os dados ou arquivos anexados. Explique os critérios usados, identifique inconsistências e gere [arquivo final desejado].": "Organize the attached data or files. Explain the criteria used, identify inconsistencies, and produce [desired final file].",
})

ES.update({
    "Decisão clara. Execução sob seu controle.": "Decisiones claras. Ejecución bajo su control.",
    "equilibrada": "equilibrada", "cautelosa": "cautelosa", "rigorosa": "rigurosa",
    "Leve": "Bajo", "Médio": "Medio", "Alto": "Alto", "Extra alto": "Extra alto", "Máximo": "Máximo", "Ultra": "Ultra",
    "Nenhuma": "Ninguna", "nenhuma": "ninguna", "nenhum": "ninguno",
    "Idioma / Language:": "Idioma:", "Automático é recomendado: o Gate explica abaixo por que cada instrução especializada foi escolhida. Use a seleção manual apenas quando quiser substituir a recomendação.": "Se recomienda la selección automática: el Gate explica por qué se eligió cada instrucción especializada. Use la selección manual solo cuando quiera reemplazar la recomendación.",
    "Selecione uma skill para conferir as instruções completas. A explicação após o travessão informa a relevância identificada.": "Seleccione una skill para revisar sus instrucciones completas. La explicación después del guion muestra la relevancia identificada.",
    "Responder pergunta pendente": "Responder pregunta pendiente", "Ctrl+Enter: analisar  •  Ctrl+Shift+Enter: executar": "Ctrl+Enter: analizar  •  Ctrl+Shift+Enter: ejecutar",
    "Resumo antes de executar": "Revisión antes de ejecutar", "MODELO RECOMENDADO": "MODELO RECOMENDADO", "NÍVEL": "NIVEL", "RISCO": "RIESGO", "SKILLS RELEVANTES": "SKILLS RELEVANTES",
    "Analise a tarefa para ver justificativa, risco e controles.": "Analice la tarea para ver la justificación, el riesgo y los controles.",
    "Depois de analisar a tarefa, confirme o resultado esperado, os anexos e a pasta de destino.": "Después de analizar la tarea, confirme el resultado esperado, los adjuntos y la carpeta de destino.",
    "Modo simples ativado: mostro apenas o necessário para concluir a tarefa.": "Modo simple activado: solo se muestra lo necesario para completar la tarea.",
    "Modo avançado ativado: você pode ajustar os controles técnicos.": "Modo avanzado activado: puede ajustar los controles técnicos.",
    "Selecione um resultado para ver tipo, tamanho e data.": "Seleccione un resultado para ver su tipo, tamaño y fecha.",
    "Registros sem avaliação": "Registros sin evaluar", "Qualificar resultado": "Evaluar resultado", "Como você avalia o resultado desta tarefa?": "¿Cómo evalúa el resultado de esta tarea?", "Salvar avaliação": "Guardar evaluación", "Cancelar": "Cancelar",
    "Boas-vindas ao Codex Model Gate": "Bienvenido a Codex Model Gate", "Comece em poucos passos": "Comience en pocos pasos", "Entendi, começar": "Entendido, comenzar",
    "Resposta Final da Tarefa": "Respuesta final de la tarea", "Conversar nesta tarefa": "Conversar en esta tarea", "Última resposta do Codex:": "Última respuesta de Codex:", "Nova mensagem:": "Nuevo mensaje:",
    "Abrir arquivos da tarefa": "Abrir archivos de la tarea", "Enviar e continuar conversa": "Enviar y continuar conversación",
    "Link inválido": "Enlace no válido", "Este endereço não pode ser aberto com segurança.": "Esta dirección no se puede abrir de forma segura.", "Não foi possível abrir o link": "No se pudo abrir el enlace", "Confira se existe um navegador padrão configurado no Windows.": "Compruebe que haya un navegador predeterminado configurado en Windows.",
    "Continuação pendente": "Continuación pendiente", "Conversa indisponível": "Conversación no disponible", "Arquivos anteriores": "Archivos anteriores", "Registros": "Registros", "Qualificar registro": "Evaluar registro",
    "Exportar registro": "Exportar registro", "Resultado": "Resultado", "Pasta": "Carpeta", "Biblioteca de skills": "Biblioteca de skills", "Adicionar skill": "Añadir skill", "Remover skill": "Quitar skill", "Anexos": "Adjuntos",
    "Continuação": "Continuación", "Nova mensagem": "Nuevo mensaje", "Sua resposta": "Su respuesta", "Codex CLI ausente": "Falta Codex CLI", "Autorização": "Autorización", "Decisão": "Decisión",
    "Confirmação reforçada": "Confirmación adicional", "Confirmar execução": "Confirmar ejecución", "Cancelar execução": "Cancelar ejecución", "Falha na execução": "Error de ejecución", "Validação de documento": "Validación de documento", "Arquivo": "Archivo", "Atividade em andamento": "Actividad en curso",
    "Usar modelo de tarefa": "Usar plantilla de tarea", "Substituir o texto atual pelo modelo escolhido?": "¿Reemplazar el texto actual por la plantilla seleccionada?",
    "Selecione um registro antes de exportar.": "Seleccione un registro antes de exportarlo.", "Selecione um arquivo da lista.": "Seleccione un archivo de la lista.", "Descreva a tarefa primeiro.": "Describa primero la tarea.",
    "Mostrar todos os registros": "Mostrar todos los registros", "Nenhum registro corresponde aos filtros atuais.": "Ningún registro coincide con los filtros actuales.",
    "Nenhum registro persistente encontrado ainda. Os próximos resultados executados pelo Gate serão salvos aqui, mesmo após fechar o programa.": "Aún no se encontraron registros guardados. Los próximos resultados ejecutados por el Gate se guardarán aquí, incluso después de cerrar el programa.",
    "Analise uma tarefa antes de executar.": "Analice una tarea antes de ejecutarla.", "Escolha um modelo e um nível válidos.": "Elija un modelo y un nivel válidos.",
    "O Codex CLI não foi encontrado.": "No se encontró Codex CLI.", "A execução foi mantida bloqueada.": "La ejecución permanece bloqueada.",
    "Selecione um arquivo da lista para remover.": "Seleccione un archivo de la lista para quitarlo.", "Selecione um arquivo da lista para abrir.": "Seleccione un archivo de la lista para abrirlo.",
    "Aguarde a análise ou a execução terminar antes de fechar o Codex Model Gate.": "Espere a que termine el análisis o la ejecución antes de cerrar Codex Model Gate.",
    "Crie um documento sobre [tema], com [seções desejadas], em formato [DOCX/PDF]. Use linguagem [tom] e salve o resultado final na pasta da tarefa.": "Cree un documento sobre [tema], con [secciones deseadas], en formato [DOCX/PDF]. Use un estilo [tono] y guarde el resultado final en la carpeta de la tarea.",
    "Analise os arquivos anexados. Explique os principais achados, apresente pontos de atenção e crie um resumo em [formato desejado].": "Analice los archivos adjuntos. Explique los principales hallazgos, señale los puntos que requieren atención y cree un resumen en [formato deseado].",
    "Crie uma imagem de [assunto], para uso em [finalidade], com estilo [estilo], proporção [proporção] e texto [se houver]. Salve o arquivo final na pasta da tarefa.": "Cree una imagen de [asunto] para [finalidad], con estilo [estilo], proporción [proporción] y texto [si lo hay]. Guarde el archivo final en la carpeta de la tarea.",
    "Pesquise referências confiáveis sobre [tema]. Entregue uma síntese objetiva e uma lista de fontes verificáveis em [formato de citação].": "Busque referencias confiables sobre [tema]. Entregue una síntesis objetiva y una lista de fuentes verificables en [formato de cita].",
    "Organize os dados ou arquivos anexados. Explique os critérios usados, identifique inconsistências e gere [arquivo final desejado].": "Organice los datos o archivos adjuntos. Explique los criterios utilizados, identifique inconsistencias y genere [archivo final deseado].",
})

EN.update({
    "Falha anterior do Codex CLI": "Previous Codex CLI failure",
    "Esta tarefa terminou antes de receber uma resposta. Atualize o Codex CLI e analise a pergunta novamente.": "This task ended before receiving an answer. Update Codex CLI and analyze the question again.",
    "Atualizar Codex CLI...": "Update Codex CLI...",
    "Atualização do Codex CLI": "Codex CLI update",
    "Falha do Codex CLI": "Codex CLI failure",
    "Atualizar Codex CLI": "Update Codex CLI",
    "A instalação baixa software da OpenAI e pode exigir conexão, permissões ou aprovação da política da sua organização. Se o CLI pedir autenticação, entre com sua conta.": "The installer downloads OpenAI software and may require connectivity, permissions, or approval under your organization’s policy. If the CLI asks you to sign in, use your account.",
    "O Codex CLI recusou {model}. Confira a versão do CLI, a autenticação e a disponibilidade do modelo nesse cliente. O Gate não altera o modelo autorizado automaticamente.": "Codex CLI rejected {model}. Check the CLI version, authentication, and model availability in that client. Gate does not change the approved model automatically.",
    "Análise desatualizada": "Analysis out of date",
    "A tarefa ou os anexos mudaram. Clique em Analisar tarefa novamente antes de executar.": "The task or attachments changed. Select Analyze task again before running.",
})
ES.update({
    "Falha anterior do Codex CLI": "Fallo anterior de Codex CLI",
    "Esta tarefa terminou antes de receber uma resposta. Atualize o Codex CLI e analise a pergunta novamente.": "Esta tarea terminó antes de recibir una respuesta. Actualice Codex CLI y analice la pregunta de nuevo.",
    "Atualizar Codex CLI...": "Actualizar Codex CLI...",
    "Atualização do Codex CLI": "Actualización de Codex CLI",
    "Falha do Codex CLI": "Fallo de Codex CLI",
    "Atualizar Codex CLI": "Actualizar Codex CLI",
    "A instalação baixa software da OpenAI e pode exigir conexão, permissões ou aprovação da política da sua organização. Se o CLI pedir autenticação, entre com sua conta.": "El instalador descarga software de OpenAI y puede requerir conexión, permisos o aprobación de la política de su organización. Si CLI solicita autenticación, inicie sesión con su cuenta.",
    "O Codex CLI recusou {model}. Confira a versão do CLI, a autenticação e a disponibilidade do modelo nesse cliente. O Gate não altera o modelo autorizado automaticamente.": "Codex CLI rechazó {model}. Compruebe la versión de CLI, la autenticación y la disponibilidad del modelo en ese cliente. Gate no cambia automáticamente el modelo autorizado.",
    "Análise desatualizada": "Análisis desactualizado",
    "A tarefa ou os anexos mudaram. Clique em Analisar tarefa novamente antes de executar.": "La tarea o los archivos adjuntos cambiaron. Seleccione Analizar tarea de nuevo antes de ejecutar.",
})

PACKS = {"pt-BR": {}, "en": EN, "es": ES}

MANUALS = {
    "en": """# Codex Model Gate Guide

The Gate organizes tasks run by Codex CLI. It helps you describe the work, review the recommended model and skills, approve execution, and find the results later.

## Basic workflow

1. Write the task in the **Task** tab and attach files if needed.
2. Select **Analyze task** to review the model, reasoning level, risk, and skills.
3. Select **Confirm and run** after checking the destination and decision.
4. Read the result in the **Response** tab. Web links are clickable.
5. Use **Previous tasks** to search, review, or continue a saved conversation.

## Language

Use **Language** at the top of the Task tab. The choice is saved in the Gate settings and included in backups. Changing it restarts the application so the complete interface is loaded consistently.

## Safety and data

The Gate never changes the language of your task or answer automatically. Each task uses its own folder. Review the model, skills, attachments, and destination before approval. Use **Create backup** to preserve projects, skills, records, and settings.
""",
    "es": """# Manual de Codex Model Gate

El Gate organiza las tareas ejecutadas por Codex CLI. Le ayuda a describir el trabajo, revisar el modelo y las skills recomendadas, autorizar la ejecución y encontrar los resultados posteriormente.

## Flujo básico

1. Escriba la tarea en la pestaña **Tarea** y adjunte archivos si es necesario.
2. Seleccione **Analizar tarea** para revisar el modelo, nivel de razonamiento, riesgo y skills.
3. Seleccione **Confirmar y ejecutar** después de comprobar el destino y la decisión.
4. Lea el resultado en la pestaña **Respuesta**. Los enlaces web son clicables.
5. Use **Tareas anteriores** para buscar, revisar o continuar una conversación guardada.

## Idioma

Use **Idioma** en la parte superior de la pestaña Tarea. La elección se guarda en la configuración del Gate y se incluye en las copias de seguridad. El cambio reinicia la aplicación para cargar toda la interfaz de forma coherente.

## Seguridad y datos

El Gate no cambia automáticamente el idioma de su tarea o respuesta. Cada tarea utiliza su propia carpeta. Revise el modelo, las skills, los adjuntos y el destino antes de autorizar. Use **Crear copia** para conservar proyectos, skills, registros y configuración.
""",
}

# Complete manuals: these intentionally mirror every section in the Portuguese
# guide instead of offering a shortened foreign-language quick start.
MANUALS["en"] = """# Codex Model Gate Guide

Codex Model Gate organizes tasks run by Codex CLI. It helps you prepare the request, review the recommended model and skills, approve execution, and find the results later.

## Start here

1. In the **Task** tab, choose where projects will be stored.
2. Write what you want to do and, if necessary, use **Attach files...**.
3. Select **Analyze task**. The Gate recommends a model, reasoning level, and skills.
4. Review the decision. You may adjust the skill selection before continuing.
5. Select **Confirm and run**. Files are kept in the task's exclusive folder.
6. When finished, review the result, open the created files, and record their quality.

### Simple mode and task templates

The application opens in **simple mode**, with the essential controls for preparing, analyzing, and running a task. Directly below the description, web research, and attachments are **1. Analyze task** and **2. Confirm and run**, followed by the model, reasoning level, risk, and skill summary. The detailed library and monitoring area appear farther down. Use `Ctrl+Enter` to analyze and `Ctrl+Shift+Enter` to run. Enable **Show advanced options** when you want to choose the policy, model, reasoning level, or skill library, or inspect technical execution details.

The buttons use the interface's existing colors to show progress: **Analyze task** turns blue when a description is ready. After analysis it turns green with a checkmark, and **Confirm and run** turns blue. Once execution is started, the second button also turns green. Changing the description or attachments returns the controls to the preparation state; analyze again before running.
Selecting **Confirm and run** opens the approval dialog over the main window. The Codex CLI version check runs in the background without opening another window.

Under **Start from a template**, choose a starting point for creating a document, analyzing a file, generating an image, researching references, or organizing data. Replace the fields in brackets with your context before analyzing.

## Model and reasoning level

The Gate recommends the main GPT-6 models according to the **complexity of the requested result**, not the number of words in the request. **Luna — Low** handles bounded lookups and transformations, such as a public date or current exchange rate, with an appropriate source when needed. **Sol — Low** handles explicit fact checks; **Sol — Medium/High** handles research, synthesis, creation, specialized judgment, and work with meaningful impact. **Astra — Medium/High** handles broad deliverables with interdependent steps and decisions, with more review for high-impact work. The assessment also shows risk, tool use, specialization, verifiability, and ambiguity. The final model and effort choice remains with the user in advanced options. Legacy models are in the separate **Legacy model** selector for manual use; older Terra records remain supported.

**Low** is for quick requests; **Medium** balances planning and speed; **High** and **Extra high** serve difficult work involving several steps, sources, or decisions. **Maximum** is not recommended automatically. **Ultra** is not available for the GPT-6 family and is not recommended automatically; choose an effort supported by the selected model.

Requests to explain how a technical mechanism works, including downconversion and upconversion, receive at least **Sol — Medium** in Portuguese, English, or Spanish. The Gate considers the explanation required even when the question is short.

### Interface responsiveness

When a task completes, the Gate opens the answer before updating files and history. The usage dashboard reuses records already loaded, and the duration estimate uses the same data. The Codex CLI version checked in the current session is reused at authorization, and progress messages are grouped to keep the window responsive. These changes reduce interface delays; model response time still depends on the task, the selected effort, and Codex CLI.

### Usage and estimated cost

For conversations with several responses, the task record lists time and tokens for each execution separately. The **Usage** tab sums the tokens reported by those executions. Older records without this breakdown retain the available total.

After a task runs, the Gate displays the input, cached input, output, and reasoning tokens reported by Codex CLI, plus the estimated cost for the selected model. Costs use two decimal places and the currency associated with the interface language. If the CLI does not report usage, the estimate is unavailable. This is an estimate, not a charge: it excludes tool fees, special modalities, long-context and priority processing, and exchange-rate changes beyond the Gate's reference rate.

Standard text-token reference prices in USD per million tokens, for prompts up to 272K input tokens: GPT-6 Luna, input $0.10, cached input $0.01, output $0.50; GPT-6 Sol, $2, $0.20, and $10; GPT-6 Astra, $10, $1, and $50. Legacy GPT-5.6 Terra remains available for manual selection and retains the rates configured in the Gate: input $2, cached input $0.20, and output $12. Prices can change; see the [official OpenAI pricing table](https://developers.openai.com/api/docs/pricing).

## Skills

Leave automatic selection enabled for the Gate to choose skills related to the task. To choose them yourself, enable **Use manual selection** and search using part of a skill's name; you do not need to type the complete name. Skills shown under **Skills recommended for this task** are the ones that will be used for that task. Removing one from the task does not delete it from the library.

For automatic selection, the Gate uses explicit rules to recognize the requested action and result and checks which skills for that purpose are available in the library. It may choose more than one when each covers a concrete part of the result. There is no extra Codex semantic-analysis call or score based on similar words in skill names. A question about today's dollar exchange rate or an election date uses reliable-source research; changing a corporate card uses the dedicated business-card skill; finding scientific papers uses reference search and, when useful, a subject specialist such as nanofluids. If the result cannot be recognized confidently, no domain skill is suggested; use manual selection to choose one. The built-in orchestration skill organizes the chosen skills during execution.

Questions about election poll results, such as first and second round presidential polls, also call for reliable sources. Here “research” or “polls” does not mean scientific research; nanofluid and other laboratory skills are not selected.

When you install a skill manually or through a skill-creation task, the Gate updates its memory immediately. It appears in the library; automatic selection requires its purpose to match a recognized result route. Otherwise, choose it manually. If two versions have the same name, the most recently installed version is used in the catalog.

A skill author can declare its purposes in the optional `gate_outcomes` field of `SKILL.md`, using the route codes documented in the project guide. This lets a new skill join an existing route without comparing similar words.

When using **Schedule task...**, enter the local date and time as `YYYY-MM-DD HH:MM`. The Gate requests your confirmation at the scheduled time.

## Previous tasks and files

In **Previous tasks**, use **Search tasks** to locate an execution by request, topic, response, or file name. Search updates as you type, ignores capitalization and accents, and is also available with `Ctrl+F`. Use the additional filters to restrict results by date, model, status, or skill. Select a task and open **Files** to see only its files. Displayed dates and the date filter use the interface format and local time; the record file keeps its original timestamps for auditing.

The area to the right of search shows only the number of displayed records. Review token and cost totals in **Usage**.

Tasks run by this version preserve the Codex session. Select one and use **Continue conversation** to request adjustments, review the delivery, or continue the analysis in the same session and folder. In **Previous tasks**, all four filters share one row. The action bar shows **Refresh records**, **Continue conversation**, and **Rate record**. **List** contains unrated records and the report; **Open / export** contains text view, TXT/PDF export, and the records folder; **.gate packages** contains task export and import. Every function remains available. The bar stays on one row and scrolls horizontally when needed. The task list and **Selected record details** divide the available height equally. Each new message is added to the task record. Older records without a session identifier remain readable, but cannot retroactively restore context that was not saved.

## Usage

Open **Usage** to review estimated costs and aggregated tokens for today, the last seven days, this month, this year, or all time. Select **Custom** to enter a start and end date in `YYYY-MM-DD` format. Filter by all models or Luna, Terra, Sol, and Astra. The table identifies the model and shows tasks, input, cache, output, reasoning, and cost by hour, day, or month depending on the selected period. English displays dates as `YYYY-MM-DD`, uses commas for thousands, and uses a decimal point for monetary values. Choose the interface-language currency automatically or select USD, BRL, or EUR. Use **Export CSV...** to save the displayed rows for a spreadsheet.

In the **Breakdown** table, headers and values are centered within each column, including model, tokens, and estimated cost.

The notice beside the summary explains that the total is an estimate, not an account charge. The dashboard aggregates local records with token usage and an identifiable model; it shows how many records fall in the period, how many are included, and how many are excluded for missing data. Costs use the prices and reference exchange rate configured in the Gate, have two decimal places, and can be recalculated with current rates: records store the model and tokens, not an invoice or the price in effect when the task ran.

## Links in responses

Page addresses shown in a response appear as blue, underlined hyperlinks. Select one to open it in the default Windows browser. The Gate recognizes both plain URLs and titled Markdown links, and only opens valid `http` or `https` addresses.

## Controlled web research

For public dates, election polls, or tasks using the reliable sources skill, the Gate enables Codex live web search. The task starts directly in Codex, which can consult current sources and cite their links. Check dates and figures against the original source before relying on them.

Technical mechanism explanations also enable live web search. For every task, the Gate instructs Codex to open each cited page, confirm that it directly supports the claim, and use a specific section when possible. This rule applies automatically. Verification depends on access to the page during execution; if access fails, Codex should state the limitation instead of inventing a citation.

Select **Allow Gate visual browser (Edge)** to make a visible, isolated browser available to Codex. Checking the box does not start a search: the task starts in Codex, and Edge opens only if Codex chooses the browser tool. The session does not automatically reuse your personal logins or history. Without the box checked, **Edge search terms (optional)** is disabled and has no effect on the task.

This field accepts **search words**, for example `Mexico election calendar 2027`. They are a suggestion, not a command: Codex may use different terms or may not use Edge. If left blank, the task description is sent as the suggested query. When used, the visual browser searches Google and Bing and can open a page only if it appears among the search results. Pasting `https://example.com/article` into this field searches for that URL as text; it **does not open the page directly**. To request analysis of a specific link, put it in the main task description, for example `Read and summarize https://example.com/article`. Codex can try to access the page with the available tools and should say if it cannot. Bounded questions about election or sports competition dates receive Luna — Low and live web search; requests for comparison or analysis are rated by the complexity of the result.

When enabled, the Gate offers its visual browser to Codex through local MCP tools. Codex live web search works independently of this option.

## Response screen

When a task finishes, the Gate automatically opens **Response**, including in simple mode. The technical panel remains limited to advanced options, but you never need to enable it merely to read the final response.

## Backup and data

Use **Create backup...** in the Task tab to save projects, skills, records, and settings in a ZIP file. New backups use a compact internal structure to avoid Windows long-path errors. The `backup-manifest.json` file inside the ZIP maps each item to its original path.

### Full ZIP backup and `.gate` task package

The **full ZIP backup** and the **`.gate` package** serve different purposes. The ZIP created with **Create backup...** contains Gate data: projects, the skill library, records, and settings. Use it for a general backup or to migrate these data to another computer. To restore it, select **Restore backup...**, choose the ZIP, and review the file and category preview. Choose **Yes** to replace files that match the backup; **No** to preserve current files and restore items under alternate names; **Cancel** to stop. Files outside the backup are never removed. Restoring settings from another computer may require restarting the Gate.

The **`.gate` package** contains only one selected task: its record and files in its task folder, such as attachments and outputs. It does not include the full library, settings, or other projects and records. In **Previous tasks**, select the task and choose **Export task as package...**. On the other installation, choose **Import `.gate` package...**. The Gate restores the files in a dedicated folder and creates a local record. Then analyze the imported task to start a new conversation with that context. The package does not transfer the authenticated session or original conversation identifier, so it cannot resume the previous session. It can also serve as an isolated portable copy of one task.

To migrate to another computer, install and open the Gate, then select **Restore backup...**. Choose the ZIP copied from the previous computer. If the new computer has no data, choose **Yes** to restore normally. If it already contains data you want to preserve, choose **No**: the Gate keeps current files and adds restored files with a restoration suffix.

Application data is stored in a dedicated Gate folder. **Open Gate data** displays that folder in File Explorer. Normal application updates preserve this data.

## Codex CLI

The Gate needs Codex CLI installed and authenticated to run tasks. The **Codex CLI** area shows its status and provides installation instructions. The Gate looks for the executable both on PATH and in the Windows Codex app installation. You can still analyze and organize a task without the CLI, but you cannot run it. **Decision ready** means analysis is complete and execution still needs approval; it does not mean the model has answered. After **2. Confirm and run**, watch for **Codex started** and open **Response** when it finishes. If the CLI cannot be found, the task does not start and the screen explains why.

If preparation or the interface fails, the Gate shows an error instead of leaving the task waiting indefinitely. For diagnosis, open the task folder and read `.codex-model-gate/startup-status.txt`; interface errors are also recorded in `gui-error.txt`. Creating a folder or confirming approval alone does not prove that Codex started.

Version 2.6.5 corrects the start and duration clock. After approving a new task or continuing a conversation, look for **Codex started** before treating the process as started.

The Codex app model picker and Codex CLI may be on different versions. GPT-6 Sol and Luna entered the CLI model catalog in version 0.156.1. If Gate finds an older CLI, it displays the version and prevents starting a Sol or Luna task until it is updated. Select **Update Codex CLI...** to open the official installer in PowerShell, then select **Check again**. A CLI rejection does not prove that the model is unavailable in your account; Gate keeps its original recommendation. If an updated CLI still rejects a model, check authentication, availability in that client, and the error message. Gate records the failure and never changes your approved model automatically.

## Language

Use **Language** at the top of the Task tab. The choice is saved in Gate settings, included in backups, and stored on the drive in the portable edition. Changing the language restarts the application to load the complete interface consistently. The interface language does not automatically change the language of your task or Codex response.

## Tips

- State a clear desired result, for example: “create a PDF report with these sections.”
- Review attachments, skills, and destination folder before approval.
- If Codex asks a question, use **Answer pending question** to keep the same task and context.
- The Gate does not delete files produced when an execution is cancelled; open the task folder to review what was already created.
"""

MANUALS["es"] = """# Manual de Codex Model Gate

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

**Bajo** es para solicitudes rápidas; **Medio** equilibra planificación y velocidad; **Alto** y **Extra alto** sirven para trabajos difíciles con varias etapas, fuentes o decisiones. **Máximo** no se recomienda automáticamente. **Ultra** no está disponible para la familia GPT-6 y no se recomienda automáticamente: elija un nivel compatible con el modelo seleccionado.

### Agilidad de la interfaz

Al concluir una tarea, el Gate abre la respuesta antes de actualizar los archivos y el historial. El panel de consumo reutiliza los registros ya cargados, y la estimación de duración usa los mismos datos. La versión del Codex CLI comprobada en la sesión se reutiliza al autorizar, y los mensajes de progreso se agrupan para mantener la ventana ágil. Estas mejoras reducen las esperas de la interfaz; el tiempo de generación del modelo depende de la tarea, el nivel elegido y Codex CLI.

### Consumo y costo estimado

En conversaciones con varias respuestas, el registro muestra el tiempo y los tokens de cada ejecución por separado. La pestaña **Consumo** suma los tokens informados por esas ejecuciones. Los registros antiguos sin este desglose conservan el total disponible.

Después de la ejecución, el Gate muestra los tokens de entrada, entrada en caché, salida y razonamiento informados por Codex CLI, además del costo estimado para el modelo seleccionado. El importe se presenta con dos decimales y en la moneda asociada al idioma de la interfaz. Si el CLI no informa el uso, la estimación no está disponible. Es una estimación, no un cargo: no incluye tarifas de herramientas, modalidades especiales, contexto largo, procesamiento prioritario ni cambios de divisa más allá de la tasa de referencia del Gate.

Precios de referencia estándar para tokens de texto en USD por millón, para solicitudes de hasta 272 mil tokens de entrada: GPT-6 Luna, entrada US$ 0,10, caché US$ 0,01 y salida US$ 0,50; GPT-6 Sol, US$ 2, US$ 0,20 y US$ 10; GPT-6 Astra, US$ 10, US$ 1 y US$ 50. El modelo heredado GPT-5.6 Terra sigue disponible para selección manual y conserva las tarifas configuradas en el Gate: entrada US$ 2, caché US$ 0,20 y salida US$ 12. Los precios pueden cambiar; consulte la [tabla oficial de precios de OpenAI](https://developers.openai.com/api/docs/pricing).

## Skills

Mantenga activada la selección automática para que el Gate elija las skills relacionadas con la tarea. Para elegirlas usted mismo, active **Usar selección manual** y busque por una parte del nombre; no es necesario escribirlo completo. Las skills mostradas en **Skills recomendadas para esta tarea** son las que se usarán en esa tarea. Quitar una de la tarea no la elimina de la biblioteca.

En la selección automática, el Gate usa reglas explícitas para reconocer la acción y el resultado solicitados y consulta qué skills para esa finalidad están disponibles en la biblioteca. Puede elegir varias cuando cada una cubre una parte concreta del resultado. No hay una llamada adicional de análisis semántico a Codex ni una puntuación por palabras parecidas en los nombres de las skills. Una consulta sobre la cotización actual del dólar o la fecha de unas elecciones usa investigación en fuentes fiables; modificar una tarjeta corporativa usa la skill específica de tarjetas; buscar artículos científicos usa búsqueda de referencias y, cuando sea útil, una especialidad temática como nanofluidos. Si el resultado no se reconoce con seguridad, no se sugiere ninguna skill de dominio; use la selección manual para elegir una. La skill interna de orquestación organiza las skills elegidas durante la ejecución.

Las preguntas sobre resultados de encuestas electorales, como las presidenciales de primera y segunda vuelta, también requieren fuentes fiables. En ese contexto, “investigación” o “encuestas” no significa investigación científica; no se eligen skills de nanofluidos ni de otros temas de laboratorio.

Al instalar una skill manualmente o mediante una tarea de creación, el Gate actualiza su memoria de inmediato. Aparece en la biblioteca; para la selección automática, su finalidad debe corresponder a una ruta de resultado reconocida. En los demás casos, elíjala manualmente. Si hay dos versiones con el mismo nombre, se usa en el catálogo la instalada más recientemente.

Quien crea una skill puede declarar sus finalidades en el campo opcional `gate_outcomes` de `SKILL.md`, usando los códigos de ruta documentados en la guía del proyecto. Así, una skill nueva puede incorporarse a una ruta existente sin comparar palabras parecidas.

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

El selector de modelos de la aplicación Codex y Codex CLI pueden tener versiones diferentes. GPT-6 Sol y Luna entraron en el catálogo de CLI 0.156.1. Si Gate encuentra un CLI anterior, muestra la versión e impide iniciar una tarea con Sol o Luna hasta actualizarlo. Seleccione **Actualizar Codex CLI...** para abrir el instalador oficial en PowerShell y después seleccione **Comprobar de nuevo**. Un rechazo del CLI no demuestra que el modelo no esté disponible en su cuenta; Gate conserva su recomendación original. Si un CLI actualizado todavía rechaza un modelo, compruebe la autenticación, la disponibilidad en ese cliente y el mensaje de error. Gate registra el fallo y nunca cambia automáticamente el modelo autorizado.

## Idioma

Use **Idioma** en la parte superior de la pestaña Tarea. La elección se guarda en la configuración del Gate, se incluye en las copias y permanece en la unidad de la edición portátil. El cambio de idioma reinicia el programa para cargar la interfaz completa de forma coherente. El idioma de la interfaz no cambia automáticamente el idioma de la tarea o de la respuesta de Codex.

## Consejos

- Indique un resultado deseado claro, por ejemplo: “cree un informe PDF con estas secciones”.
- Revise los adjuntos, las skills y la carpeta de destino antes de autorizar.
- Si Codex hace una pregunta, use **Responder pregunta pendiente** para mantener la misma tarea y el mismo contexto.
- El Gate no elimina los archivos producidos al cancelar una ejecución; abra la carpeta de la tarea para revisar lo que ya se creó.
"""


def normalize_language(value: str | None) -> str:
    value = (value or "").replace("_", "-").lower()
    if value.startswith("pt"):
        return "pt-BR"
    if value.startswith("es"):
        return "es"
    if value.startswith("en"):
        return "en"
    return "pt-BR"


def system_language() -> str:
    try:
        return normalize_language(locale.getlocale()[0])
    except (ValueError, TypeError):
        return "pt-BR"


def translate(text: str, language: str) -> str:
    language = normalize_language(language)
    pack = PACKS.get(language, {})
    if language == "pt-BR" or not text:
        return text
    if text in pack:
        return pack[text]

    patterns = {
        "en": (
            (r"^Codex CLI (\d+\.\d+\.\d+) encontrado\. Atualize para 0\.156\.1 ou posterior para usar GPT-6 Sol e Luna\.$", r"Codex CLI \1 found. Update to 0.156.1 or later to use GPT-6 Sol and Luna."),
            (r"^Codex CLI (\d+\.\d+\.\d+) é anterior ao suporte a GPT-6 Sol e Luna\. Atualize o Codex CLI para 0\.156\.1 ou posterior e clique em Verificar novamente antes de executar\.$", r"Codex CLI \1 predates support for GPT-6 Sol and Luna. Update Codex CLI to 0.156.1 or later and click Check again before running."),
            (r"^Codex CLI disponível \((.+)\)\. Se esta for a primeira utilização, execute uma tarefa para concluir a autenticação da sua conta\.$", r"Codex CLI available (\1). If this is your first use, run a task to finish authenticating your account."),
            (r"^Memória pronta: (\d+) indexada\(s\), (\d+) nova\(s\)/alterada\(s\), (\d+) reutilizada\(s\) e (\d+) removida\(s\)\. Vincule outra biblioteca se quiser ampliar o catálogo\.$", r"Skill memory ready: \1 indexed, \2 new/updated, \3 reused, and \4 removed. Link another library to expand the catalog."),
            (r"^(\d+) de (\d+) registro\(s\) exibido\(s\)$", r"\1 of \2 record(s) shown"),
            (r"^(\d+) skill\(s\) disponíveis$", r"\1 skill(s) available"),
            (r"^Registros sem avaliação \((\d+)\)$", r"Unrated records (\1)"),
            (r"^Tempo decorrido: (.+)$", r"Elapsed time: \1"),
            (r"^Tempo restante estimado: (.+)$", r"Estimated time remaining: \1"),
            (r"^Tempo restante: (.+)$", r"Remaining time: \1"),
            (r"^Resultado registrado: (.+)\.$", r"Result recorded: \1."),
            (r"^Registro exportado: (.+)$", r"Record exported: \1"),
        ),
        "es": (
            (r"^Codex CLI (\d+\.\d+\.\d+) encontrado\. Atualize para 0\.156\.1 ou posterior para usar GPT-6 Sol e Luna\.$", r"Se encontró Codex CLI \1. Actualice a 0.156.1 o posterior para usar GPT-6 Sol y Luna."),
            (r"^Codex CLI (\d+\.\d+\.\d+) é anterior ao suporte a GPT-6 Sol e Luna\. Atualize o Codex CLI para 0\.156\.1 ou posterior e clique em Verificar novamente antes de executar\.$", r"Codex CLI \1 es anterior a la compatibilidad con GPT-6 Sol y Luna. Actualice Codex CLI a 0.156.1 o posterior y pulse Comprobar de nuevo antes de ejecutar."),
            (r"^Codex CLI disponível \((.+)\)\. Se esta for a primeira utilização, execute uma tarefa para concluir a autenticação da sua conta\.$", r"Codex CLI disponible (\1). Si es su primer uso, ejecute una tarea para completar la autenticación de su cuenta."),
            (r"^Memória pronta: (\d+) indexada\(s\), (\d+) nova\(s\)/alterada\(s\), (\d+) reutilizada\(s\) e (\d+) removida\(s\)\. Vincule outra biblioteca se quiser ampliar o catálogo\.$", r"Memoria de skills lista: \1 indexadas, \2 nuevas/actualizadas, \3 reutilizadas y \4 eliminadas. Vincule otra biblioteca para ampliar el catálogo."),
            (r"^(\d+) de (\d+) registro\(s\) exibido\(s\)$", r"\1 de \2 registro(s) mostrados"),
            (r"^(\d+) skill\(s\) disponíveis$", r"\1 skill(s) disponibles"),
            (r"^Registros sem avaliação \((\d+)\)$", r"Registros sin evaluar (\1)"),
            (r"^Tempo decorrido: (.+)$", r"Tiempo transcurrido: \1"),
            (r"^Tempo restante estimado: (.+)$", r"Tiempo restante estimado: \1"),
            (r"^Tempo restante: (.+)$", r"Tiempo restante: \1"),
            (r"^Resultado registrado: (.+)\.$", r"Resultado registrado: \1."),
            (r"^Registro exportado: (.+)$", r"Registro exportado: \1"),
        ),
    }
    for pattern, replacement in patterns.get(language, ()):
        if re.match(pattern, text):
            return re.sub(pattern, replacement, text)

    # Dynamic messages often add a path, count, model, or exception to a known
    # sentence. Translate the stable phrases while preserving those values.
    result = text
    for source in sorted(pack, key=len, reverse=True):
        if len(source) >= 8 and source in result:
            result = result.replace(source, pack[source])
    return result


def manual(default_text: str, language: str) -> str:
    return MANUALS.get(normalize_language(language), default_text)


def source_text(translated: str, language: str) -> str:
    """Return the Portuguese source key used by internal domain logic."""
    pack = PACKS.get(normalize_language(language), {})
    return next((source for source, target in pack.items() if target == translated), translated)
