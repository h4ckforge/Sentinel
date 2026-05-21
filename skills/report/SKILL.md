---
name: /report
description: Genera reporte estructurado de hallazgos desde session_state al cierre de fase o sesión.
version: 0.1
author: h4ckforge
license: MIT
---

## When to Use

Al cierre de cualquier fase o de la sesión completa. También invocar si el operador pide documentar hallazgos en cualquier momento. No requiere que todas las fases estén completas.

## Quick Reference

| Sección del reporte | Contenido |
|---|---|
| Resumen ejecutivo | 2-3 líneas: qué se evaluó, acceso obtenido, impacto general |
| Hallazgos por severidad | Crítico / Alto / Medio / Bajo — un bloque por hallazgo |
| Evidencia | Output de herramientas, comandos ejecutados |
| Recomendaciones | Una recomendación accionable por hallazgo |

**Criterios de severidad:**
- Crítico: RCE, credenciales de admin, acceso a DC
- Alto: escalada de privilegios, acceso a datos sensibles, LFI/RFI
- Medio: información expuesta, configuración débil, enumeración de usuarios
- Bajo: banner disclosure, headers de seguridad faltantes, directorios listables

## Procedure

1. Leer session_state.findings[] completo — no solicitar información adicional salvo que findings[] esté vacío.
2. Si findings[] está vacío: "No hay hallazgos documentados en session_state. Ejecutar fases de recon/enum/exploit primero o describir los hallazgos manualmente."
3. Clasificar cada hallazgo por severidad usando los criterios de la tabla anterior.
4. Construir el reporte en este orden:

   **Resumen ejecutivo**
   Target evaluado, fases completadas, resultado de mayor impacto en 2-3 líneas.

   **Hallazgos** (uno por bloque, ordenados de mayor a menor severidad)
   - Título del hallazgo
   - Severidad: [Crítico|Alto|Medio|Bajo]
   - Descripción: qué se encontró y por qué importa
   - Evidencia: output literal de la herramienta o comando que lo confirma
   - Recomendación: acción concreta para remediar

   **Próximos pasos** (si la sesión continúa)
   Listar session_state.pending_actions[] si no está vacío.

5. No modificar session_state.findings[] — esta skill es de solo lectura.

## Pitfalls

- No resumir evidencia con "se obtuvo acceso" sin incluir el output concreto que lo demuestra.
- No mezclar severidades en un mismo bloque — un hallazgo, un bloque.
- No generar recomendaciones genéricas — especificar el parche o configuración exacta cuando sea posible.

## Verification

El reporte es válido si:
- Tiene resumen ejecutivo de 2-3 líneas.
- Tiene al menos 1 hallazgo con: título, severidad, descripción, evidencia, recomendación.
- session_state.findings[] no fue modificado.
