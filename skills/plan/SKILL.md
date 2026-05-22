---
name: /plan
description: Genera un plan de ataque estructurado por fases antes de ejecutar cualquier herramienta.
version: 0.1
author: h4ckforge
license: MIT
---

## When to Use

Invocar cuando no existe un objetivo definido en session_state o cuando el operador quiere estructurar el engagement antes de correr herramientas. También invocar si pending_actions está vacío al inicio de una sesión.

## Quick Reference

| Input requerido | Output producido |
|---|---|
| target (IP/dominio/app) | Plan con 6 fases |
| scope (in-scope/out-of-scope) | Objetivos por fase |
| tipo de engagement (red team / pentest / CTF) | Herramientas sugeridas por fase |
| | Criterios de completitud por fase |

## Procedure

1. Verificar session_state. Si target está vacío, preguntar: "Target y scope del engagement?"
2. Si tipo de engagement no fue especificado, preguntar: "Red team, pentest externo, o CTF?"
3. Construir plan con exactamente estas fases en orden:
   - **Recon**: objetivos pasivos y activos, criterio = al menos 1 host con puertos documentados
   - **Enum**: profundización por servicio, criterio = endpoints/recursos mapeados con estado
   - **Threat Modeling (STRIDE)**: según hallazgos de recon/enum, identificar y clasificar vectores probables, criterio = lista de vectores priorizados declarada
   - **Exploit**: validación de vulnerabilidades, criterio = shell obtenida o CVE confirmado con evidencia
   - **Post-explotación** (condicional — solo si el scope lo incluye): escalada y movimiento lateral, criterio = privilegios escalados o credenciales adicionales
   - **Report**: documentación de hallazgos, criterio = reporte con severidades y recomendaciones
4. Para cada fase incluir: objetivo, herramientas sugeridas, criterio de completitud, dependencia de fase anterior.
5. Escribir en session_state: mode="plan", target con valor, pending_actions con las fases en orden.
6. Presentar el plan como lista estructurada, no como párrafo.

## Pitfalls

- No generar el plan sin conocer el scope — un plan sin scope produce acciones fuera de objetivo.
- No omitir criterios de completitud — sin ellos el operador no sabe cuándo avanzar de fase.
- No sugerir herramientas que requieran compilación o instalación compleja; priorizar las que vienen en Kali.

## Verification

El plan generado cumple si:
- Tiene exactamente 6 fases nombradas (post-explotación condicional al scope).
- Cada fase tiene al menos: objetivo, 1+ herramienta sugerida, criterio de completitud.
- session_state.mode = "plan", session_state.target tiene valor, session_state.pending_actions lista las fases en orden.
