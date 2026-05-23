---
name: /enum
description: Enumera servicios identificados en recon para descubrir endpoints, recursos y configuraciones explotables.
version: 0.1
author: h4ckforge
license: MIT
---

## When to Use

Después de que session_state.recon_done = true. Si recon_done = false, mostrar advertencia estándar (ver recon/SKILL.md) y esperar confirmación antes de continuar.

## Quick Reference

| Herramienta | Protocolo / Servicio | Uso típico |
|---|---|---|
| gobuster dir | HTTP/HTTPS | Fuerza bruta de directorios y archivos |
| ffuf | HTTP/HTTPS | Fuzzing de parámetros, headers, subdominios |
| nikto | HTTP/HTTPS | Escaneo de vulnerabilidades web conocidas |
| enum4linux | SMB (445/139) | Usuarios, shares, políticas en Windows/Samba |

## Procedure

1. Leer session_state.findings[] para identificar puertos/servicios en scope.
2. Bifurcar por protocolo detectado:

   **Rama Web (puertos 80, 443, 8080, 8443 u otros HTTP identificados):**
   - **Pipeline paralelo** — lanzar simultáneamente:
     - **Terminal 1 (background):** `gobuster dir -u http://<target> -w /usr/share/wordlists/dirb/common.txt -o gobuster_<target>.txt`
     - **Terminal 2 (inmediato):** `nikto -h http://<target> -o nikto_<target>.txt`
     - **Terminal 2 (continuar):** `ffuf -u http://<target>/FUZZ -w /usr/share/wordlists/dirb/common.txt -o ffuf_<target>.json`
   - No esperar a gobuster para iniciar nikto/ffuf. Ningún turno de espera sin otra tarea activa.
   - Documentar a medida que llegan resultados: código de respuesta, tamaño, título de página.

   **Rama SMB (puertos 445 o 139):**
   - `enum4linux -a <target> | tee enum4linux_<target>.txt`
   - Documentar: usuarios enumerados, shares con permisos, versión de SO, política de contraseñas.

   **Otros servicios:**
   - FTP (21): `nmap -sV --script ftp-anon,ftp-bounce <target>`
   - SSH (22): `nmap --script ssh-auth-methods <target>`
   - SMTP (25): `nmap --script smtp-enum-users <target>`

3. Consolidar en findings[]: host, ruta/recurso, estado, notas relevantes.
4. Identificar rutas de ataque: endpoints con parámetros, autenticación débil, shares accesibles, usuarios enumerados.
5. Escribir en session_state: mode="enum", findings actualizados, pending_actions con rutas de ataque identificadas.
6. Sugerir siguiente paso: "/exploit si hay vulnerabilidades identificadas."

## Pitfalls

- gobuster con wordlist grande puede generar tráfico masivo — usar `-t 10` para entornos ruidosos.
- ffuf sin `-fc 404` puede filtrar incorrectamente si el servidor usa códigos custom — ajustar con `-fc <código>`.
- enum4linux puede fallar con SMBv1 deshabilitado; alternativamente usar `smbclient -L //<target>`.
- nikto genera muchos falsos positivos — priorizar hallazgos con OSVDB o CVE referenciados.

## Verification

La fase de enum está completa si:
- session_state.findings[] contiene al menos 1 endpoint, recurso o usuario enumerado con estado documentado.
- session_state.pending_actions[] lista al menos 1 ruta de ataque identificada.
- session_state.mode = "enum".
