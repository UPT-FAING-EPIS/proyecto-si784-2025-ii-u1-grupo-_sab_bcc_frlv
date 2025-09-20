# Documentación del Sistema Anti-Keylogger

Esta carpeta contiene toda la documentación técnica del proyecto.

## Contenido

### 📋 Requerimientos y Análisis
- **[requerimientos.md](requerimientos.md)** - Requerimientos funcionales y no funcionales del sistema
- **[modelo_logico_analisis_objetos.txt](modelo_logico_analisis_objetos.txt)** - Análisis lógico de objetos del dominio

### 🏗️ Arquitectura y Diseño
- **[diagramas.md](diagramas.md)** - Diagramas PlantUML del sistema (casos de uso, clases, secuencia, etc.)
- **[plan_reestructuracion.md](plan_reestructuracion.md)** - Plan detallado de reestructuración del proyecto

### 📖 Documentación Académica
- **[articulo_keylogger.tex](articulo_keylogger.tex)** - Artículo académico en formato LaTeX

## Estructura de Arquitectura

El proyecto sigue **Clean Architecture** con las siguientes capas:

```
src/
├── core/           # Lógica de negocio central
│   ├── domain.py   # Entidades y value objects
│   ├── use_cases.py # Casos de uso de la aplicación
│   └── config.py   # Configuración del sistema
├── adapters/       # Adaptadores a servicios externos
│   ├── feature_extractors.py  # Extracción de características
│   └── ml_adapters.py         # Adaptadores de modelos ML
├── infrastructure/ # Implementaciones de infraestructura
│   └── system_adapters.py     # Logging, alertas, procesos
└── ui/             # Interfaces de usuario
    └── cli.py      # Interfaz de línea de comandos
```

## Diagramas Disponibles

Los diagramas se pueden renderizar con PlantUML:

1. **Diagrama de Paquetes** - Organización modular del sistema
2. **Casos de Uso** - Funcionalidades principales
3. **Diagrama de Secuencia** - Flujo de detección
4. **Diagrama de Clases** - Estructura del dominio
5. **Arquitectura Hexagonal** - Patrón de diseño aplicado
6. **Arquitectura por Capas** - Organización tradicional

## Cómo Usar la Documentación

1. **Para desarrolladores**: Revisar `diagramas.md` y `requerimientos.md`
2. **Para arquitectos**: Consultar `plan_reestructuracion.md` y diagramas de arquitectura
3. **Para investigadores**: Ver `articulo_keylogger.tex` para contexto académico
4. **Para product owners**: Revisar requerimientos funcionales y casos de uso

## Herramientas Recomendadas

- **PlantUML**: Para renderizar diagramas
- **VS Code + PlantUML Extension**: Para editar diagramas
- **LaTeX**: Para compilar el artículo académico
- **Markdown**: Para visualizar documentación