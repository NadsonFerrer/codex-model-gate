[Setup]
AppName=Codex Model Gate
AppVersion=2.6.20
AppId={{F3BCFCED-762A-4571-BD3B-C2B5D7B1FA44}
DefaultDirName={localappdata}\Programs\Codex Model Gate
DefaultGroupName=Codex Model Gate
OutputDir=Release
OutputBaseFilename=CodexModelGate-Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=assets\CodexModelGate-Setup.ico
UninstallDisplayIcon={app}\CodexModelGate.exe
CreateUninstallRegKey=yes
DisableProgramGroupPage=yes
; The Gate is a single-process desktop application.  During an update, force its
; executable to close instead of leaving the installer at an unrecoverable
; Restart Manager retry prompt.  Setup restarts it after a successful install.
CloseApplications=force
RestartApplications=yes

[Files]
; The portable EXE is the single signed-off application payload produced by the build.
; It is renamed only inside the installed directory so the program keeps its normal name.
Source: "Release\CodexModelGate-Pendrive.exe"; DestDir: "{app}"; DestName: "CodexModelGate.exe"; Flags: ignoreversion
; This marker is intentionally absent from the portable package.  It lets a custom
; installed location remain an installed edition instead of being mistaken for portable.
Source: "assets\installed.marker"; DestDir: "{app}"; Flags: ignoreversion
Source: "README-INSTALADOR.md"; DestDir: "{app}\Documentação"; Flags: ignoreversion

[Dirs]
Name: "{localappdata}\CodexModelGate\projetos"
Name: "{localappdata}\CodexModelGate\skills"
Name: "{localappdata}\CodexModelGate\registro"

[InstallDelete]
; The checkbox-like radio selection below is false by default.  Therefore a normal
; update preserves all user data; only a confirmed clean installation reaches this path.
Type: filesandordirs; Name: "{localappdata}\CodexModelGate"; Check: IsCleanInstall

[Icons]
Name: "{userprograms}\Codex Model Gate\Codex Model Gate"; Filename: "{app}\CodexModelGate.exe"; IconFilename: "{app}\CodexModelGate.exe"
Name: "{userdesktop}\Codex Model Gate"; Filename: "{app}\CodexModelGate.exe"; IconFilename: "{app}\CodexModelGate.exe"
Name: "{userprograms}\Codex Model Gate\Leia-me — versão instalada"; Filename: "{sys}\notepad.exe"; Parameters: """{app}\Documentação\README-INSTALADOR.md"""
Name: "{userprograms}\Codex Model Gate\Desinstalar Codex Model Gate"; Filename: "{uninstallexe}"; IconFilename: "{app}\CodexModelGate.exe"

[Run]
Filename: "{app}\CodexModelGate.exe"; Description: "Abrir Codex Model Gate"; Flags: nowait postinstall skipifsilent

[Code]
var
  CleanInstallPage: TInputOptionWizardPage;
  CleanInstallRequested: Boolean;

function IsCleanInstall(): Boolean;
begin
  Result := CleanInstallRequested;
end;

procedure InitializeWizard();
begin
  CleanInstallPage := CreateInputOptionPage(
    wpSelectDir,
    'Dados existentes do Codex Model Gate',
    'Escolha como tratar seus dados locais',
    'A atualização padrão preserva projetos, registros, skills e configurações. ' +
    'A instalação limpa só remove os dados próprios do Gate após confirmação.',
    True,
    False
  );
  CleanInstallPage.Add('Manter meus dados do Codex Model Gate (recomendado)');
  CleanInstallPage.Add('Fazer instalação limpa e remover os dados anteriores do Gate');
  CleanInstallPage.SelectedValueIndex := 0;
  CleanInstallRequested := False;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = CleanInstallPage.ID then
  begin
    if CleanInstallPage.SelectedValueIndex = 1 then
    begin
      if not CleanInstallRequested then
      begin
        if MsgBox(
          'Confirma a remoção dos dados do Codex Model Gate em:' + #13#10 +
          ExpandConstant('{localappdata}\CodexModelGate') + #13#10 + #13#10 +
          'Serão removidos somente projetos, registros, skills e configurações do Gate. ' +
          'Nenhum outro arquivo do computador será removido.',
          mbConfirmation,
          MB_YESNO
        ) = IDYES then
          CleanInstallRequested := True
        else
        begin
          CleanInstallPage.SelectedValueIndex := 0;
          CleanInstallRequested := False;
        end;
      end;
    end
    else
      CleanInstallRequested := False;
  end;
end;
