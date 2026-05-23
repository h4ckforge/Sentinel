---
name: /recon
description: Ejecuta reconocimiento pasivo y activo para mapear la superficie de ataque del objetivo.
version: 0.1
author: h4ckforge
license: MIT
---

## When to Use

Primera fase de todo engagement. Si cualquier otra skill se invoca con session_state.recon_done = false, advertir una vez: "Recon no completado — ¿confirmás saltar esta fase?" y esperar respuesta antes de continuar. Si confirma, continuar sin advertir de nuevo en esa sesión.

## Quick Reference

| Herramienta | Uso |
|---|---|
| theHarvester | OSINT pasivo: emails, subdominios, IPs desde fuentes públicas |
| dnsenum | Enumeración DNS: zonas, subdominios, MX, NS |
| nmap -sV -sC | Escaneo activo: versiones de servicio + scripts por defecto |
| amass enum -passive | Descubrimiento de subdominios sin contactar el objetivo |

## Session State — Schema Canónico

Este es el schema de referencia para todas las skills de Hermes. Todas las demás skills lo extienden o leen pero no lo redefinen.

```json
{
  "mode": "recon|enum|threat_modeling|exploit|post|report",
  "target": "IP/dominio/aplicación",
  "last_tool": "herramienta anterior",
  "user_level": "operator",
  "recon_done": false,
  "explained_concepts": [],
  "pending_actions": [],
  "active_skill": "",
  "phase_complete": false,
  "findings": [],
  "checklist_progress": {
    "fase_activa": "",
    "items_completados": [],
    "items_pendientes": [],
    "hallazgos_por_item": {}
  }
}
```

Cada entrada en findings[] sigue esta estructura mínima:
```json
{
  "host": "IP o hostname",
  "ports": [{"port": 80, "service": "http", "version": "Apache 2.4"}],
  "notes": "string libre"
}
```

## Procedure

1. Verificar session_state.target. Si está vacío, preguntar: "Target y scope para recon?"
2. Confirmar scope: qué IPs, dominios o rangos están in-scope.
3. **OSINT pasivo** (sin contactar el objetivo directamente):
   - `theHarvester -d <dominio> -b all` — recolectar emails, subdominios, IPs.
   - `amass enum -passive -d <dominio>` — subdominios adicionales.
   - `dnsenum <dominio>` — registros DNS completos.
4. **Pipeline paralelo** — lanzar simultáneamente, no esperar a que termine uno para iniciar el otro:
   - **Terminal 1 (background):** `nmap -sC -sV -p- --open <target> -v -oN recon_<target>.txt`
   - **Terminal 2 (inmediato):** `whatweb <target>` — fingerprinting web mientras nmap corre
   - **Terminal 2 (continuar):** si se identifica stack web → `whatweb <target>:<port>` para puertos alternativos
   - No esperar a nmap para comenzar con whatweb. Ningún turno de espera sin otra tarea activa.
5. **Análisis de resultados parciales** — a medida que llegan:
   - Si nmap revela 139/445: aplicar enumeración SMB anónima antes de continuar (ver /enum)
   - Si nmap revela 25: enumerar usuarios SMTP antes de continuar
   - Si whatweb identifica tecnología: registrar en findings[] inmediatamente
6. Consolidar resultados: listar hosts descubiertos, puertos abiertos por host, servicios con versión.
7. Escribir en session_state: mode="recon", target, recon_done=true al completar, findings con hosts/puertos/servicios.
8. Sugerir siguiente paso: "/enum para profundizar en servicios identificados."

## Pitfalls

- No correr escaneo activo antes de confirmar autorización.
- nmap sin -oN pierde el output; siempre guardar a archivo.
- theHarvester con `-b all` puede ser lento; si el operador quiere rapidez, usar `-b google,bing`.
- dnsenum puede fallar en dominios con DNSSEC agresivo — registrar el error en findings[].notes.

## Verification

La fase de recon está completa si:
- session_state.recon_done = true.
- session_state.findings[] contiene al menos 1 host con al menos 1 puerto abierto documentado con servicio.
- session_state.mode = "recon".
