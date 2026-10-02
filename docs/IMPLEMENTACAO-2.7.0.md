# Implementação e verificação — Codex Model Gate 2.7.0

Data: 1 de outubro de 2026. Referência: [auditoria inicial](AUDITORIA-PROJETO-2026-10-01.md).

Esta entrega modifica o código, os testes, os manuais e o processo de build. Não gera instaladores, não publica releases, não atualiza o CLI instalado e não inicia tarefas pagas.

## Prioridades da auditoria

| Prioridade | Entrega implementada | Evidência principal |
|---|---|---|
| Pacotes e anexos | `.gate` inclui anexos ativos, preserva cópias na pasta da tarefa e remapeia resultados; contexto importado pode iniciar uma nova sessão na pasta restaurada | Testes de migração após remoção da origem e integração da conversa importada |
| Backup e restauração | Inclui pastas externas gerenciadas, remapeia caminhos, conserva `.md` ao restaurar sem substituir, recupera prefixos de projetos de backups antigos quando identificáveis | Testes de raiz externa, restauração sem substituição e formato antigo |
| Idioma durante atividade | Bloqueia reinício durante preparação, execução, indexação e persistência; preserva rascunho ao sair/reiniciar em repouso | Integração de bloqueio de idioma |
| Configuração efetiva | Lê o destino e a política no momento da autorização, valida restrições portáteis e esforço, utiliza configuração imutável para preparar a tarefa | Integração com destino digitado e política alterados após análise |
| Gravação e histórico | Escritas atômicas, revisão anterior recuperável, erros explícitos; Markdown permanente é a fonte do histórico, sem nova gravação paralela em `history.json` | Falha de substituição, recuperação e erro de gravação na interface |
| Consumo | Cache aninhado, distinção de totais cumulativos, datas por turno, tarifas/câmbio salvos e recálculo opcional; Sol antigo permanece associado ao modelo anterior | Testes de parser, datas, preços e compatibilidade de registros |
| Texto português | Detecta sequências comuns de corrupção sem reprovar `CONCLUSÃO`, `REFERÊNCIAS` ou `ÂNCORA` | Teste com texto legítimo e texto corrompido |
| Escolha de modelo | Separa recomendado/selecionado, sincroniza cartões e política, filtra esforço por modelo e utiliza catálogo público correspondente à versão local | Integração dos cartões e testes de capacidades/catálogo |
| Agilidade | Preparação, cópia, leitura do histórico, indexação, importação/exportação, backup, validação e gravação de resultados em trabalhos de fundo; busca usa cache e atraso curto durante digitação | Integração da execução e medição de reconsulta do histórico |
| Cancelamento | Supervisor com Job Object no Windows e fallback `taskkill /T`; cópia de anexos verifica cancelamento em blocos | Teste com processo descendente real e preparação cancelada |

## Interface

- Barra inferior mantém analisar, executar e cancelar disponíveis durante a rolagem.
- Modo simples recolhe biblioteca detalhada e controles técnicos; recuperação do CLI continua acessível.
- Cartões em duas linhas e controles reorganizados conforme a largura.
- Tabelas com rolagem horizontal; seleção do histórico preservada e divisor ajustável entre lista e detalhes.
- Copiar/exportar resposta, abrir pasta da tarefa e diagnósticos; leitor maximizado.
- Resposta apresentada antes da atualização do histórico. Abertura automática de resultados é desligada por padrão; quando habilitada, só ocorre após validação e gravação bem-sucedidas, com até três arquivos PDF/imagem.
- Indicação de preparação, execução, validação, gravação, espera por resposta, cancelamento e falhas; erro de gravação mantém a resposta disponível.

## CLI e modelos

`gate_models.py` centraliza versão do programa, IDs, mínimos conhecidos e esforços. O Sol principal usa `gpt-6.1-sol`; `gpt-6-sol` permanece como opção anterior. Registros antigos não trocam silenciosamente de modelo.

O Gate identifica o executável e sua versão em segundo plano. Na autorização, verifica se o executável mudou e pede nova checagem quando necessário. O botão **Download / atualização oficial** abre a [página oficial do CLI](https://learn.chatgpt.com/docs/codex/cli), onde o usuário deve selecionar Windows. **Consultar novas versões** lê o [changelog oficial](https://learn.chatgpt.com/docs/changelog), com timeout e leitura limitada, sem baixar código executável.

Sol 6.1 exige CLI 0.159.1 ou posterior, conforme a entrada de lançamento no changelog. O executável local identificado nesta análise foi 0.159.2; a consulta real ao changelog retornou 0.160.0 no momento da verificação. Esses valores são registros desta execução, não uma definição permanente da versão mais recente.

O catálogo público local complementa a lista quando sua versão corresponde ao CLI identificado. Campos de identidade e autenticação não são utilizados. Ultra só é exposto quando declarado nesse catálogo compatível. O catálogo não comprova acesso da conta: plano, cliente e configurações do workspace também influenciam a disponibilidade. Uma recusa continua visível e não troca automaticamente o modelo autorizado.

## Organização do código e build

Serviços separados: `gate_storage`, `gate_archives`, `gate_execution`, `gate_records`, `gate_usage`, `gate_models`, `gate_skills`, `gate_widgets` e `gate_manuals`. O conteúdo atual da orquestradora tem uma única definição; templates antigos permanecem isolados para migrações compatíveis. A seleção por regras existente foi preservada.

Metadados de skills usam PyYAML seguro, incluindo valores multilinha, e exigem nome/descrição. Importações limitam quantidade e tamanho, rejeitam destinos duplicados segundo comparação sem distinção de maiúsculas, caminhos inválidos e links; destinos resolvidos permanecem dentro da raiz autorizada. Pacotes e backups são publicados por substituição de arquivo temporário ao concluir.

Manuais atuais ficam em `docs/manual/{pt-BR,en,es}.md`, separados do changelog e dos documentos históricos. Os valores internos permanecem em chaves estáveis; textos traduzidos são convertidos na fronteira dos controles.

PowerShell e CI utilizam o mesmo `.spec`, que coleta Playwright, YAML e os manuais. `APP_VERSION` fornece a versão ao instalador. PyInstaller fica fixado em `requirements-build.txt`; o build registra dependências e hashes. Testes precedem empacotamento/publicação e a tag deve corresponder à versão do código. O script de build foi conferido sintaticamente, mas não executado para gerar produtos nesta entrega.

## Verificação

- **88 testes passaram**, incluindo cinco testes com widgets Tk reais, CLI simulado e dados temporários.
- Cancelamento de descendentes testado com processos Python reais no Windows; nenhuma tarefa do Codex foi executada nesse teste.
- Verificados abertura, redimensionamento até 620 × 500, modos simples/avançado, visibilidade das ações, sincronização dos cartões, fluxo autorizado completo, gravação e falha de gravação.
- Consulta real somente de leitura ao changelog oficial funcionou.
- Compilação sintática dos módulos Python, análise sintática de PowerShell e `git diff --check` sem erro.

### Medição de desempenho

Comparação local da implementação original de leitura com a reconsulta atual após carregar o cache: 1.000 registros sintéticos, respostas de aproximadamente 8 KB, mediana de cinco consultas.

| Operação | Tempo mediano |
|---|---:|
| Leitura original | 162,56 ms |
| Reconsulta com cache | 24,26 ms |

A reconsulta foi aproximadamente 6,7 vezes mais rápida nesse cenário e não releu o conteúdo dos arquivos inalterados. A primeira consulta ainda precisa ler os registros; o cache também verifica os metadados dos arquivos. Isso não mede o tempo do modelo, a rede ou uma execução real de tarefa paga. Fontes da medição e resultados ficam em `.build-artifacts/upgrade/benchmark.py` e `benchmark.json`, ignorados pelo Git.

## Limites e compatibilidade

Arquivos que já faltavam no backup/pacote de origem não podem ser reconstruídos. Backups antigos sem caminhos suficientes para inferir a origem não permitem remapeamento completo de pastas externas que não foram incluídas; o formato novo passa a registrá-las. Restauração não transfere autenticação e abre contexto migrado em nova sessão.

Validação de PDF/DOCX verifica aspectos específicos de texto e estrutura; não comprova integralmente diagramação visual ou validade científica. Tarifa/câmbio são referências estimativas, não fatura; registros antigos usam os dados históricos disponíveis e referências atuais quando não há preço salvo.

Os testes integram o programa a um CLI simulado, além de verificar versão e consulta oficial reais. Não comprovam acesso pago a todos os modelos nem o comportamento do instalador. Os executáveis existentes em `Release` continuam anteriores: a entrega atual é o código 2.7.0, aguardando uma solicitação de empacotamento.

## Empacotamento solicitado e concluído

Após a solicitação do usuário, os dois executáveis 2.7.0 foram gerados em `Release` em 1 de outubro de 2026. O instalador tem versão de produto 2.7.0. Os 88 testes passaram novamente antes do build; o protocolo MCP do executável portátil respondeu corretamente a `initialize` e `tools/list`, com saída zero e sem erros. Foram conferidos os hashes SHA-256, os três manuais e os arquivos Tcl/Tk incluídos no portátil.

Arquivos: `CodexModelGate-Setup.exe`, `CodexModelGate-Pendrive.exe`, `LEIA-ME-PORTATIL.md`, `SHA256SUMS.txt` e `BUILD-DEPENDENCIES.txt`. O empacotamento usa Python 3.14.6, PyInstaller 6.22.3 e Inno Setup local. A geração não instala o programa no computador nem publica no GitHub. O instalador não foi executado nesta verificação.
