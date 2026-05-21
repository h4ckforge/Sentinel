---
name: /checkpoint
description: Persiste el session_state actual en SQLite con timestamp y fase. El agente genera el estado en texto plano — un script externo lo parsea y escribe la base de datos.
version: 0.1
author: h4ckforge
license: MIT
---

## When to Use

Invocar en cualquiera de estos momentos:
- Al completar una fase (recon, enum, exploit, post, report)
- Antes de cerrar la sesión
- Cuando el operador quiere guardar el estado manualmente
- Ante cualquier cambio crítico de contexto (nuevo target, escalación de privilegios, cambio de vector)

## Quick Reference

| Acción | Responsable |
|---|---|
| Generar texto plano con el estado | Agente (este skill) |
| Parsear el texto y escribir SQLite | `scripts/checkpoint.py` |
| Decidir cuándo invocar | Operador o trigger de fase |

## Procedure

1. Leer session_state completo del contexto actual.
2. Generar el siguiente bloque — separador `=`, arrays en JSON inline, delimitado por `END_CHECKPOINT`:

```
CHECKPOINT
session_id=<identificador único de sesión, ej: eng-2026-05-20-acme>
mode=<valor de session_state.mode: recon|enum|exploit|post|report>
target=<valor de session_state.target>
last_tool=<comando literal completo, omitir si no aplica>
user_level=<operator|beginner|expert>
recon_done=<true|false>
phase_complete=<true|false>
active_skill=<nombre de skill activa, omitir si ninguna>
pending_actions=["acción uno", "acción dos"]
explained_concepts=["concepto A", "concepto B"]
findings=[{"host":"10.10.11.42","ports":[{"port":80,"service":"http"}],"notes":"detalle"}]
nota=<resumen de 1 línea del estado actual del engagement>
END_CHECKPOINT
```

3. Indicar al operador: "Estado generado. Ejecutar `python skills/checkpoint/scripts/checkpoint.py` para persistir."

## Pitfalls

- El agente NO escribe JSON directamente. Solo genera el bloque de texto con el formato definido.
- Si session_state.target está vacío, registrar igual con target: "sin definir".
- No inventar valores. Si un campo es incierto, marcarlo como "desconocido".

## Verification

El checkpoint está completo cuando:
- El bloque CHECKPOINT fue generado con todos los campos.
- El operador ejecutó `skills/checkpoint/scripts/checkpoint.py` sin errores.
- La entrada quedó registrada en `sentinel.db` con timestamp y fase correctos.
