# Análise do Codex Model Gate — 01/10/2026

## Conclusão

O projeto tem uma proposta consistente: preparar, recomendar, autorizar, executar e registrar tarefas do Codex CLI no Windows. A próxima evolução deve começar pela integridade dos dados e pela coerência entre o que a interface apresenta e o que é executado. Uma reorganização visual ajuda bastante, mas não resolve sozinha os problemas de migração, estado e persistência identificados.

A análise não modificou o programa nem gerou instaladores. A versão analisada declara 2.6.20.

## Escopo e método

Foram inventariados e lidos por ferramenta 219 arquivos textuais fora de dependências e saídas de compilação, incluindo 31 SKILL.md e 23 registros locais; 12 arquivos Python foram analisados sintaticamente. A revisão funcional se concentrou nos quatro módulos principais, testes, scripts de empacotamento, documentação e memórias de evolução. Skills e registros são conteúdo de entrada e histórico, não componentes equivalentes ao código do aplicativo.

Executáveis, ICOs, caches, ferramentas baixadas e objetos de build foram identificados como artefatos, sem decompilação. A leitura mecânica de todos os textos não equivale a uma auditoria especializada de cada skill científica. Não houve inspeção visual de uma janela em execução, teste de instalação, chamada real ao Codex ou pesquisa na internet. As propostas de interface derivam da construção dos widgets e precisam de conferência visual em diferentes escalas do Windows.

Validação: `python -m unittest discover -s tests -v` passou com **58 testes** em Python 3.14.6. Foram realizadas verificações adicionais com dados temporários e mocks, sem chamadas ao Codex, instalações ou alteração dos dados reais do usuário. Os resultados abaixo distinguem reprodução, inspeção estática e recomendação.

## Como funciona

1. `GateApp` inicializa preferências, idioma, catálogo de skills, histórico, estado de continuação e verificação do CLI.
2. `recommend()` combina o pedido com os tipos dos anexos, seleciona skills por regras explícitas e chama `assess_task()` para recomendar modelo e raciocínio. Essa análise não chama um modelo para compreender o conteúdo dos documentos: `attachment_context()` acrescenta essencialmente o tipo dos arquivos.
3. `apply_recommendation()` cria um dicionário `pending` com a decisão. O usuário pode ajustar opções antes de autorizar.
4. `authorize_run()` confirma a tarefa, cria uma pasta exclusiva, copia anexos para `.codex-model-gate/anexos`, carrega instruções e monta o comando.
5. Uma thread inicia `codex exec` ou `codex exec resume`; o prompt vai por stdin. Threads leem stdout e stderr; uma fila leva eventos à interface Tkinter.
6. `finish_run()` apresenta a resposta, procura arquivos alterados, extrai uso de tokens, valida documentos, instala skills geradas e grava histórico.
7. A continuação usa uma sessão identificada e estado salvo. Agendamentos são locais, verificados com o aplicativo aberto, e pedem confirmação.

### Componentes

| Componente | Papel | Observação |
|---|---|---|
| `codex_model_gate_gui.py` | Tkinter, abas, interação, execução e pós-processamento | 4.286 linhas; concentra responsabilidades demais em `GateApp` |
| `codex_model_gate.py` | Regras, prompts, skills, armazenamento, pacotes, validação e CLI | 3.133 linhas; biblioteca de domínio e serviços misturadas |
| `gate_i18n.py` | Traduções, transformação de textos e manuais | 659 linhas, algumas muito extensas |
| `gate_browser_mcp.py` | Servidor MCP STDIO para Edge isolado | 183 linhas |
| `tests/test_gate.py` | 58 testes existentes | Boa base funcional; faltam cenários de estado, migração e interface |
| `build_windows.ps1`, `.iss`, `.spec`, workflow | Distribuição Windows | Há mais de uma receita de build |
| `Skills-Codex`, `registro`, `.codex-model-gate` | Biblioteca e dados locais históricos | Não representam necessariamente os dados atuais em LocalAppData |
| `Release`, `dist`, `Output`, `build` | Entregas e artefatos de compilação | Deve ficar inequívoco qual é a distribuição vigente |

A edição instalada usa LocalAppData; a portátil detecta a ausência de `installed.marker`, guarda dados junto ao EXE e prepara um CODEX_HOME próprio. O Gate é um cliente do CLI: não controla o modelo de outros chats do aplicativo Codex. Suas políticas e recomendações complementam as opções do CLI; não constituem uma validação independente de tudo que o modelo faz.

## Falhas e inconsistências prioritárias

### 1. Pacotes .gate perdem anexos e mantêm caminhos da instalação original — alta

**Evidência:** `codex_model_gate.py:1153–1214`, especialmente a exclusão de qualquer arquivo cujo caminho contenha `.codex-model-gate` e a atualização de apenas alguns campos do registro importado. **Reproduzido.**

Os anexos ficam justamente dentro da pasta excluída. No teste de exportação/importação, o pacote continha o resultado, mas não `input.txt`, que era um anexo da tarefa. Além disso, `artifacts` continuava apontando para o workspace antigo, fora da pasta importada. Enquanto o original existe, isso pode parecer funcionar e abrir o arquivo errado; em outro computador, o caminho tende a não existir.

**Melhoria:** exportar anexos ativos e seus metadados; excluir apenas estado interno não transferível. Armazenar caminhos relativos ao workspace no pacote e reconstruir `artifacts`, anexos e referências locais na importação. Limpar dados de sessão não transferíveis e validar a tarefa importada antes de exibi-la como disponível.

**Verificação necessária:** exportar, remover o acesso ao workspace original e importar em outro diretório. Todos os arquivos exibidos devem pertencer à nova pasta.

### 2. Backup geral não cobre projetos externos e restauração não remapeia registros — alta

**Evidência:** `codex_model_gate.py:742–805`, `882–922`; escolha de pasta em `codex_model_gate_gui.py:2552` e `2678`. **Omissão de projeto externo e registro invisível reproduzidos; remapeamento avaliado por inspeção.**

O backup percorre somente `app_data_dir()/projetos`, `skills`, `registro` e `settings.json`. A edição instalada permite uma raiz externa de projetos; os resultados nessa raiz ficam fora da cópia geral. O teste confirmou que um resultado no projeto externo não entrou no manifesto.

Ao restaurar em outro computador ou com nomes `-restaurado-N`, os registros continuam carregando caminhos absolutos antigos. A cópia dos bytes não basta para restabelecer a navegação e a continuação. Não se deve prometer transferir sessões apenas por copiar registros.

Na restauração sem substituir, um registro existente `arquivo.md` recebe o nome `arquivo.md-restaurado-1`. Como o histórico procura `*.md`, essa cópia restaurada fica invisível. A reprodução deixou dois arquivos na pasta e apenas um registro visível. O sufixo deve entrar antes da extensão, com identificador próprio para distinguir a cópia.

**Melhoria:** prévia explícita da cobertura do backup, cadastro das raízes gerenciadas e mapa de origem/destino aplicado aos registros. Manter exclusão de credenciais como decisão expressa de produto. O backup atual também não inclui `history.json`, o índice global de continuação ou CODEX_HOME; documentar claramente esses limites.

### 3. Alteração de idioma permite reiniciar durante a execução — alta

**Evidência:** `codex_model_gate_gui.py:1414–1437` e `4254–4273`. **Reproduzido com mocks, sem processo real.**

`change_language()` inicia outra instância e destrói a atual sem verificar `running` ou `selecting_skills`. `language_box` não está entre os controles desabilitados. Isso contorna a proteção de `on_close()`, pode perder rascunhos e interromper o acompanhamento e a gravação do resultado; não foi confirmado o destino de um subprocesso real nesse cenário.

**Melhoria:** bloquear reinício durante atividade, ou aplicar a preferência ao terminar. Persistir rascunho, anexos e seleção antes de reiniciar. Centralizar todas as saídas e reinícios num mesmo ciclo de encerramento.

### 4. Pasta e política exibidas podem divergir da decisão executada — alta

**Evidência:** `codex_model_gate_gui.py:2678`, `3405`, `3431`, `3497`, `3508–3592`. **Inspeção estática; ausência de sincronização em recommend também verificada com mock.**

Digitar uma nova pasta altera `path_var`, mas `projects_root` é atualizado em `refresh_skills()`. A execução cria o workspace usando `projects_root`; o checklist mostra `path_var`. O agendamento também altera o campo antes de chamar `recommend()` sem atualizar a raiz. A divergência ocorre quando o campo é editado diretamente ou o agendamento usa uma raiz diferente, sem atualização de skills.

A política é copiada para `pending` na análise. Mudar o combobox depois não atualiza essa política; a confirmação reforçada usa o valor antigo. O problema não é a escolha pelo diálogo de pasta, que chama a atualização.

**Melhoria:** construir uma configuração única, validada e imutável no momento da autorização. Mostrar o caminho absoluto efetivo no diálogo. Qualquer alteração relevante deve atualizar a decisão ou exigir nova análise, com justificativa visível. Validar também as restrições de caminho da edição portátil nesse ponto.

### 5. Gravações diretas e erros silenciosos fragilizam a recuperação — alta

**Evidência:** `codex_model_gate.py:1055`, `1072`, `1639–1653`; `codex_model_gate_gui.py:1890–1909`, `4017`. **Inspeção estática.**

Configurações, histórico e registros são escritos diretamente no arquivo final. Uma interrupção pode produzir JSON ou Markdown incompleto. `update_execution_record()` captura erros e retorna sem informar se salvou. Há dois históricos com esquemas diferentes, além do JSON embutido no Markdown; `add_history()` ainda pode trocar o identificador inicial da tarefa.

**Melhoria:** gravação em arquivo temporário único seguida de substituição atômica; retorno explícito ou exceção de falha; um repositório de registros como fonte de verdade. Manter um backup anterior recuperável e validar esquemas/versionamento. Considerar SQLite quando paginação e concorrência realmente exigirem, sem começar por uma migração grande.

### 6. Consumo perde cache aninhado e agrupa conversas pela data final — média

**Evidência:** `codex_model_gate.py:1571–1592`; `codex_model_gate_gui.py:1166–1211`, `4037–4083`. **Cache reproduzido; agrupamento por inspeção.**

Um evento com `usage.input_tokens_details.cached_tokens=50` retornou `cached_input=0`. A comparação de caminhos completos não reconhece o prefixo `usage`. A soma recursiva também precisa distinguir totais cumulativos de métricas por evento para evitar contagem duplicada em formatos que emitam ambos.

O registro guarda `turn_metrics`, mas o painel percorre `token_usage` agregado e `finished_at`; não usa a data de cada resposta. Uma conversa iniciada ontem e continuada hoje pode ter todo seu consumo atribuído à data final do registro, contrariando a explicação de métricas por execução.

**Melhoria:** parser por tipos de evento e variantes conhecidas, preservando origem e campos ausentes. Agregar cada turno por sua data e manter fallback documentado para registros antigos. Preservar a tarifa/câmbio usados quando se desejar comparação histórica estável; permitir recalcular como opção explícita.

### 7. Validador acusa caracteres portugueses legítimos — média

**Evidência:** `codex_model_gate.py:2584–2595`. **Reproduzido.**

A presença isolada de `Ã` ou `Â` é tratada como possível corrupção. `CONCLUSÃO E REFERÊNCIAS` foi marcada como suspeita. Isso gera revisão necessária para um documento válido.

**Melhoria:** detectar sequências típicas de mojibake, considerar contexto e distinguir aviso de bloqueio. Acrescentar exemplos legítimos e corrompidos aos testes. As validações atuais de PDF/DOCX verificam aspectos delimitados de texto e limites; não comprovam qualidade visual integral nem validade científica.

### 8. Seletor de raciocínio e resumo não acompanham as escolhas — média

**Evidência:** `codex_model_gate_gui.py:748–750`, `1336`, `2068–2085`, `3528–3535`. **Inspeção estática.**

O seletor oferece todos os valores de `EFFORT_LABELS`, inclusive Ultra, sem uma matriz de compatibilidade por modelo. O próprio manual diz que Ultra não é oferecido pela família GPT-6. Os cartões permanecem com o valor recomendado mesmo quando o usuário muda a escolha; falta um resumo explícito de configuração efetiva.

**Melhoria:** separar “recomendado” de “selecionado”, sincronizar modelo/raciocínio/política/skills e validar a combinação antes de preparar arquivos. Não inferir suporte só pela presença de uma string no catálogo local.

### 9. Operações pesadas permanecem na thread da interface — média

**Evidência:** `codex_model_gate_gui.py:2493`, `2572–2644`, `2678`, `3550–3623`, `3846–4015`. **Inspeção estática.**

A execução do CLI está em segundo plano, o que é positivo. Entretanto, versão do CLI, cópia de anexos, backups, indexação, varredura de arquivos e validação de documentos ainda podem bloquear callbacks Tkinter. `after()` agenda o callback na thread da interface; não o transforma em operação de fundo. Abrir automaticamente todos os PNG/JPG/PDF em `finish_run()` também pode causar muitas janelas, inclusive antes de tratar falha/validação.

**Melhoria:** jobs para I/O e validação, devolvendo resultados pela fila existente. Exibir etapas reais de preparação e opção de cancelar. Tornar abertura automática uma preferência, desligada por padrão, após validação e com limite de arquivos.

### 10. Cancelamento encerra apenas o processo imediato — média

**Evidência:** `codex_model_gate_gui.py:3782–3799`. **Inspeção estática; árvore de processos não testada.**

`terminate()` não implementa gerenciamento de todos os descendentes que o CLI possa iniciar, como ferramentas e MCP. A interface não permite fechar enquanto há execução, mas o reinício por idioma segue outra regra.

**Melhoria:** encapsular ciclo de vida em um supervisor, com cancelamento cooperativo quando disponível, prazo para encerramento e tratamento da árvore de processos no Windows. Usar um mecanismo compatível com a plataforma, como Job Objects, após validar o comportamento com o CLI utilizado.

## Melhorias de interface

A identidade existente, as seis abas e os recursos podem ser preservados. Não há evidência de que uma migração imediata de Tkinter seja necessária.

1. **Localização:** aba Tarefa e modo simples. **Ação principal:** colocar descrição, anexos, decisão e executar no primeiro bloco visível; mover backup, biblioteca e manutenção para Configurações ou painel recolhível. **Referência base:** editor do pedido e ações principais. **Integridade:** preservar funções e a opção de acesso avançado. Hoje `apply_ui_mode()` esconde apenas controles do CLI, linha técnica de decisão e log; a biblioteca detalhada continua visível.
2. **Localização:** barra de ações da tarefa. **Ação principal:** manter as ações principais acessíveis durante a rolagem; separar analisar/executar das ações de agendamento, resposta pendente e cancelar. **Referência base:** largura útil do editor. **Integridade:** preservar atalhos e confirmação explícita. A linha atual reúne muitos botões e um texto à direita sem adaptação de largura.
3. **Localização:** cartões de decisão. **Ação principal:** exibir recomendado e selecionado, quantidade de skills de domínio e configuração efetiva; adaptar quatro cartões para duas linhas em janela estreita. **Referência base:** alinhamento e largura equivalentes. **Integridade:** preservar explicação de risco e o modelo escolhido pelo usuário.
4. **Localização:** filtros de histórico, consumo, idioma e barras de arquivo. **Ação principal:** permitir reorganização em duas linhas; usar `grid` com pesos e larguras mínimas proporcionais. **Referência base:** janela mínima de 620×500 e área útil disponível. **Integridade:** manter filtros, menus e exportações. Os `wraplength` fixos entre 820 e 950 e várias linhas horizontais precisam acompanhar a largura real.
5. **Localização:** tabelas de histórico e consumo. **Ação principal:** incluir rolagem horizontal e preservação da seleção; usar um divisor ajustável entre lista e detalhes. **Referência base:** cabeçalhos e largura das colunas. **Integridade:** preservar o painel de detalhes. A tabela de consumo declara larguras que somam 935 px, antes de margens e scrollbar.
6. **Localização:** estado da execução. **Ação principal:** apresentar Preparando, Executando, Validando, Salvando, Concluída, Falhou e Aguardando resposta como estados distintos. **Referência base:** faixa de progresso visível. **Integridade:** preservar cancelamento e dados parciais. Evitar 100% e “concluído” antes de concluir validação/gravação ou quando a execução falha.
7. **Localização:** Resposta e Arquivos. **Ação principal:** incluir copiar resposta, exportar e acesso claro aos arquivos da tarefa atual; habilitar ações de conversa apenas quando o estado permite. **Referência base:** resposta como área principal de leitura. **Integridade:** preservar links http/https e o contexto selecionado. “Tela cheia” atualmente abre uma janela 900×700; ajustar o comportamento ou o nome.
8. **Localização:** primeiro uso e erros. **Ação principal:** deixar instalação/autenticação acessíveis quando o CLI falta, inclusive no modo simples; dar botão para abrir diagnóstico diretamente na falha. **Referência base:** status do CLI e ação disponível. **Integridade:** manter opção de analisar sem CLI. Os controles de instalação são escondidos no modo simples.

Verificar visualmente português, inglês e espanhol em 100%, 125%, 150% e 200% de escala, resoluções comuns e janela mínima. Conferir teclado, ordem de foco, indicação além de cor e controles desabilitados. Esta matriz é uma proposta de validação, não um teste concluído nesta análise.

## Melhorias de arquitetura e manutenção

- Extrair gradualmente `execution_service`, `record_repository`, `backup_service`, `skill_catalog`, `assessment_rules` e componentes de cada aba. Evitar reescrever tudo ao mesmo tempo.
- Introduzir objetos tipados para decisão, configuração autorizada, tarefa, evento e métricas de turno. `pending` e muitos atributos soltos atualmente fazem estado de apresentação e estado de execução se misturarem.
- Manter códigos internos estáveis para política/status/modelo; localizar somente a apresentação. Hoje textos traduzidos precisam voltar ao português por `source_text()` para entrar em regras.
- Unificar o prompt de acordo com o idioma pedido. `build_execution_prompt()` impõe português independentemente do idioma da interface e pode conflitar com pedidos em inglês/espanhol. O idioma de entrega deve respeitar o pedido, com um padrão explícito.
- Usar parser YAML adequado, ou documentar e validar o subconjunto suportado. `_skill_profile()` divide front matter por linha e não interpreta descrições multilinha/listas YAML completas. Validar de fato `description`, já que a mensagem de instalação diz exigir esse campo.
- Manter seleção automática explicável por rotas, como já previsto pelo produto, com corpus de casos positivos e negativos em três idiomas. Não é necessário reintroduzir seleção semântica paga. Funções semânticas antigas ainda existem e são testadas embora a GUI use seleção por regras; identificar compatibilidade necessária antes de removê-las.
- Remover a definição duplicada de `on_usage_period_changed()` em 1089/1249; a segunda sobrescreve a primeira. Consolidar o conteúdo atual da orquestradora em vez de manter cadeias V1–V11 por substituições, preservando migrações necessárias em testes específicos.
- Endurecer importação/restauração: limite de arquivos e tamanho descompactado, detecção de destinos duplicados segundo regras do Windows, validação de tipos de metadados, caminhos resolvidos dentro da raiz e links/junctions. Não foi demonstrado escape de diretório nesta análise; esses itens são recomendações de robustez, não uma exploração confirmada.
- Preparar backup/pacote num arquivo temporário e publicá-lo só ao terminar. Recusar exportação `.gate` dentro do próprio workspace para evitar incluir o arquivo de saída na varredura.
- Tornar os testes uma etapa obrigatória de CI antes de publicar. O workflow atual compila/publica quando há tag, mas não executa a suíte. Centralizar versão e receita de build; o `.spec` coleta componentes diferentes do PowerShell, que inclui Playwright.
- Fixar ferramentas de build e registrar versões/hashes. O script usa upgrade de PyInstaller; uma execução futura pode gerar artefatos diferentes sem mudança do projeto.
- Separar manual de uso atual, changelog e documentos históricos. O dossiê de 11/09 mostra catálogo anterior e critérios antigos; não deve ser tratado como especificação atual. Consolidar os manuais em fontes por idioma, com checagem de consistência.

## Ordem recomendada de implementação

| Etapa | Entrega | Critério de conclusão |
|---|---|---|
| 1 | Pacotes, backup, remapeamento e gravação segura | Migração funciona sem os arquivos da origem; erros de gravação são visíveis |
| 2 | Configuração autorizada e ciclo de execução | Pasta/política/modelo exibidos são os efetivos; idioma não interrompe tarefa |
| 3 | Tokens, datas por turno e validação de texto | Cache e múltiplos dias corretos; texto português válido não é reprovado |
| 4 | Jobs de fundo e reorganização do modo simples | I/O não congela a janela; ações essenciais continuam acessíveis |
| 5 | Modularização, tradução e pipeline | Mesmas funções, menos acoplamento; testes precedem publicação |

Os testes novos devem cobrir cenários reais: migração com anexos, raiz externa, edição direta de pasta, política alterada após análise, reinício com atividade, cache aninhado, conversa em dois dias, falha de escrita e cancelamento com descendentes. Os 58 testes atuais passando não demonstram que esses casos estejam corretos.

## Registros da análise

Arquivos auxiliares ficaram em `.build-artifacts/audit/`: `inventory.json`, `probes.json`, `probe.py`, `roundtrip.py`, `restore.py` e `inventory.py`. São diagnósticos locais ignorados pelo Git. O inventário contém caminhos e hashes, sem reproduzir o conteúdo privado dos registros. Os testes exploratórios usam diretórios temporários e mocks; não são uma nova suíte de regressão incorporada ao produto.
