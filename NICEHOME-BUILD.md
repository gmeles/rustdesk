# Interlogic Support Windows build

Add these files to the fork's default branch:
- .github/workflows/nicehome-windows.yml
- .github/scripts/configure-nicehome.py
- .github/branding/interlogic/ (all image files)

The workflow uses the fork's existing bridge.yml and third-party-RustDeskTempTopMostWindow.yml.
Based on gmeles/rustdesk commit 53996e3c404ea5083df0775057e4149e49102084.
No existing tracked files are modified by this change. No signing credentials or account password is needed.

GitHub: Actions -> enable workflows if prompted -> Interlogic Windows client -> Run workflow.
Inputs are server hostname:port, relay hostname:port, HTTPS API origin, public server key.
Download Interlogic-Support-windows-x64 from the completed run's Artifacts.
The artifact includes Interlogic-Support.exe, SHA256, source commit, and customization diff.

This is an UNSIGNED source build. It changes server defaults, fallback public key, the
app name to Interlogic Support, Windows product metadata, logo, launcher and tray icons.
The provided JPEG is preserved; PNG/ICO derivatives add square padding without distorting it.
Upstream copyright, AGPL license, and legal/about attribution are retained.
Defaults are overridable by an existing client configuration. Test in clean Windows first.
The changed app name can create a separate configuration/service identity from stock RustDesk.
Only Windows x64 portable EXE is built; MSI/macOS/Linux branding is outside this workflow.
Existing app/service configuration can take precedence; a filename alone cannot distinguish builds.
The server's MUST_LOGIN policy remains the authorization boundary.

The default server/key point to the NiceHome production setup using ports 22116/22117.
Inputs are PUBLIC build configuration, not secrets. Never enter private keys or technician passwords.
Only artifacts are uploaded; this workflow does not publish a release or deploy a client.
Build dependency versions/actions follow the fork's current upstream Windows pipeline.
The build is not fully reproducible: some upstream downloads and third-party action internals
still reference mutable resources. Record and review the exact source commit before distribution.
Updating upstream may require updating the workflow and reviewing runtime customization anchors.
Retain corresponding source, submodule revision and customization diff for distributed AGPL builds.

Validation performed locally: YAML parse; script applied to actual hbb_common fixture;
invalid-input and upstream-drift rejection. No full Windows compile or runtime test performed.
Regression surface: no existing source/runtime paths changed in the repository. During this
manual CI build only, hbb_common DEFAULT_SETTINGS, RS_PUB_KEY and APP_NAME, Windows
Runner.rc product metadata, Windows/res icons, and Flutter logo/icon assets are changed
in the disposable checkout. These are necessary to embed configuration and display the
requested brand. Other workflows and normal builds retain original behavior.
