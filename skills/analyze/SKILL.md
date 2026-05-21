---
name: /analyze
description: Interpreta output de herramientas de seguridad y produce resumen accionable con siguiente paso concreto.
version: 0.1
author: h4ckforge
license: MIT
---

## When to Use

Cuando el operador pega output de cualquier herramienta (nmap, gobuster, enum4linux, mimikatz, linpeas, msfconsole, o cualquier otra) y quiere interpretación. También invocar si el operador dice "qué significa esto" o "analizá esto" seguido de output.

## Quick Reference

| Estructura de respuesta | Tamaño |
|---|---|
| Bloque de resumen | 2-4 frases |
| Detalle por item relevante | 1 párrafo o lista por item |
| Siguiente paso concreto | 1 acción específica |

## Procedure

1. Identificar la herramienta que generó el output (si no es evidente, inferir del formato o preguntar).
2. **SIEMPRE comenzar con bloque de resumen** — 2-4 frases: qué herramienta corrió, qué encontró de relevancia, impacto potencial. No comenzar con detalle ni con listas.
3. Detalle por item relevante:
   - nmap: listar puertos abiertos con servicio/versión, marcar puertos de alto interés (21, 22, 80, 443, 445, 1433, 3306, 3389, 5985).
   - gobuster/ffuf: listar endpoints con código 200 o 301 primero; ignorar 404.
   - enum4linux: destacar usuarios enumerados, shares accesibles, información de dominio.
   - linpeas: destacar items críticos o de alto interés, vectores SUID y sudo.
   - mimikatz/secretsdump: listar credenciales y hashes con usuario y tipo.
   - Output genérico: identificar las 3-5 líneas de mayor relevancia operacional.
4. Cerrar con "Siguiente paso:" seguido de 1 acción específica y el comando o skill a ejecutar.
5. Escribir session_state.pending_actions[] con los siguientes pasos inferidos.

## Pitfalls

- No comenzar la respuesta con detalle — el bloque de resumen es obligatorio primero.
- No analizar output línea por línea — agrupar por relevancia, no por orden de aparición.
- No inventar vulnerabilidades que el output no confirma — distinguir "confirmado" de "indicativo de".
- Si el output está truncado, indicarlo: "El output parece incompleto — algunos hallazgos podrían faltar."

## Verification

La respuesta de /analyze es válida si:
- La primera sección es el bloque de resumen (2-4 frases) antes de cualquier lista o detalle.
- session_state.pending_actions[] fue actualizado con los pasos inferidos.
- La respuesta termina con un siguiente paso concreto.
