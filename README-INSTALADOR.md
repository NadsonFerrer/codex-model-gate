# Codex Model Gate — versão instalada no computador

## Versão 2.6.20 — instalador gerado em 24/09/2026

Na aba Tarefas anteriores, filtros e comandos ficam alinhados, a lista e os detalhes recebem alturas iguais, e as dez ações permanecem acessíveis em três botões e três menus. O campo de termos do Edge agora explica que sugere buscas ao Codex e não abre links diretamente. O manual descreve esse comportamento em português, inglês e espanhol.

## Versão 2.6.16 — instalador gerado em 24/09/2026

Recomenda Sol — Médio para explicações de mecanismos técnicos, oferece conferência persistente das páginas citadas e registra tempo e tokens por resposta em conversas.

## Versão 2.6.15 — instalador gerado em 24/09/2026

Mostra a resposta antes das atualizações de arquivos e histórico, reaproveita os registros já carregados e a versão verificada do CLI, e agrupa mensagens de progresso para manter a janela responsiva.

## Versão 2.6.14 — instalador gerado em 24/09/2026

Revisa a escolha de modelo conforme a complexidade da entrega, sem usar o tamanho do pedido: Luna para consultas pontuais, Sol para conferência e trabalho com julgamento, Astra para entregas amplas com decisões interdependentes.

## Versão 2.6.12 — instalador gerado em 24/09/2026

Oculta a janela transitória da consulta de versão do Codex CLI e vincula o diálogo de confirmação à janela principal.

## Versão 2.6.11 — instalador gerado em 24/09/2026

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

Perguntas sobre datas públicas e pesquisas eleitorais iniciam o Codex diretamente, com pesquisa web ao vivo para consultar fontes atuais. A skill de fontes confiáveis não ativa mais uma pesquisa prévia no Edge. O navegador visual do Gate é opcional e só abre se o Codex utilizar sua ferramenta. Ao atualizar, mantenha a opção padrão do instalador para preservar projetos, registros, skills e configurações. Na primeira abertura sem preferência salva, a interface aparece em inglês; o idioma pode ser alterado em **Idioma / Language**.

## Memória inteligente de skills

O programa mantém um índice local das skills instaladas. Na primeira leitura ele registra os dados necessários para localizar cada habilidade; depois, reaproveita as que não mudaram e atualiza somente skills novas, editadas ou removidas. Em bibliotecas grandes, a orquestradora analisa primeiro uma lista curta de candidatas e abre as instruções completas apenas das skills escolhidas.

## Pesquisa web e resposta no modo simples

A versão 1.6.0 pode abrir o Microsoft Edge em uma sessão isolada e visível para consultar Google e Bing quando o usuário autoriza a pesquisa na tarefa. O relatório registra títulos, URLs, buscador e posição aproximada. O Edge precisa estar instalado. Verificações ou bloqueios apresentados pelos buscadores não são burlados.

Na versão 1.6.1, o navegador também é conectado à sessão do Codex como servidor MCP. O agente recebe ferramentas próprias para pesquisar, abrir resultados, ler a página atual e fechar o navegador. Elas não aparecem na lista `browsers` do navegador interno da OpenAI; aparecem como ferramentas `gate_browser_*`.

A resposta textual agora possui uma aba própria e é exibida automaticamente ao final da execução, mesmo quando as opções avançadas estão desativadas.

## Busca de tarefas

A versão 1.7.0 apresenta uma barra **Buscar tarefa** no topo de **Tarefas anteriores**. Ela pesquisa enquanto o usuário digita no pedido original, nas respostas, na conversa e nos nomes dos arquivos gerados. A busca ignora diferenças entre acentos e maiúsculas. Também há botões Buscar e Limpar busca e o atalho `Ctrl+F`.

## Fluxo principal mais próximo

Na versão 1.8.0, os botões **1. Analisar tarefa** e **2. Confirmar e executar** aparecem logo depois da descrição, pesquisa web e anexos. Os cartões de modelo, nível, risco e skills ficam imediatamente abaixo desses botões. A biblioteca detalhada foi movida para depois da decisão e o acompanhamento permanece na parte inferior. Atalhos: `Ctrl+Enter` para analisar e `Ctrl+Shift+Enter` para executar.

Na versão 1.9.0, endereços web apresentados na resposta ficam clicáveis e abrem no navegador padrão do Windows. São reconhecidos links em Markdown e URLs escritas por extenso; apenas endereços `http` e `https` válidos são abertos.

Na versão 2.0.0, a interface passou a oferecer Português (Brasil), English e Español. Escolha **Idioma / Language** no topo da aba de tarefa; o programa salva a preferência e reinicia para carregar menus, fluxo principal, histórico e manual no idioma escolhido. O comportamento inicial foi posteriormente alterado para abrir em inglês quando não há preferência salva.

A versão 2.0.1 corrige o reinício após a troca de idioma nos executáveis empacotados. Cada nova instância recebe seu próprio ambiente temporário, evitando os avisos “Failed to remove temporary directory” e “Failed to start embedded python interpreter”.

Na versão 2.1.0, inglês e espanhol cobrem também textos dinâmicos, caixas de diálogo, contadores, progresso, níveis, políticas, modelos de tarefa e estados do programa. Os dois manuais estrangeiros possuem a mesma abrangência do manual em português.

A versão 2.2.0 adota uma identidade visual mais colorida e profissional: cabeçalho azul profundo, ações principais em azul-petróleo, ações secundárias em verde suave, cartões em azul-claro, abas destacadas e tabelas com maior contraste. Campos de escrita e leitura permanecem claros para preservar conforto visual.

Na versão 2.3.0, a aba **Resposta** permite enviar arquivos adicionais a uma conversa e desanexar arquivos que não devem ser usados nas próximas mensagens. O Gate preserva a cópia de trabalho e registra o desanexamento, sem reescrever o histórico da tarefa.

## Arquivo de instalação

Use `Release\CodexModelGate-Setup.exe`. Este é o instalador real do Windows: ele
instala o programa para o usuário atual, cria atalhos no Menu Iniciar e na Área de
Trabalho e registra **Codex Model Gate** em **Configurações > Aplicativos
instalados** (também visível em “Desinstalar um programa”). Não exige privilégios
de administrador.

## Instalação ou atualização

1. Abra `CodexModelGate-Setup.exe`.
2. Escolha a pasta do aplicativo, se quiser uma diferente da sugerida.
3. Na tela **Dados existentes do Codex Model Gate**, mantenha a opção padrão
   **Manter meus dados** para instalar ou atualizar sem perder histórico.
4. Conclua a instalação e abra o Gate por um dos atalhos criados.

Por padrão, o aplicativo é instalado em:

```text
%LOCALAPPDATA%\Programs\Codex Model Gate\
```

## Instalação limpa — escolha explícita

Na mesma tela do instalador, a segunda opção é **Fazer instalação limpa e remover
os dados anteriores do Gate**. Ela só funciona após uma confirmação adicional que
mostra o caminho exato afetado:

```text
%LOCALAPPDATA%\CodexModelGate\
```

Quando confirmada, essa ação remove somente os dados do Gate — `projetos`,
`registro`, `skills` e configurações. Ela não remove documentos, perfis ou arquivos
de outros programas. Faça um backup pela interface antes de escolher essa opção se
quiser preservar os dados.

## Dados e desinstalação

Os dados ficam separados dos arquivos do programa, em:

```text
CodexModelGate\
├── projetos\
├── skills\
└── registro\
```

Atualizações e a desinstalação padrão preservam essa pasta. Para remover somente o
aplicativo, use **Configurações > Aplicativos instalados > Codex Model Gate >
Desinstalar** ou o atalho **Desinstalar Codex Model Gate** no Menu Iniciar.

## Primeiro uso

1. O programa abre no modo simples, com um pequeno guia inicial. Descreva a tarefa ou selecione um modelo pronto e, se necessário, anexe arquivos de referência.
2. Analise a recomendação, incluindo a justificativa do modelo e do nível. As recomendações automáticas usam GPT-6 Luna para tarefas claras, GPT-6 Sol para trabalho cotidiano ou especializado e GPT-6 Astra para fluxos críticos. Modelos legados, como Terra, ficam em uma opção separada para escolha manual. Máximo e Ultra não são recomendados automaticamente.
3. Cada execução usa uma subpasta exclusiva em `projetos`; os resultados aparecem
   em **Resultados e arquivos criados**, com tipo, tamanho, data e prévia de imagens.

Se o Codex fizer uma pergunta, o Gate mantém a tarefa em continuação para que você
responda na mesma sessão e abra os arquivos associados. Para executar tarefas, o
Codex CLI precisa estar instalado e autenticado; o Gate oferece orientação quando
ele não é encontrado.

Depois da conclusão, selecione a tarefa na aba **Tarefas anteriores** e clique em
**Continuar conversa** para pedir ajustes ou avançar a análise na mesma sessão e
na mesma pasta. As mensagens seguintes são incorporadas ao mesmo registro. Essa
continuidade está disponível para tarefas executadas a partir da versão 1.4.0,
quando o identificador da sessão passou a ser salvo no histórico permanente.

## Levar um backup para outro computador

No computador novo, instale e abra o Gate. Na aba **Tarefa**, use **Restaurar
backup...** e escolha o ZIP criado no computador anterior. Antes de restaurar, o
programa mostra uma prévia com quantidade, tamanho, projetos, skills, registros e
configurações encontrados. Escolha **Sim** somente se quiser substituir arquivos
com o mesmo nome; escolha **Não** para preservar o que já existe e trazer os itens
restaurados com um sufixo próprio. Arquivos fora do backup nunca são removidos.
