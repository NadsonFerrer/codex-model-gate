"""Compatibility-only snapshots used to upgrade unmodified built-in skills."""
ORCHESTRATOR_SKILL_CONTENT_V1 = """---
name: orquestrar-selecao-de-skills
description: Analisa a tarefa e coordena o uso das skills selecionadas pelo Gate, definindo relevância, papel e sequência antes da execução.
---

# Orquestração de skills

Antes de executar a tarefa, faça uma leitura completa do pedido, dos arquivos anexados e das skills fornecidas pelo Gate.

1. Identifique o resultado que o usuário espera, o formato de entrega, o domínio e as restrições.
2. Para cada skill selecionada, determine se ela é essencial, complementar ou não aplicável ao pedido concreto.
3. Use as skills aplicáveis com papéis claros e em uma sequência coerente; resolva instruções sobrepostas pela que for mais específica para a tarefa.
4. Não invente skills, ferramentas, dados, fontes ou capacidades que não estejam disponíveis. Se uma competência essencial estiver ausente, declare a limitação de forma objetiva.
5. Preserve as exigências explícitas do usuário. A orquestração melhora a delegação, mas não amplia autorização para ações externas.

Quando a resposta final incluir explicação, mantenha-a concisa e orientada ao resultado. Não descreva esta etapa interna, salvo se a seleção de skills afetar materialmente uma limitação ou decisão do usuário.
"""
ORCHESTRATOR_SKILL_CONTENT_V2 = """---
name: orquestrar-selecao-de-skills
description: Decompõe a tarefa e coordena as skills selecionadas pelo Gate, priorizando combinação, papel, sequência e lacunas antes da execução.
---

# Orquestração de skills

Antes de executar, transforme a tarefa em uma decisão de delegação. Leia o pedido completo, arquivos anexados, resultado esperado e todas as skills fornecidas.

## Diagnóstico da tarefa

Identifique, separadamente: entrega final e formato; domínio; público ou contexto organizacional; ação principal; restrições; evidências ou arquivos de referência; e critério de sucesso. Dê mais peso à entrega concreta e ao contexto explícito do que a palavras genéricas como “criar”, “melhorar” ou “analisar”.

## Matriz de delegação

Para cada skill selecionada, classifique mentalmente como **essencial**, **complementar** ou **não aplicável** e responda a quatro perguntas:

1. Qual parte específica da tarefa ela cobre?
2. O que ela acrescenta que nenhuma outra skill selecionada cobre?
3. Em que momento deve ser usada: enquadramento, produção, validação ou revisão?
4. Há uma skill mais específica que deve prevalecer em caso de sobreposição?

Use todas as skills essenciais e somente as complementares que aumentem materialmente a qualidade. Não descarte uma skill de contexto quando ela altera a mensagem, o público, os critérios de evidência ou a entrega; não use uma skill apenas porque compartilha uma palavra genérica.

Para peças de comunicação, combine quando aplicável: a skill de produção visual para composição e legibilidade; a skill do artefato específico para conteúdo e requisitos de uso; e a skill de contexto de negócio, marca, público ou setor para manter mensagens e alegações adequadas. Em uma tarefa ligada a startup, deeptech ou organização nomeada, trate o contexto estratégico como complementar somente se ele puder melhorar posicionamento, mensagem, público ou decisão — nunca como enfeite.

## Execução e limites

Defina uma sequência coerente: enquadrar → produzir → verificar. Preserve exigências explícitas do usuário e não invente skills, ferramentas, fontes, dados ou capacidades. Se houver uma lacuna essencial que não possa ser coberta pelas skills fornecidas, declare-a objetivamente. A orquestração não amplia autorização para ações externas.

Não descreva esta deliberação interna na resposta final, exceto quando uma limitação ou escolha de skills afetar materialmente o resultado entregue.

<!-- CODEX_MODEL_GATE_BUILTIN: ORCHESTRATOR_V2 -->
"""
ORCHESTRATOR_SKILL_CONTENT_V3 = """---
name: orquestrar-selecao-de-skills
description: Decompõe a tarefa e coordena as skills selecionadas pelo Gate, combinando domínio, evidência e formato de entrega antes da execução.
---

# Orquestração de skills

Antes de executar, transforme o pedido em uma decisão de delegação. Separe: resultado e formato; domínio; público ou contexto; ação principal; restrições; arquivos anexados; e critério de sucesso. Dê mais peso à entrega concreta e ao contexto explícito que a palavras genéricas como “criar”, “melhorar” ou “analisar”.

## Matriz de delegação

Para cada skill selecionada, classifique mentalmente como **essencial**, **complementar** ou **não aplicável**. Determine qual parte concreta ela cobre, o que acrescenta que as outras não cobrem, em que etapa entra (enquadramento, produção, validação ou revisão) e qual skill mais específica prevalece quando houver sobreposição.

Use todas as skills essenciais e somente as complementares que aumentem materialmente a qualidade. Não descarte uma skill de contexto quando ela altera a mensagem, o público, os critérios de evidência ou a entrega; não use uma skill apenas porque compartilha uma palavra genérica.

## Cadeias de competência

Quando a tarefa combinar um tema técnico ou científico com uma entrega documental, raciocine em cadeia, não como skills isoladas:

`domínio especializado → evidências e referências → redação/estrutura → formatação do arquivo → norma acadêmica aplicável → verificação final`

Por exemplo, para um PDF científico sobre marcadores ou traçadores de combustíveis, a combinação normalmente exige: a skill especializada em marcadores/traçadores de combustíveis para o conteúdo; referências científicas para sustentar afirmações; formatação de documentos/PDF para a entrega; e normalização ABNT quando o pedido for acadêmico, brasileiro ou solicitar referências segundo essa norma. Não trate a sequência como uma lista fixa: aplique somente as etapas justificadas pelo pedido e declare a norma em uso quando ela puder alterar o resultado.

Para peças de comunicação, combine quando aplicável: produção visual para composição e legibilidade; skill do artefato específico para conteúdo e requisitos de uso; e contexto de negócio, marca, público ou setor para manter mensagens e alegações adequadas. Em tarefa ligada a startup, deeptech ou organização nomeada, trate o contexto estratégico como complementar somente se ele melhorar posicionamento, mensagem, público ou decisão.

## Execução e limites

Defina uma sequência coerente: enquadrar → produzir → verificar. Preserve exigências explícitas do usuário e não invente skills, ferramentas, fontes, dados ou capacidades. Se houver uma lacuna essencial que não possa ser coberta pelas skills fornecidas, declare-a objetivamente. A orquestração não amplia autorização para ações externas.

Não descreva esta deliberação interna na resposta final, exceto quando uma limitação ou escolha de skills afetar materialmente o resultado entregue.

<!-- CODEX_MODEL_GATE_BUILTIN: ORCHESTRATOR_V3 -->
"""
ORCHESTRATOR_SKILL_CONTENT_V4 = ORCHESTRATOR_SKILL_CONTENT_V3.replace(
    "\n## Execução e limites\n",
    """
## Cadeia para melhoria de site

Para melhorar um site, comece pela especialidade web: experiência, interface, layout, responsividade, acessibilidade e implementação compatível com o pedido. Se a plataforma for explicitamente Wix, acrescente a skill de Wix para aplicar as decisões com os recursos, limites e fluxo dessa plataforma. Não use a skill de Wix em um site cuja plataforma não foi identificada como Wix; não use uma skill web apenas porque a tarefa cita uma página sem pedir análise, criação ou melhoria digital.

Quando a tarefa também envolver conteúdo, SEO, marca ou publicação, acrescente essas competências somente se o pedido as tornar necessárias. A cadeia típica é: diagnóstico do site → melhoria web → configuração específica da plataforma → validação de responsividade/acessibilidade/publicação solicitada.

## Execução e limites
"""
).replace("ORCHESTRATOR_V3", "ORCHESTRATOR_V4")
ORCHESTRATOR_SKILL_CONTENT_V5 = ORCHESTRATOR_SKILL_CONTENT_V4.replace(
    "description: Decompõe a tarefa e coordena as skills selecionadas pelo Gate, combinando domínio, evidência e formato de entrega antes da execução.",
    "description: Atua como decisora de competências: entende a tarefa, seleciona somente as skills necessárias e coordena sua execução.",
).replace(
    "# Orquestração de skills\n",
    """# Orquestração de skills

## Escolha consciente de competências

Atue como uma pessoa responsável por montar a equipe certa para a tarefa, e não como alguém que acumula skills por palavras parecidas. Antes da execução, interprete o pedido completo e pergunte: **qual resultado será entregue, qual domínio o sustenta, em que meio ele será produzido e quais capacidades são realmente necessárias?**

Inclua uma skill somente quando ela cobrir uma parte concreta da entrega ou elevar materialmente sua qualidade. Exclua explicitamente skills sem relação com o pedido, mesmo que pareçam sofisticadas ou compartilhem termos genéricos. Uma página de web design, por exemplo, pede competência de interface/web e eventualmente da plataforma declarada; não pede referências científicas, ABNT ou formatação de PDF, a menos que o usuário também solicite pesquisa científica, documento acadêmico ou arquivo PDF.

Para cada seleção, tenha uma justificativa simples do tipo “esta skill cobre X da entrega”. Se não houver essa justificativa, não a use. Prefira a skill mais específica à genérica e evite duplicações. Não acrescente uma plataforma (como Wix) sem ela ser mencionada ou comprovada pelo contexto.
""",
).replace("ORCHESTRATOR_V4", "ORCHESTRATOR_V5")
ORCHESTRATOR_SKILL_CONTENT_V6 = ORCHESTRATOR_SKILL_CONTENT_V5.replace(
    "# Orquestração de skills\n",
    """# Orquestração de skills

## Memória de competências

Atue como a camada de decisão de um espaço de trabalho contínuo. O Gate mantém uma memória local incremental com o nome, a descrição e os sinais de busca de cada skill. Use primeiro os perfis candidatos fornecidos por essa memória; não exija a releitura da biblioteca inteira a cada tarefa.

A memória serve para localizar candidatas, não para substituir suas instruções. Depois da seleção, leia integralmente apenas o `SKILL.md` de cada skill escolhida antes de executá-la. Considere novas versões quando o Gate indicar alteração e nunca invente ou reutilize uma skill removida. Se nenhuma candidata cobrir uma parte essencial do pedido, declare a lacuna em vez de forçar uma correspondência.

Organize mentalmente as escolhidas como uma pequena equipe: competência principal, competências complementares justificadas e ordem de uso. Evite duplicações e mantenha rastreável a contribuição concreta de cada uma.
""",
    1,
).replace("ORCHESTRATOR_V5", "ORCHESTRATOR_V6")
ORCHESTRATOR_SKILL_CONTENT = ORCHESTRATOR_SKILL_CONTENT_V6.replace(
    "Organize mentalmente as escolhidas como uma pequena equipe: competência principal, competências complementares justificadas e ordem de uso. Evite duplicações e mantenha rastreável a contribuição concreta de cada uma.",
    "Organize mentalmente as escolhidas como uma pequena equipe: competência principal, competências complementares justificadas e ordem de uso. Evite duplicações e mantenha rastreável a contribuição concreta de cada uma. Na seleção automática, use no máximo quatro skills de domínio (duas ao criar ou atualizar uma skill), além desta skill de orquestração; para a maioria das tarefas, uma ou duas bastam. Se o usuário quiser mais, deixe que as acrescente pela seleção manual.",
).replace("ORCHESTRATOR_V6", "ORCHESTRATOR_V7")
ORCHESTRATOR_SKILL_CONTENT_V7 = ORCHESTRATOR_SKILL_CONTENT
ORCHESTRATOR_SKILL_CONTENT = ORCHESTRATOR_SKILL_CONTENT_V7.replace(
    "## Diagnóstico da tarefa\n",
    """## Prioridade da seleção

Identifique primeiro a ação pedida e o objeto da entrega em português, inglês ou espanhol. Escolha a competência específica que realiza essa ação; acrescente outra somente se ela cobrir uma etapa adicional concreta. Para cotação atual ou data pública, use pesquisa em fontes confiáveis; para modificar um cartão corporativo, use a skill de cartões; para buscar artigos científicos, use busca de referências e, se útil, a especialidade científica do tema. Nome de empresa, país ou palavra genérica não justifica uma skill de mercado, mentoria ou orquestração ampla.

## Diagnóstico da tarefa
""",
).replace("ORCHESTRATOR_V7", "ORCHESTRATOR_V8")
ORCHESTRATOR_SKILL_CONTENT_V8 = ORCHESTRATOR_SKILL_CONTENT
ORCHESTRATOR_SKILL_CONTENT = ORCHESTRATOR_SKILL_CONTENT_V8.replace(
    "Use primeiro os perfis candidatos fornecidos por essa memória; não exija a releitura da biblioteca inteira a cada tarefa.",
    "Consulte o resumo de todas as skills indexadas fornecido pela memória. Compare as capacidades com a ação e a entrega pedidas; escolha a melhor skill ou uma combinação pequena quando as contribuições forem distintas. Não exija a releitura integral da biblioteca a cada tarefa.",
).replace("ORCHESTRATOR_V8", "ORCHESTRATOR_V9")
ORCHESTRATOR_SKILL_CONTENT_V9 = ORCHESTRATOR_SKILL_CONTENT
ORCHESTRATOR_SKILL_CONTENT = ORCHESTRATOR_SKILL_CONTENT_V9.replace(
    "Para cotação atual ou data pública, use pesquisa em fontes confiáveis;",
    "Para cotação atual, data pública ou resultados de pesquisas eleitorais, use pesquisa em fontes confiáveis;",
).replace("ORCHESTRATOR_V9", "ORCHESTRATOR_V10")
ORCHESTRATOR_SKILL_CONTENT_V10 = ORCHESTRATOR_SKILL_CONTENT
ORCHESTRATOR_SKILL_CONTENT = ORCHESTRATOR_SKILL_CONTENT_V10.replace(
    "Consulte o resumo de todas as skills indexadas fornecido pela memória. Compare as capacidades com a ação e a entrega pedidas; escolha a melhor skill ou uma combinação pequena quando as contribuições forem distintas. Não exija a releitura integral da biblioteca a cada tarefa.",
    "O Gate já selecionou competências por regras explícitas de ação e entrega. Organize somente as skills selecionadas e leia integralmente suas instruções antes de executar. Não acrescente outra skill por semelhança de palavras; se faltar uma competência, explique a lacuna ao usuário.",
).replace(
    "A memória serve para localizar candidatas, não para substituir suas instruções.",
    "A memória do Gate registra as skills disponíveis, enquanto as regras explícitas definem quais foram selecionadas para esta tarefa.",
).replace("ORCHESTRATOR_V10", "ORCHESTRATOR_V11")

ORCHESTRATOR_SKILL_CONTENT_V11 = ORCHESTRATOR_SKILL_CONTENT
