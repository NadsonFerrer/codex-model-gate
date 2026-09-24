# LEIA-ME — Codex Model Gate portátil

## Versão 2.6.20 — portátil gerado em 24/09/2026

Na aba Tarefas anteriores, filtros e comandos ficam alinhados, a lista e os detalhes recebem alturas iguais, e as dez ações permanecem acessíveis em três botões e três menus. O campo de termos do Edge agora explica que sugere buscas ao Codex e não abre links diretamente. O manual descreve esse comportamento em português, inglês e espanhol.

## Versão 2.6.16 — portátil gerado em 24/09/2026

Recomenda Sol — Médio para explicações de mecanismos técnicos, oferece conferência persistente das páginas citadas e registra tempo e tokens por resposta em conversas.

## Versão 2.6.15 — portátil gerado em 24/09/2026

Mostra a resposta antes das atualizações de arquivos e histórico, reaproveita os registros já carregados e a versão verificada do CLI, e agrupa mensagens de progresso para manter a janela responsiva.

## Versão 2.6.14 — portátil gerado em 24/09/2026

Revisa a escolha de modelo conforme a complexidade da entrega, sem usar o tamanho do pedido: Luna para consultas pontuais, Sol para conferência e trabalho com julgamento, Astra para entregas amplas com decisões interdependentes.

## Versão 2.6.12 — portátil gerado em 24/09/2026

Oculta a janela transitória da consulta de versão do Codex CLI e vincula o diálogo de confirmação à janela principal.

## Versão 2.6.11 — portátil gerado em 24/09/2026

Retira o resumo de custo da barra de busca de **Tarefas anteriores**. Nesse espaço fica apenas a contagem de registros; os totais permanecem na aba **Consumo**.

## Mudança incluída da 2.6.10

Localiza datas e números exibidos em Consumo, Tarefas anteriores e Arquivos conforme o idioma da interface. Em português do Brasil, as datas usam dia/mês/ano e os milhares usam ponto.

## Mudança incluída da 2.6.9

Centraliza os títulos e valores de todas as colunas da tabela **Por intervalo** na aba Consumo.

## Mudança incluída da 2.6.8

Os botões **Analisar tarefa** e **Confirmar e executar** agora distinguem por cor as etapas prontas e acionadas. Se a descrição ou os anexos mudarem, a análise anterior deixa de valer.

## Mudança incluída da 2.6.7

Corrige a falha de interface ao organizar os botões de **Tarefas anteriores**. Os botões continuam disponíveis quando a janela muda de largura.

## Versão 2.6.6

O Gate detecta um Codex CLI anterior à versão 0.156.1 antes de executar GPT-6 Sol ou Luna e oferece a atualização pelo instalador oficial. Uma recusa do CLI não é atribuída automaticamente à conta; a recomendação do modelo permanece.

## Versão 2.6.5

Corrige a falha `datetime.time has no attribute monotonic` ao iniciar ou continuar uma tarefa.

## Versão 2.6.4

O início da tarefa registra as etapas após carregar as skills e prossegue mesmo se um elemento secundário da interface falhar. Erros de interface são exibidos e gravados na pasta da tarefa.

## Versão 2.6.3

O Gate localiza o Codex CLI tanto no PATH quanto na pasta da instalação do Codex para Windows. A tela informa quando a execução foi autorizada, quando está preparando a tarefa e quando o processo do Codex realmente iniciou. Uma falha para localizar o CLI aparece antes da criação da pasta da tarefa.

## Versão 2.6.2

Perguntas sobre datas públicas e pesquisas eleitorais iniciam o Codex diretamente, com pesquisa web ao vivo para consultar fontes atuais. A skill de fontes confiáveis não ativa mais uma pesquisa prévia no Edge. O navegador visual do Gate é opcional e só abre se o Codex utilizar sua ferramenta. Na primeira abertura sem preferência salva, a interface aparece em inglês; o idioma pode ser alterado em **Idioma / Language**.

## Memória inteligente de skills

A memória local das skills fica dentro de `CodexModelGate-Dados` no próprio pendrive. O Gate reaproveita os perfis que não mudaram, atualiza apenas skills novas ou editadas e entrega à orquestradora uma lista curta de candidatas para cada tarefa.

## Pesquisa web e resposta

A pesquisa web autorizada usa o Microsoft Edge instalado no computador em uma sessão isolada e visível. Os relatórios ficam na pasta da tarefa no pendrive. A resposta textual é aberta automaticamente na aba **Resposta**, inclusive no modo simples.

A versão 1.6.1 conecta essa capacidade ao Codex por ferramentas MCP `gate_browser_*`. O servidor MCP funciona dentro do próprio executável portátil e somente é habilitado para a tarefa após a confirmação do usuário.

## Busca de tarefas anteriores

A versão 1.7.0 inclui uma barra de busca no topo de **Tarefas anteriores**, com pesquisa instantânea no pedido, nas respostas, na conversa e nos nomes dos arquivos. Use `Ctrl+F` para ir diretamente à busca.

## Interface principal reorganizada

Na versão 1.8.0, análise, execução e os cartões de decisão ficam próximos do campo onde a tarefa é escrita. A biblioteca de skills e o acompanhamento continuam abaixo, sem interromper o fluxo principal.

Na versão 1.9.0, os links exibidos na resposta ficam azuis, sublinhados e clicáveis. Um clique abre endereços `http` ou `https` válidos no navegador padrão do Windows.

## Idiomas

A versão 2.0.0 oferece Português (Brasil), English e Español. Use **Idioma / Language** no topo da aba de tarefa. A escolha fica salva em `CodexModelGate-Dados` no próprio pendrive e acompanha os backups.

A versão 2.0.1 reinicia a edição portátil em um ambiente temporário independente depois da troca de idioma, evitando conflito com a pasta `_MEI` da instância anterior.

Na versão 2.1.0, toda a interface visível, inclusive mensagens e estados dinâmicos, acompanha inglês ou espanhol. Os manuais nesses idiomas têm o mesmo conteúdo funcional do manual em português.

A versão 2.2.0 apresenta o novo tema visual em azul-petróleo e verde, com botões principais, cartões, abas, tabelas e estados de foco mais fáceis de reconhecer.

Na versão 2.3.0, a aba **Resposta** também permite enviar arquivos adicionais para uma conversa já iniciada ou desanexar arquivos das próximas mensagens. As cópias e o histórico permanecem no pendrive para auditoria.

## Uso rápido

1. Copie `CodexModelGate-Pendrive.exe` e este arquivo para uma pasta do pendrive.
2. Abra `CodexModelGate-Pendrive.exe` com duplo clique.
3. Mantenha o executável no pendrive durante o uso para que todos os dados fiquem
   nele.

Esta edição é um executável direto. Ela não é instalada no Windows e não cria
atalhos, desinstalador ou entrada de registro do Codex Model Gate no computador.
Não é necessário instalar Python, `pip` ou bibliotecas de PDF/DOCX para abri-la.

## Seus dados viajam com o pendrive

O programa cria os dados ao lado do executável:

```text
CodexModelGate-Dados\
├── projetos\       # uma subpasta exclusiva por tarefa
├── skills\         # skills instaladas ou criadas no Gate
├── registro\       # histórico, evidências e relatórios
├── codex-cli\      # sessão e configurações locais do Codex CLI
├── temporarios\    # arquivos temporários da execução
└── settings.json    # preferências do Gate
```

Assim, projetos, arquivos de tarefa, registros, configurações, skills, sessão do
Codex e arquivos temporários permanecem no pendrive. Use **Abrir dados do Gate** para conferir a pasta e **Fazer backup...**
para gravar uma cópia ZIP em outro local seguro.

## Restaurar em outro computador

Copie o ZIP de backup para o novo computador ou pendrive, abra o Gate e use
**Restaurar backup...**. O programa mostra uma prévia do conteúdo antes de mudar
qualquer dado. Use **Não** para preservar o que já existir e importar os itens com
um nome de restauração; use **Sim** apenas quando quiser substituir arquivos de
mesmo nome. O ZIP usa nomes internos curtos para evitar o erro 0x80010135 de
caminho longo no Windows.

Antes de uma execução ou da instalação de um componente adicional, o Gate informa o
espaço disponível e a estimativa mínima necessária. Se o espaço for insuficiente,
libere capacidade no pendrive antes de continuar.

## Atualização

Feche o Gate e substitua apenas `CodexModelGate-Pendrive.exe` pela versão mais
recente. Preserve a pasta `CodexModelGate-Dados` e este `LEIA-ME-PORTATIL.md`.

## Requisitos

- Windows 10 ou Windows 11 em arquitetura x64 compatível.
- Codex CLI instalado e autenticado para executar tarefas.

Sem o Codex CLI, o Gate continua permitindo analisar tarefas e ver recomendações,
mas não pode executá-las.

As tarefas executadas a partir da versão 1.4.0 preservam a sessão do Codex no
registro. Na aba **Tarefas anteriores**, use **Continuar conversa** para revisar
uma entrega ou pedir ajustes na mesma sessão e na mesma pasta do pendrive.

Na primeira execução portátil, o Codex CLI pode pedir autenticação. A sessão do
CLI é mantida na pasta `codex-cli` do pendrive, e não no perfil do Windows usado
naquele computador.
