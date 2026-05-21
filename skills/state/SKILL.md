---
name: /state
description: Muestra snapshot completo del session_state actual en formato tabla.
version: 0.1
author: h4ckforge
license: MIT
---

## When to Use

Cuando el operador quiere ver el estado actual de la sesión: fase en curso, target, hallazgos acumulados, acciones pendientes. También invocar si hay confusión sobre en qué punto del engagement se encuentra la sesión.

## Quick Reference

| Campo | Descripción |
|---|---|
| mode | Fase activa actual |
| target | Objetivo del engagement |
| last_tool | Última herramienta ejecutada |
| recon_done | Si la fase de recon fue completada |
| active_skill | Skill activa en este momento |
| phase_complete | Si la fase actual fue completada |
| findings count | Número de entradas en findings[] |
| pending_actions | Lista de acciones pendientes |

## Procedure

1. Leer session_state completo — no modificar ningún campo.
2. Presentar todos los campos en tabla con dos columnas: Campo | Valor.
3. Para findings[]: mostrar solo el count y un resumen de 1 línea por entrada (host + primer puerto o recurso).
4. Para pending_actions[]: listar cada item como fila separada en la tabla.
5. Si session_state está vacío, mostrar todos los campos con valor "no definido".
6. Agregar al final: "Siguiente acción sugerida:" basada en el estado:
   - recon_done = false y target tiene valor → "/recon"
   - recon_done = true y findings[] tiene hosts pero no vulnerabilidades → "/enum"
   - findings[] tiene vulnerabilidades → "/exploit"
   - phase_complete = true en exploit → "/post"
   - pending_actions[] tiene items → listar el primero

## Pitfalls

- No modificar session_state — esta skill es estrictamente de solo lectura.
- No omitir campos aunque tengan valor null o false — mostrar todos.
- No expandir findings[] completo — el snapshot debe ser legible en pantalla.

## Verification

El output de /state es válido si:
- La tabla incluye todos los campos del schema canónico (definido en recon/SKILL.md).
- Cada campo muestra su valor actual (o "no definido" si no está inicializado).
- session_state no fue modificado.
- La respuesta incluye "Siguiente acción sugerida:" al final.
