# Histórico de versões

## 2.8.0 — 1 de outubro de 2026

- A seleção automática usa IA para analisar a tarefa, os anexos e todas as competências instaladas, sem rotas temáticas fixas.
- Memória incremental com descrições completas e escopo; novas skills podem ser escolhidas sem cadastrar regras por nome.
- Prévia de texto, DOCX, PDF e XLSX, entrada visual de imagens, justificativas e limites visíveis antes de executar.
- Análise em segundo plano pelo CLI autenticado, sandbox somente leitura, cancelamento e validação de anexos modificados.
- Evita orquestradores redundantes e limita trechos de escopo enviados, preservando descrições e acesso às instruções completas.
- Corrige YAML da skill interna de orquestração para que seja reconhecida pelo catálogo; migra versões originais e preserva personalizações.
- Registra a decisão e os tokens da análise separadamente dos turnos da tarefa; atualiza os manuais nos três idiomas.

## 2.7.0 — 1 de outubro de 2026 (executáveis gerados localmente)

- Identifica a versão do CLI, oferece instalação/atualização oficial e consulta opcional de novas versões; Sol 6.1 passa a ser o Sol principal e o Sol 6 anterior permanece compatível com registros antigos.
- Corrige anexos em pacotes, caminhos de resultados e backup de pastas externas; permite continuar tarefas importadas em uma nova sessão.
- Usa gravações atômicas, revisão anterior recuperável e registros permanentes como histórico único; falhas de gravação ficam visíveis.
- Move preparação, histórico, indexação, validação, importação, exportação e backups para trabalhos em segundo plano; cancela processos descendentes.
- Mantém ações essenciais durante a rolagem, simplifica o modo simples, adapta controles à largura, acrescenta rolagem horizontal e divisor do histórico.
- Oferece copiar/exportar resposta e abrir diagnósticos; abertura automática de resultados é opcional, desligada por padrão e limitada após validação.
- Corrige cache de tokens aninhado, consumo por data de turno, preservação de tarifas/câmbio e falsos alertas sobre letras portuguesas.
- Separa serviços, parser YAML, catálogo e manuais; unifica receita/versão de build, fixa PyInstaller e exige testes antes da publicação.

## 2.6.20 — 24 de setembro de 2026

- Organiza os filtros e as ações de **Tarefas anteriores** em linhas mais claras.
- Dá alturas equivalentes à lista de tarefas e aos detalhes do registro selecionado.
- Agrupa as dez ações do histórico em três botões e três menus, preservando todas as funções.
- Explica que a consulta opcional do Edge sugere termos para o Codex; ela não abre um link diretamente.
- Atualiza os manuais em inglês, português e espanhol.

## 2.6.16 a 2.6.19

- Apresenta a resposta antes de atualizar histórico e arquivos, reaproveita registros já carregados e agrupa mensagens de progresso.
- Revisa a recomendação de modelo conforme a complexidade da entrega.
- Melhora a abertura da confirmação de execução e reduz janelas transitórias.
- Corrige a localização do Codex CLI no Windows e mensagens de estado da execução.

## 2.6.5 a 2.6.15

- Corrige falhas de execução e interface identificadas durante os testes com diferentes versões do Codex CLI.
- Adiciona análise de compatibilidade do CLI, consumo de tokens por execução e estimativas de custo.
- Adiciona resumo e tabelas de consumo, localizados para o idioma da interface.
- Melhora a organização do histórico, anexos, confirmação, idioma inicial em inglês e seleção de skills.

## 1.0.0 a 2.6.4

O programa evoluiu de uma interface local para preparar e executar tarefas com o Codex CLI para um aplicativo desktop com autorização explícita, projetos separados por tarefa, anexos, skills, histórico, avaliação, exportação, backup ZIP e pacote individual `.gate`. Consulte os manuais integrados para as instruções atuais de uso e preservação de dados.

> Este resumo registra os principais marcos disponíveis no histórico do projeto; não é uma lista exaustiva de cada alteração intermediária.
