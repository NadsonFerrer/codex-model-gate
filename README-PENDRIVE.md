# Codex Model Gate no pendrive

## Não é um instalador

Para o pendrive, entregue os dois itens gerados em `Release`:

```text
CodexModelGate-Pendrive.exe
LEIA-ME-PORTATIL.md
```

Copie ambos para uma pasta do pendrive e abra `CodexModelGate-Pendrive.exe` com
duplo clique. Não existe `CodexModelGate-Pendrive-Setup.exe` na distribuição atual:
a versão de pendrive é um executável portátil direto, não uma instalação.

Ela não cria atalhos, desinstalador ou entrada de registro do Gate no computador em
que é aberta. O Codex CLI, quando necessário para executar tarefas, é um requisito
separado e precisa estar instalado no computador usado. A sessão usada pela edição
portátil é mantida no próprio pendrive.

## O que fica no pendrive

Ao lado do executável, o Gate mantém todos os seus dados em:

```text
CodexModelGate-Dados\
├── projetos\
├── skills\
├── registro\
├── codex-cli\
├── temporarios\
└── settings.json
```

Projetos, arquivos de tarefa, registros, configurações, skills instaladas pela
interface, sessão do Codex e temporários permanecem nessa pasta. Para atualizar, feche o programa e substitua
somente `CodexModelGate-Pendrive.exe`; não apague `CodexModelGate-Dados`.

Antes de iniciar uma tarefa ou instalar um componente adicional, confira o aviso de
espaço livre exibido pelo Gate. Quando a capacidade disponível não for suficiente,
libere espaço ou use outro pendrive antes de prosseguir.

## Uso diário

1. Conecte o pendrive e abra `CodexModelGate-Pendrive.exe` a partir dele.
2. Se solicitado, faça a autenticação do Codex CLI; ela ficará em `codex-cli` no
   pendrive.
3. Anexe referências, analise a tarefa e autorize a execução.
4. Abra **Dados do Gate** ou **Abrir arquivos da tarefa** para consultar os
   resultados no próprio pendrive.

Remova o pendrive somente depois de fechar o Gate e concluir cópias ou backups.
