---
name: handoff
description: Genera un documento de handoff para continuar el trabajo en una nueva sesión de Claude. Usar cuando se necesite cerrar la sesión actual y mantener continuidad.
version: 1.0
author: QH4X / h4ckforge
---

# Handoff Skill

## When to Use
- Antes de cerrar una sesión larga
- Cuando el contexto está cerca del límite
- Para transferir trabajo entre Claude Chat y Claude Code
- Para documentar el estado actual del proyecto

## IMPORTANTE
Antes de ejecutar, presentar al operador:
1. Lo que entendiste que se hizo en esta sesión
2. Los próximos pasos propuestos
3. Esperar aprobación antes de escribir el handoff

## Procedure

### 1. Analizar la sesión
- ¿Qué se hizo?
- ¿Qué decisiones se tomaron?
- ¿Qué quedó pendiente?

### 2. Escribir el handoff
Guardar en la ruta que indique el operador, o por defecto en el directorio actual del proyecto.

```
[ruta-del-proyecto]\handoff.md
```

### 3. Formato del handoff

```markdown
# Handoff — [título breve]
[fecha y hora]

## Contexto
[Qué estábamos haciendo. 2-3 frases máximo.]

## Decisiones clave
[Decisiones tomadas, constraints descubiertos, arquitectura definida]

## Estado actual
[Qué existe, qué está a medias, qué falta]

## Próximos pasos
1. [Primero]
2. [Segundo]
3. [Tercero]

## Archivos relevantes
- `[ruta\archivo1]`
- `[ruta\archivo2]`

## Instrucción para el agente receptor
No asumir contexto previo. Leer este documento completo.
Presentar al operador lo que entendiste y los próximos pasos propuestos.
Esperar aprobación antes de ejecutar cualquier cosa.
```

## Key Rules
- Sin contexto asumido — el agente receptor parte de cero
- Rutas completas — no referencias relativas
- Conciso — suficiente para continuar, no una novela
- Siempre esperar aprobación antes de ejecutar
