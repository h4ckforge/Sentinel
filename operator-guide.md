# operator-guide.md — Guía de construcción para el operador
# Esta documentación es para Rodrigo, no para el modelo.
# No forma parte de sentinel_soul.md.

---

## Filosofía de la wiki Obsidian — recetario, no biblioteca

```
INCORRECTO:
  — Subir el manual de nmap completo al RAG
  — Wikificar libros capítulo por capítulo
  — Resúmenes de teoría general sin contexto operacional
  — 10.000 documentos genéricos en el vector store

CORRECTO:
  — Recetas por situación: "Cuando encuentres SMB abierto, probá estos 3 comandos en este orden"
  — Casos de uso: "Cómo montar C2 con Empire en 5 pasos"
  — Writeups de CTF como pares pregunta-respuesta
  — 500 ejemplos buenos > 50.000 generados automáticamente
  — Chunks relevantes, no la biblioteca completa
```

---

## Estructura recomendada de la wiki

```
/Sentinel-Wiki
  /recetas
    smb-enumeration.md
    kerberoasting.md
    privesc-linux.md
    privesc-windows.md
    lateral-movement.md
  /herramientas
    nmap-casos-de-uso.md
    impacket-cheatsheet.md
    bloodhound-edges.md
    burp-tecnicas.md
    mimikatz-comandos.md
  /cves
    CVE-XXXX-YYYY.md        ← un archivo por CVE relevante
  /ctf-writeups
    htb-[nombre-maquina].md
    thm-[nombre-room].md
```

**Formato de cada nota:**
```
# [Situación o herramienta]
## Cuándo usar esto
## Comandos
## Output esperado
## Siguientes pasos
## Gotchas
```
