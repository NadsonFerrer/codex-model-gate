# Manual do Codex Model Gate

O Codex Model Gate organiza tarefas executadas pelo Codex CLI. Ele ajuda você a preparar a solicitação, conferir modelo e skills recomendadas, autorizar a execução e encontrar os resultados depois.

## Comece por aqui

1. Na aba **Tarefa**, escolha onde os projetos serão guardados.
2. Escreva o que deseja fazer e, se necessário, use **Anexar arquivos...**.
3. Clique em **Analisar tarefa**. O Gate recomenda modelo, nível e skills.
4. Confira a decisão. Você pode ajustar a seleção de skills antes de continuar.
5. Clique em **Confirmar e executar**. Os arquivos ficam na pasta exclusiva da tarefa.
6. Ao terminar, confira o resultado, abra os arquivos gerados e registre a qualidade.

Ao usar **Agendar tarefa...**, informe a data e a hora local em `DD/MM/AAAA HH:MM`. O Gate solicita sua confirmação no horário previsto.

### Modo simples e modelos de tarefa

O programa abre no **modo simples**, com os controles essenciais para preparar, analisar e executar uma tarefa. Logo abaixo da descrição, pesquisa e anexos ficam os botões **1. Analisar tarefa** e **2. Confirmar e executar**, seguidos pelo resumo de modelo, nível, risco e skills. A biblioteca detalhada e o acompanhamento ficam mais abaixo. Use `Ctrl+Enter` para analisar e `Ctrl+Shift+Enter` para executar. Marque **Mostrar opções avançadas** quando quiser escolher política, modelo, nível, biblioteca de skills ou consultar os detalhes técnicos da execução.

Os botões mostram o andamento pelas cores da própria interface: **Analisar tarefa** fica azul quando há uma descrição pronta; após a análise, fica verde com uma marca de conclusão, e **Confirmar e executar** fica azul. Quando a execução é acionada, o segundo botão também fica verde. Se você alterar a descrição ou os anexos, a indicação volta ao estado de preparação; analise novamente antes de executar.

Ao selecionar **Confirmar e executar**, o diálogo de autorização abre sobre a janela principal. A consulta de versão do Codex CLI ocorre em segundo plano, sem abrir uma janela adicional.

Em **Começar com um modelo**, escolha um ponto de partida para criar documento, analisar arquivo, gerar imagem, pesquisar referências ou organizar dados. Substitua os campos entre colchetes pelo seu contexto antes de analisar.

## Modelo e nível de raciocínio

O Gate recomenda automaticamente apenas os modelos principais da família GPT-6 conforme a **complexidade da entrega**, e não pela quantidade de palavras do pedido. **Luna — Leve** atende consultas pontuais e transformações delimitadas, como uma data pública ou cotação atual, com fonte apropriada quando necessário. **Sol — Leve** atende conferência explícita de um fato; **Sol — Médio/Alto** atende pesquisa, síntese, criação, julgamento especializado e trabalhos com impacto relevante. **Astra — Médio/Alto** atende entregas amplas com etapas e decisões interdependentes, elevando a revisão quando há alto impacto. A avaliação também mostra risco, uso de ferramentas, especialização, verificabilidade e ambiguidade. Nas opções avançadas, a escolha final de modelo e nível continua com o usuário. Modelos legados ficam em um seletor separado **Modelo legado**, para escolha manual; registros antigos com Terra continuam disponíveis.

Leve, Médio, Alto, Extra alto e Máximo são oferecidos conforme o modelo. Ultra depende da declaração explícita do catálogo público local da mesma versão do CLI e não é recomendado automaticamente.

Pedidos para explicar como funciona um mecanismo técnico, incluindo downconversion e upconversion, recebem pelo menos **Sol — Médio** em português, inglês ou espanhol. O Gate avalia a explicação que precisa ser entregue, mesmo que a pergunta seja curta.

### Agilidade da interface

Ao concluir uma tarefa, o Gate abre a resposta antes de atualizar os arquivos e o histórico. O painel de consumo reaproveita os registros já carregados; a estimativa de duração usa esses mesmos dados. A versão do Codex CLI verificada na sessão é reutilizada na autorização, e as mensagens de progresso são agrupadas para manter a janela responsiva. Essas medidas reduzem esperas da interface; o tempo de geração da resposta pelo modelo depende da tarefa, do nível escolhido e do Codex CLI.

### Consumo e custo estimado

Após a execução, o Gate mostra os tokens de entrada, entrada em cache, saída e raciocínio informados pelo Codex CLI, além do custo estimado para o modelo selecionado. O valor usa duas casas decimais e a moeda correspondente ao idioma. Se o CLI não enviar os dados de uso, a estimativa aparece como indisponível. A estimativa não é uma cobrança: não inclui tarifas de ferramentas, modalidades especiais, contexto longo, processamento prioritário ou diferenças de câmbio além da taxa de referência do Gate.

Em conversas com várias respostas, o registro mostra tempo e tokens de cada execução separadamente. A aba **Consumo** soma os tokens informados por essas execuções. Registros antigos sem essa separação preservam o total disponível.

Referência de preços padrão em USD por milhão de tokens de texto, para prompts com até 272 mil tokens de entrada: GPT-6 Luna, entrada US$ 0,10, cache US$ 0,01 e saída US$ 0,50; GPT-6 Sol, US$ 2, US$ 0,20 e US$ 10; GPT-6 Astra, US$ 10, US$ 1 e US$ 50. O modelo legado GPT-5.6 Terra permanece disponível para seleção manual e mantém as tarifas cadastradas no Gate: entrada US$ 2, cache US$ 0,20 e saída US$ 12. Os preços podem mudar; consulte a [tabela oficial da OpenAI](https://developers.openai.com/api/docs/pricing).

## Skills

Deixe a seleção automática ativada para o Gate escolher as skills relacionadas à tarefa. Para escolher por conta própria, marque **Usar seleção manual** e pesquise uma skill por parte do nome — não é necessário digitar o nome completo. As skills mostradas em **Skills recomendadas para esta tarefa** são as que serão usadas naquela tarefa; remover uma delas não a exclui da biblioteca.

Na seleção automática, o Gate usa o Codex CLI com Sol 6.1 — Médio para analisar o pedido, o conteúdo dos anexos e o catálogo completo de competências. A memória incremental guarda descrições completas, títulos e trechos de escopo de cada skill, atualizados quando os arquivos mudam. A IA compara capacidades, escolhe skills complementares em ordem de uso e justifica cada contribuição. Skills novas participam pelo seu escopo, sem cadastrar rotas fixas. A contagem segue a biblioteca disponível; nomes duplicados usam a versão instalada mais recentemente.

A análise é uma chamada ao modelo e consome tokens. Os perfis e o conteúdo relevante dos anexos são enviados pelo CLI autenticado. Ela ocorre em segundo plano, em sandbox somente leitura, antes da autorização da execução. Textos, DOCX, PDF com texto e XLSX têm prévias locais limitadas; PNG, JPEG e WebP são enviados para análise visual. Se necessário, a IA pode ler os originais indicados. PDFs digitalizados e formatos sem leitor disponível podem exigir OCR ou outra ferramenta; as limitações devem aparecer na recomendação.

Confira as skills, justificativas e limitações antes de confirmar. Pode cancelar a análise ou revisar a seleção manualmente. Se o CLI falhar, a análise não será considerada concluída nem substituída silenciosamente por regras locais. Se um anexo mudar, analise novamente. O registro da execução guarda a decisão e os tokens informados da análise separadamente dos turnos da tarefa. O campo opcional antigo `gate_outcomes` continua legível, mas não é exigido pela seleção inteligente.


## Tarefas anteriores e arquivos

Na aba **Tarefas anteriores**, use a barra **Buscar tarefa** para localizar uma execução pelo pedido, assunto, resposta ou nome de arquivo. A busca acontece enquanto você digita, ignora diferenças entre acentos e maiúsculas e também pode ser acessada com `Ctrl+F`. Use os filtros adicionais quando precisar restringir por data, modelo, status ou skill. Selecione uma tarefa e abra a aba **Arquivos** para ver somente os arquivos dela. Na interface em português, as datas exibidas e o filtro de data aceitam `DD/MM/AAAA` e usam hora local; o arquivo do registro preserva as datas originais para auditoria.

À direita da busca, aparece somente a quantidade de registros exibidos. Consulte os totais de tokens e custos na aba **Consumo**.

As tarefas executadas por esta versão preservam a sessão do Codex. Selecione uma delas e use **Continuar conversa** para pedir ajustes, revisar a entrega ou avançar a análise na mesma sessão e na mesma pasta. Cada nova mensagem é incorporada ao registro da tarefa. Na aba **Tarefas anteriores**, os quatro filtros ficam na mesma linha. A barra de ações mostra **Atualizar registros**, **Continuar conversa** e **Qualificar registro**; **Lista** reúne registros sem avaliação e relatório, **Abrir / exportar** reúne leitura, exportação TXT/PDF e pasta do registro, e **Pacotes .gate** reúne exportação e importação de tarefas. Nenhuma função foi removida. A barra permanece em uma linha e ganha rolagem horizontal quando necessário. A lista de tarefas e **Detalhes do registro selecionado** dividem igualmente a altura disponível; selecione um registro para ler seu conteúdo no painel rolável. Registros antigos que não possuem identificador de sessão continuam disponíveis para leitura, mas não podem recuperar retroativamente um contexto que não foi salvo.

## Links nas respostas

## Consumo

Abra a aba **Consumo** para consultar custo estimado e tokens agregados por hoje, últimos sete dias, mês, ano ou todo o período. Selecione **Personalizado** para informar as datas inicial e final em `DD/MM/AAAA`. Filtre por todos os modelos ou por Luna, Terra, Sol e Astra. A tabela identifica o modelo e discrimina tarefas, entrada, cache, saída, raciocínio e custo por hora, dia ou mês, conforme o período. Na interface em português, as datas usam dia/mês/ano, os meses aparecem como `MM/AAAA`, os milhares usam ponto e os valores monetários usam vírgula decimal e duas casas. Os campos em inglês usam datas `AAAA-MM-DD` e vírgula para milhares. Escolha a moeda automática do idioma da interface ou USD, BRL e EUR. Use **Exportar CSV...** para salvar as linhas exibidas e abri-las em uma planilha.

Na tabela **Por intervalo**, títulos e valores ficam centralizados em cada coluna, inclusive modelo, tokens e custo estimado.

O aviso junto ao resumo informa que o total é estimado, não uma cobrança da conta. O painel agrega registros locais com tokens e modelo identificável; exibe quantos registros há no período, quantos entraram nos totais e quantos foram excluídos por dados ausentes. Os custos usam os preços e o câmbio de referência cadastrados no Gate, têm duas casas decimais e podem ser recalculados com tarifas atuais: os registros guardam o modelo e os tokens, não uma fatura nem o preço vigente na data da execução.

## Links nas respostas

Endereços de páginas exibidos na resposta aparecem como hiperlinks azuis e sublinhados. Clique em um deles para abrir a página no navegador padrão do Windows. O recurso reconhece links escritos por extenso e links com título em Markdown, sempre limitados a endereços `http` ou `https` válidos.

## Pesquisa web controlada

Quando a pergunta envolve datas públicas, pesquisas eleitorais ou a skill de fontes confiáveis, o Gate disponibiliza a pesquisa web ao vivo do Codex. A tarefa começa diretamente no Codex, que pode consultar fontes atuais e citar os links usados. Confira as datas e os números na fonte original antes de utilizá-los.

Explicações de mecanismos técnicos também recebem pesquisa web ao vivo. Em todas as tarefas, o Gate instrui o Codex a conferir na página original se cada link citado sustenta diretamente a afirmação e a usar uma seção específica quando possível. Essa regra é automática. A conferência depende do acesso à página durante a execução; se não puder ser feita, o Codex deve declarar a limitação em vez de inventar a referência.

Marque **Permitir navegador visual do Gate (Edge)** para disponibilizar ao Codex um navegador visível e isolado. Marcar a caixa não inicia uma busca: a tarefa começa no Codex, e o Edge só abre se ele escolher usar a ferramenta. A sessão não reutiliza automaticamente seus logins ou histórico pessoal. Sem a caixa marcada, **Termos para busca no Edge (opcional)** fica desativado e não influencia a tarefa.

Esse campo aceita **palavras para pesquisa**, por exemplo `calendário eleições México 2027`. Elas são uma sugestão ao Codex, não um comando: ele pode pesquisar outros termos ou não usar o Edge. Se o campo ficar vazio, a descrição da tarefa é enviada como sugestão de consulta. Quando o navegador visual é usado, ele pesquisa no Google e no Bing; uma página só pode ser aberta nesse navegador se aparecer entre os resultados da pesquisa. Colar `https://exemplo.com/artigo` nesse campo faz da URL um termo de busca, **não abre a página diretamente**. Para pedir a análise de um link específico, escreva na descrição principal da tarefa, por exemplo: `Leia e resuma https://exemplo.com/artigo`. O Codex poderá tentar acessar a página com as ferramentas disponíveis e deve informar se não conseguir. Consultas pontuais sobre datas de eleições ou competições esportivas recebem Luna — Leve e acesso à busca web ao vivo; exigências de comparação ou análise elevam o nível pela complexidade da entrega.

Quando habilitado, o navegador visual é oferecido ao Codex por ferramentas MCP locais do Gate. A busca web ao vivo do Codex funciona independentemente dessa opção.

## Tela de resposta

Ao concluir uma tarefa, o Gate abre automaticamente a aba **Resposta**, inclusive no modo simples. O painel técnico continua restrito às opções avançadas, mas nunca mais será necessário ativá-lo para ler a resposta final.

Na versão 2.3.0, use **Enviar arquivo à conversa...** para acrescentar contexto a uma tarefa já concluída ou pendente. **Remover arquivo da conversa...** o desanexa das próximas mensagens, mas preserva a cópia e seu histórico para auditoria.

## Backup e dados

Use **Fazer backup...** na aba Tarefa para guardar projetos, skills, registros e configurações em um arquivo ZIP. Os novos backups usam uma estrutura interna compacta para evitar o erro de caminho longo do Windows. O arquivo `backup-manifest.json`, dentro do ZIP, relaciona cada item ao seu caminho original.

### Backup completo ZIP e pacote de tarefa `.gate`

O **backup completo ZIP** e o **pacote `.gate`** têm finalidades diferentes. O ZIP criado em **Fazer backup...** reúne os dados do Gate: projetos, biblioteca de skills, registros e configurações. Use-o para uma cópia geral ou para migrar esses dados para outro computador. Para restaurar, abra **Restaurar backup...**, selecione o ZIP e confira a prévia de arquivos e categorias. Escolha **Sim** para substituir arquivos que coincidam com os do backup; **Não** para preservar os atuais e restaurar os itens com nomes alternativos; **Cancelar** para interromper. Arquivos fora do backup nunca são removidos. Restaurar configurações de outro computador pode exigir reiniciar o Gate.

O pacote **`.gate`** contém somente uma tarefa selecionada: seu registro e os arquivos da pasta de trabalho, como anexos e resultados. Não inclui a biblioteca inteira, configurações nem outros projetos ou registros. Na aba **Tarefas anteriores**, selecione a tarefa e clique em **Exportar tarefa como pacote...**. Na outra instalação, use **Importar pacote `.gate`...**. O Gate restaura os arquivos em uma pasta exclusiva e cria um registro local. Depois, analise a tarefa importada para iniciar uma nova conversa com esse contexto. O pacote não transfere a sessão autenticada nem o identificador da conversa original; portanto, não retoma a sessão anterior. Também serve como cópia portátil isolada de uma tarefa.

Para migrar para outro computador, instale o Gate, abra-o e clique em **Restaurar backup...**. Escolha o ZIP levado do computador anterior. Se o outro computador ainda não tiver dados, escolha **Sim** para repor os itens normalmente. Se já houver dados que você quer preservar, escolha **Não**: o Gate mantém os arquivos atuais e adiciona os restaurados com um sufixo de restauração.

Os dados do programa ficam em uma pasta própria do Gate. **Abrir dados do Gate** mostra essa pasta no Explorador de Arquivos. A atualização normal do programa preserva esses dados.

## Codex CLI

O Gate precisa do Codex CLI instalado e autenticado para executar tarefas. A área **Codex CLI** informa o estado e oferece instruções de instalação. O Gate procura o executável tanto no PATH quanto na instalação do aplicativo Codex no Windows. Você ainda pode analisar e organizar uma tarefa sem o CLI, mas não poderá executá-la. **Decisão pronta** significa que a análise terminou e a execução ainda precisa ser autorizada; não significa que o modelo respondeu. Depois de **2. Confirmar e executar**, acompanhe a fase **Codex iniciado** e abra a aba **Resposta** ao concluir. Se o CLI não for localizado, a tarefa não inicia e a tela mostra o motivo.

Se houver falha na preparação ou na interface, o Gate mostra o erro em vez de deixar a tarefa esperando indefinidamente. Para diagnóstico, abra a pasta da tarefa e consulte `.codex-model-gate/startup-status.txt`; falhas de interface também são registradas em `gui-error.txt`. Uma pasta criada ou a mensagem de autorização, por si só, não comprovam que o Codex começou a executar.

Na versão 2.6.5, o cronômetro de início e duração foi corrigido. Após autorizar uma tarefa nova ou continuar uma conversa, confira a fase **Codex iniciado** antes de considerar que o processo começou.

O Gate identifica a versão instalada do CLI. Sol 6.1 (`gpt-6.1-sol`) exige CLI 0.159.1 ou posterior; Sol 6 anterior e Luna exigem 0.156.1 ou posterior. Use **Download / atualização oficial** para abrir a página oficial com instruções de instalação e atualização e depois **Verificar novamente**. **Consultar novas versões** consulta o changelog oficial, mediante seu clique, sem baixar ou executar instaladores. O catálogo público local do CLI complementa os modelos disponíveis quando corresponde à versão identificada. Acesso ao modelo também depende da conta e do workspace. Uma recusa mostra o diagnóstico; o Gate preserva o modelo autorizado.

## Dicas

- Escreva um resultado desejado claro: por exemplo, “crie um relatório PDF com estas seções”.
- Confira anexos, skills e pasta de destino antes de autorizar.
- Se o Codex fizer uma pergunta, use **Responder pergunta pendente** para manter a mesma tarefa e o mesmo contexto.
- O Gate não apaga arquivos produzidos ao cancelar uma execução; abra a pasta da tarefa para conferir o que já foi criado.


## Mudanças da versão 2.7

As ações de analisar, executar e cancelar ficam na barra inferior durante a rolagem. No modo simples, a biblioteca detalhada e os controles técnicos ficam recolhidos. Os cartões distinguem o modelo recomendado do escolhido. As linhas de controles se reorganizam conforme a largura; tabelas têm rolagem horizontal e o histórico tem divisor ajustável entre lista e detalhes. A resposta pode ser copiada ou exportada e os diagnósticos abertos diretamente. O idioma fica bloqueado durante atividade; o pedido e os anexos locais disponíveis são preservados como rascunho ao sair.

Preparação, cópia de anexos, leitura do histórico, indexação de skills, exportação/importação, backups e validação de documentos usam trabalhos em segundo plano. Resultados são apresentados antes da atualização do histórico; arquivos não se abrem automaticamente. Cancelar encerra a árvore de processos e preserva resultados parciais. Isso reduz bloqueios locais; o tempo de resposta do modelo depende do CLI, da rede e da tarefa.

Pacotes `.gate` incluem anexos ativos e remapeiam os resultados para a nova pasta. Backups incluem as pastas externas de tarefas gerenciadas; a restauração remapeia caminhos e evita transferir sessões autenticadas. Arquivos ausentes na origem não podem ser recuperados. A restauração sem substituição mantém os registros legíveis com a extensão `.md`. Credenciais do CLI não fazem parte dos pacotes ou backups. As gravações locais são atômicas, mantêm a revisão anterior e mostram falhas.

Consumo é agrupado por data de cada turno. Novos turnos preservam tarifas e câmbio de referência; **Recalcular com tarifas e câmbio atuais** é opcional. Registros antigos sem métricas por turno usam o total e a data disponíveis; sem preços históricos usam referências atuais. Registros antigos de Sol mantêm o Sol 6 anterior. Os níveis de esforço são filtrados conforme o modelo; Ultra só aparece quando declarado pelo catálogo público da versão local do CLI.

A abertura automática é opcional, desligada por padrão e limitada a três PDFs/imagens após validação e gravação bem-sucedidas.
