"""Small, dependency-free language packs for the Codex Model Gate UI."""
from __future__ import annotations

import locale
from gate_manuals import MANUALS
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

EN.update({
    'Download / atualização oficial': 'Official download / update',
    'Consultar novas versões': 'Check for new releases',
    'Verificando versão do Codex CLI...': 'Checking the Codex CLI version...',
    'Consultando changelog oficial...': 'Checking the official changelog...',
    'Consulta indisponível. Use Download / atualização oficial para conferir as versões.': 'Update check unavailable. Use Official download / update to check releases.',
    'Copiar resposta': 'Copy response', 'Exportar resposta...': 'Export response...',
    'Abrir pasta da tarefa': 'Open task folder', 'Diagnósticos': 'Diagnostics',
    'Recalcular com tarifas e câmbio atuais': 'Recalculate with current prices and exchange rates',
    'Sol 6 (anterior)': 'Sol 6 (previous)', 'Preparando tarefa': 'Preparing task',
    'Salvando registro': 'Saving record', 'Falha ao salvar registro': 'Record save failed',
    'Abrir até 3 arquivos após validação': 'Open up to 3 files after validation',
    'Diagnóstico': 'Diagnostics',
    'Aguarde a atividade terminar antes de alterar o idioma.': 'Wait for the current activity to finish before changing language.',
    'Verificando a versão do CLI. Aguarde o resultado antes de executar.': 'Checking the CLI version. Wait for the result before running.',
    'A tarefa ou os anexos mudaram. Analise novamente.': 'The task or attachments changed. Analyze again.',
    'ESTIMATIVA — Não é uma cobrança da sua conta. Usa tokens registrados e tarifas/câmbio salvos em cada turno. Registros antigos usam referências atuais; recalcular é opcional.': 'ESTIMATE — This is not an account charge. It uses recorded tokens and prices/exchange rates saved per turn. Older records use current references; recalculation is optional.',
})
ES.update({
    'Download / atualização oficial': 'Descarga / actualización oficial',
    'Consultar novas versões': 'Consultar nuevas versiones',
    'Verificando versão do Codex CLI...': 'Comprobando la versión del Codex CLI...',
    'Consultando changelog oficial...': 'Consultando el changelog oficial...',
    'Consulta indisponível. Use Download / atualização oficial para conferir as versões.': 'Consulta no disponible. Use Descarga / actualización oficial para comprobar las versiones.',
    'Copiar resposta': 'Copiar respuesta', 'Exportar resposta...': 'Exportar respuesta...',
    'Abrir pasta da tarefa': 'Abrir carpeta de la tarea', 'Diagnósticos': 'Diagnósticos',
    'Recalcular com tarifas e câmbio atuais': 'Recalcular con tarifas y cambio actuales',
    'Sol 6 (anterior)': 'Sol 6 (anterior)', 'Preparando tarefa': 'Preparando tarea',
    'Salvando registro': 'Guardando registro', 'Falha ao salvar registro': 'Error al guardar el registro',
    'Abrir até 3 arquivos após validação': 'Abrir hasta 3 archivos tras validación',
    'Diagnóstico': 'Diagnóstico',
    'Aguarde a atividade terminar antes de alterar o idioma.': 'Espere a que termine la actividad antes de cambiar el idioma.',
    'Verificando a versão do CLI. Aguarde o resultado antes de executar.': 'Comprobando la versión del CLI. Espere el resultado antes de ejecutar.',
    'A tarefa ou os anexos mudaram. Analise novamente.': 'La tarea o los adjuntos cambiaron. Analice de nuevo.',
    'ESTIMATIVA — Não é uma cobrança da sua conta. Usa tokens registrados e tarifas/câmbio salvos em cada turno. Registros antigos usam referências atuais; recalcular é opcional.': 'ESTIMACIÓN — No es un cobro de su cuenta. Utiliza tokens registrados y tarifas/cambio guardados por turno. Los registros antiguos usan referencias actuales; recalcular es opcional.',
})
PACKS = {"pt-BR": {}, "en": EN, "es": ES}


# Complete manuals: these intentionally mirror every section in the Portuguese
# guide instead of offering a shortened foreign-language quick start.



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
