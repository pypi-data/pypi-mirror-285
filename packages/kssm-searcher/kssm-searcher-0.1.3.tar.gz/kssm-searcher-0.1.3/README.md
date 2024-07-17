# Searcher

Herramienta para extraer informacion de documentos localizados en un directorio en base a keywords.

Util para auditorias en las que encontramos un share que nos decargamos mediante netexec o smbclient, y queremos procesar toda la info lo mas rapido posible

## Instalacion

Necesita `catdoc` instalado:

```bash
sudo apt install catdoc
```

Con esto valdria con lanzar:

```bash
pip install kssm-searcher
```

### Requisitos

Se instalan automaticamente

Para los requisitos externos necesita:
- `textract`
- `PyPDF2` < lo mismo podria cambiarlo a textract
- `zipfile` < cuando los encuentra, extrae los contenidos y realiza la busqueda tambien dentro de ellos

## Uso basico

```bash
kssm-searcher -p /path/to/search
```

## Uso Avanzado

Tenemos varios argumentos con los que podemos modificar su comportamiento

- `-k`: cambia los keywords a buscar. Por defecto es "passwd". Mucho cuidao con cambiar esto que como metamos palabras genericas genera muchisimo ruido
- ...

# Extensiones Validas

- bat
- cmd
- csv
- doc
- docx
- html
- json
- pdf
- ps1
- py
- sh
- txt
- xls
- xlsx
- xml
- zip

# TODO

- [ ] Completar funcionalidad de ZIP
- [ ] Añadir mas extensiones validas