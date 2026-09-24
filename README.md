# Codex Model Gate

**Uma camada de decisão e autorização para tarefas executadas pelo Codex CLI no Windows.**

O Codex Model Gate ajuda a preparar uma tarefa, avaliar sua complexidade, escolher um modelo e skills adequados e revisar a decisão antes de iniciar o Codex. Depois da autorização, acompanha a execução e organiza respostas, arquivos e registros em um só lugar.

> Versão atual: **2.6.20** · Aplicativo desktop para **Windows 10/11 x64** · Interface em **English, Português (Brasil) e Español**

## Como funciona

1. **Descreva a tarefa.** Anexe documentos ou imagens e escolha a pasta de projetos.
2. **Analise a tarefa.** O Gate apresenta a complexidade, o risco, o modelo, o nível de raciocínio e as skills recomendadas.
3. **Revise a decisão.** Você pode ajustar as opções e conferir os anexos e o destino.
4. **Autorize a execução.** O Gate inicia o Codex CLI com as opções autorizadas e uma pasta própria para aquela tarefa.
5. **Confira o resultado.** A resposta, os arquivos e o registro ficam disponíveis no aplicativo; tarefas compatíveis podem continuar na mesma sessão.

A autorização permanece com a pessoa usuária. A análise do Gate é uma recomendação e não garante que o modelo vá acertar ou que a tarefa será concluída.

## O que o programa oferece

- **Seleção de modelo por complexidade:** recomenda os modelos GPT-6 Luna, Sol e Astra conforme o tipo e a complexidade da entrega. Modelos legados continuam como opção manual secundária.
- **Skills:** consulta as skills disponíveis, sugere as que correspondem ao resultado pedido ou permite escolhê-las manualmente.
- **Pesquisa atual:** pode habilitar a busca web ao vivo do Codex para tarefas que dependem de informações atuais. Há também um navegador visual Edge opcional.
- **Fontes citadas:** as instruções do Gate pedem ao Codex para abrir a fonte original e conferir se ela sustenta a afirmação. Se a página não estiver acessível, o Codex deve informar a limitação. Essa instrução não é uma validação automática independente do conteúdo da página.
- **Histórico e arquivos:** guarda registros, organiza os resultados por tarefa e oferece busca, filtros e exportações.
- **Consumo estimado:** reúne os tokens de entrada, cache, saída e raciocínio reportados pelo CLI e estima custos. Os valores não são faturas e podem não estar disponíveis para toda execução.
- **Backups:** oferece backup geral em ZIP e exportação de uma tarefa individual como pacote `.gate`.
- **Três idiomas:** English é o idioma inicial quando nenhuma preferência foi salva; Português (Brasil) e Español também estão disponíveis.

## Baixar e executar

Os pacotes compilados devem ser publicados na seção [Releases](../../releases) do GitHub. Para a versão 2.6.20, o processo de compilação gera:

- `CodexModelGate-Setup.exe`: instalação por usuário, com atalhos e desinstalador.
- `CodexModelGate-Pendrive.exe`: versão portátil.

O computador precisa ter o **Codex CLI instalado, autenticado e compatível com o modelo escolhido** para executar tarefas. O Gate pode abrir sem o CLI, mas não consegue executar uma tarefa até que o CLI esteja disponível. Os executáveis incluem o runtime Python e as bibliotecas do aplicativo; a pessoa que recebe o pacote não precisa instalar Python.

Na edição instalada, os dados do Gate ficam na pasta local de dados do Windows. Na edição portátil, os dados ficam junto ao programa no pendrive. Os registros e arquivos de tarefa podem conter o texto enviado ao Codex e os resultados recebidos; revise e proteja essas pastas como qualquer dado de trabalho.

## Executar a partir do código-fonte

Requisitos para desenvolvimento: **Windows x64**, **Python 3.13 ou 3.14** e Codex CLI para executar tarefas.

No PowerShell, a partir da pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python codex_model_gate_gui.py
```

Para compilar o instalador e o executável portátil, com Inno Setup 6 instalado:

```powershell
.\build_windows.ps1
```

O roteiro prepara os dois arquivos em `Release`. A instalação do aplicativo compilado não exige Python.

## Estrutura do projeto

- `codex_model_gate_gui.py`: interface gráfica e integração do fluxo de trabalho.
- `codex_model_gate.py`: regras, execução, registros e funções principais do Gate.
- `gate_browser_mcp.py`: integração com o navegador visual opcional.
- `gate_i18n.py`: traduções e manuais integrados.
- `CodexModelGate.iss`, `build_windows.ps1` e `tools/`: configuração e ferramentas de empacotamento.
- `tests/`: verificações automatizadas do projeto.
- `README-INSTALADOR.md`, `README-PORTATIL.md` e `README-PENDRIVE.md`: instruções das distribuições.

## Privacidade e segurança

O Gate guarda localmente as configurações, os registros e os arquivos de trabalho. Para responder à tarefa, o conteúdo descrito e os anexos selecionados são enviados ao Codex CLI e processados conforme a conta e as condições do serviço Codex. O Gate não é um mecanismo que mantém esses conteúdos apenas no computador.

O Codex trabalha na pasta da tarefa autorizada. Revise a pasta e os anexos antes de executar e não inclua credenciais ou informações que não queira enviar ao serviço. A estimativa de consumo usa os dados reportados pelo CLI e as tarifas de referência do aplicativo; ela não consulta sua fatura.

## Licença

Este repositório ainda não contém um arquivo `LICENSE`. A visibilidade pública do código, por si só, não concede uma licença de reutilização. A licença precisa ser escolhida e adicionada antes de anunciar o projeto como software de código aberto ou aceitar contribuições externas.

## Documentação adicional

- [Instruções do instalador](README-INSTALADOR.md)
- [Instruções da versão portátil](README-PORTATIL.md)
- [Informações da versão para pendrive](README-PENDRIVE.md)

Os manuais em English, Português (Brasil) e Español também estão disponíveis na aba **Manual** do aplicativo.
