# Diagramas del Proyecto Anti-Keylogger

## Diagrama de Paquetes

```plantuml
@startuml

package "Anti-Keylogger System" {
    
    package "Core" {
        package "ML" {
            class ModelManager
            class FeatureExtractor
            class Predictor
        }
        
        package "Monitor" {
            class FileMonitor
            class ProcessMonitor
            class Scanner
        }
        
        package "Detection" {
            class ThreatDetector
            class AlertManager
            class Quarantine
        }
    }
    
    package "Infrastructure" {
        package "Data" {
            class LogManager
            class ConfigManager
            class DataStorage
        }
        
        package "Utils" {
            class FileUtils
            class SystemUtils
            class SecurityUtils
        }
    }
    
    package "Interfaces" {
        package "CLI" {
            class ConsoleInterface
            class MenuManager
        }
        
        package "API" {
            class ScanAPI
            class ConfigAPI
        }
    }
    
    package "External" {
        package "Models" {
            note "Modelos .pkl/.onnx\nMetadata JSON" as ModelFiles
        }
        
        package "Logs" {
            note "monitor_log.txt\nmonitor_alerts.txt" as LogFiles
        }
    }
}

Core ..> Infrastructure : uses
Interfaces ..> Core : controls
External <.. Infrastructure : manages
@enduml
```

## Diagrama de Casos de Uso

```plantuml
@startuml

left to right direction

actor "Usuario" as User
actor "Administrador" as Admin
actor "Sistema" as System

rectangle "Anti-Keylogger System" {
    
    ' Casos de uso principales
    usecase "Realizar Escaneo Total" as UC1
    usecase "Realizar Escaneo Específico" as UC2
    usecase "Realizar Escaneo Local" as UC3
    usecase "Detectar Keylogger" as UC4
    usecase "Generar Alerta" as UC5
    usecase "Poner en Cuarentena" as UC6
    usecase "Eliminar Archivo" as UC7
    usecase "Generar Logs" as UC8
    
    ' Casos de uso de configuración
    usecase "Configurar Parámetros" as UC9
    usecase "Seleccionar Modelo ML" as UC10
    usecase "Ver Historial" as UC11
    usecase "Exportar Reportes" as UC12
    
    ' Casos de uso del sistema
    usecase "Monitorear Procesos" as UC13
    usecase "Extraer Features" as UC14
    usecase "Ejecutar Predicción" as UC15
}

' Relaciones Usuario
User --> UC1
User --> UC2
User --> UC3
User --> UC6
User --> UC7
User --> UC11

' Relaciones Administrador
Admin --> UC9
Admin --> UC10
Admin --> UC12

' Relaciones Sistema
System --> UC4
System --> UC5
System --> UC8
System --> UC13
System --> UC14
System --> UC15

' Extensiones e inclusiones
UC1 ..> UC4 : <<include>>
UC2 ..> UC4 : <<include>>
UC3 ..> UC4 : <<include>>
UC4 ..> UC5 : <<extend>>
UC4 ..> UC14 : <<include>>
UC14 ..> UC15 : <<include>>
UC5 ..> UC8 : <<include>>

@enduml
```

## Diagrama Secuencial

```plantuml
@startuml

actor Usuario
participant "ConsoleInterface" as UI
participant "Scanner" as Scan
participant "FileMonitor" as FM
participant "FeatureExtractor" as FE
participant "Predictor" as Pred
participant "ThreatDetector" as TD
participant "AlertManager" as AM
participant "LogManager" as LM

Usuario -> UI: Seleccionar tipo de escaneo
activate UI

UI -> Scan: iniciar_escaneo(tipo, ruta)
activate Scan

alt Escaneo Total
    Scan -> FM: escanear_sistema_completo()
    activate FM
    FM -> FM: obtener_archivos_y_procesos()
    FM --> Scan: lista_elementos
    deactivate FM
else Escaneo Específico
    Scan -> FM: escanear_carpeta(ruta)
    activate FM
    FM --> Scan: lista_archivos
    deactivate FM
else Escaneo Local
    Scan -> FM: analizar_archivo(archivo)
    activate FM
    FM --> Scan: archivo_info
    deactivate FM
end

loop Para cada elemento
    Scan -> FE: extraer_features(elemento)
    activate FE
    FE -> FE: calcular_entropy()
    FE -> FE: obtener_metadata()
    FE -> FE: analizar_imports()
    FE --> Scan: features
    deactivate FE
    
    Scan -> Pred: predecir(features)
    activate Pred
    Pred -> Pred: cargar_modelo()
    Pred -> Pred: ejecutar_inference()
    Pred --> Scan: resultado_prediccion
    deactivate Pred
    
    Scan -> TD: evaluar_amenaza(resultado)
    activate TD
    
    alt Es Keylogger
        TD -> AM: generar_alerta(elemento, threat_info)
        activate AM
        AM -> LM: log_alerta(details)
        activate LM
        LM --> AM: logged
        deactivate LM
        AM -> UI: mostrar_alerta()
        AM --> TD: alerta_generada
        deactivate AM
        
        TD -> Scan: detener_escaneo()
        
        UI -> Usuario: ¿Qué acción tomar?
        Usuario -> UI: Seleccionar acción
        
        alt Cuarentena
            UI -> Scan: poner_en_cuarentena(archivo)
        else Eliminar
            UI -> Scan: eliminar_archivo(archivo)
        else Re-escanear
            UI -> Scan: re_analizar(archivo)
        end
        
    else Es Benigno
        TD -> LM: log_evento(elemento, "benigno")
        activate LM
        LM --> TD: logged
        deactivate LM
    end
    
    TD --> Scan: resultado_evaluacion
    deactivate TD
end

Scan --> UI: escaneo_completado
deactivate Scan

UI --> Usuario: Mostrar resultados
deactivate UI

@enduml
```

## Diagrama de Clases

```plantuml
@startuml

' Clases principales del núcleo
class Scanner {
    -scan_type: ScanType
    -target_path: String
    -is_running: Boolean
    +iniciar_escaneo(tipo: ScanType, ruta: String): void
    +detener_escaneo(): void
    +obtener_progreso(): Integer
}

class FileMonitor {
    -monitored_paths: List<String>
    +escanear_sistema_completo(): List<FileInfo>
    +escanear_carpeta(ruta: String): List<FileInfo>
    +analizar_archivo(archivo: String): FileInfo
    +obtener_procesos_activos(): List<ProcessInfo>
}

class FeatureExtractor {
    -feature_config: FeatureConfig
    +extraer_features(elemento: FileInfo): Features
    +calcular_entropy(data: Bytes): Float
    +obtener_metadata(archivo: String): Metadata
    +analizar_imports(ejecutable: String): List<String>
}

class Predictor {
    -model_path: String
    -model_type: ModelType
    -model: MLModel
    +cargar_modelo(ruta: String): void
    +predecir(features: Features): PredictionResult
    +validar_modelo(): Boolean
}

class ThreatDetector {
    -threshold: Float
    -detection_rules: List<Rule>
    +evaluar_amenaza(resultado: PredictionResult): ThreatLevel
    +es_keylogger(probabilidad: Float): Boolean
    +generar_threat_info(elemento: FileInfo): ThreatInfo
}

class AlertManager {
    -alert_config: AlertConfig
    +generar_alerta(elemento: FileInfo, info: ThreatInfo): void
    +mostrar_alerta_consola(mensaje: String): void
    +enviar_notificacion(alerta: Alert): void
}

class LogManager {
    -log_path: String
    -alert_log_path: String
    +log_evento(evento: String): void
    +log_alerta(alerta: Alert): void
    +rotar_logs(): void
    +exportar_reporte(): String
}

class ConfigManager {
    -config_file: String
    -settings: Map<String, Object>
    +cargar_configuracion(): void
    +obtener_valor(clave: String): Object
    +actualizar_configuracion(clave: String, valor: Object): void
    +guardar_configuracion(): void
}

class ConsoleInterface {
    -menu_principal: Menu
    -scanner: Scanner
    +mostrar_menu(): void
    +procesar_seleccion(opcion: Integer): void
    +solicitar_ruta(): String
    +mostrar_progreso(progreso: Integer): void
}

' Clases de datos
class FileInfo {
    +path: String
    +size: Long
    +extension: String
    +creation_date: DateTime
    +is_executable: Boolean
}

class Features {
    +file_size: Long
    +entropy: Float
    +num_sections: Integer
    +has_imports: Boolean
    +is_document: Boolean
    +is_executable: Boolean
}

class PredictionResult {
    +label: String
    +probability: Float
    +confidence: Float
    +model_version: String
}

class ThreatInfo {
    +threat_type: String
    +severity: ThreatLevel
    +description: String
    +recommended_action: String
}

' Enumeraciones
enum ScanType {
    TOTAL
    SPECIFIC
    LOCAL
}

enum ModelType {
    PKL
    ONNX
}

enum ThreatLevel {
    LOW
    MEDIUM
    HIGH
    CRITICAL
}

' Relaciones
Scanner --> FileMonitor : uses
Scanner --> FeatureExtractor : uses
Scanner --> Predictor : uses
Scanner --> ThreatDetector : uses
Scanner --> AlertManager : uses
Scanner --> LogManager : uses

ConsoleInterface --> Scanner : controls
ConfigManager --> Scanner : configures

FileMonitor ..> FileInfo : creates
FeatureExtractor ..> Features : creates
Predictor ..> PredictionResult : creates
ThreatDetector ..> ThreatInfo : creates

ThreatDetector --> AlertManager : notifies
AlertManager --> LogManager : logs

@enduml
```

## Diagrama de Arquitectura - Arquitectura por Capas

```plantuml
@startuml

!define RECTANGLE class

rectangle "CAPA DE PRESENTACIÓN" #lightblue {
    RECTANGLE "Console Interface" as UI {
        - Menu Principal
        - Gestión de Input/Output
        - Visualización de Progreso
        - Manejo de Alertas
    }
    
    RECTANGLE "API Interface" as API {
        - REST Endpoints
        - Validación de Requests
        - Serialización de Responses
    }
}

rectangle "CAPA DE LÓGICA DE NEGOCIO" #lightgreen {
    RECTANGLE "Scan Controller" as SC {
        - Orquestación de Escaneos
        - Validación de Parámetros
        - Control de Flujo
    }
    
    RECTANGLE "Detection Engine" as DE {
        - Lógica de Detección
        - Evaluación de Amenazas
        - Gestión de Alertas
    }
    
    RECTANGLE "Configuration Manager" as CM {
        - Gestión de Configuraciones
        - Validación de Parámetros
        - Políticas de Seguridad
    }
}

rectangle "CAPA DE SERVICIOS" #lightyellow {
    RECTANGLE "ML Service" as MLS {
        - Feature Extraction
        - Model Loading
        - Prediction Execution
        - Model Validation
    }
    
    RECTANGLE "File Service" as FS {
        - File System Access
        - Process Monitoring
        - Metadata Extraction
        - File Operations
    }
    
    RECTANGLE "Security Service" as SS {
        - Quarantine Management
        - File Deletion
        - Access Control
        - Encryption
    }
}

rectangle "CAPA DE PERSISTENCIA" #lightcoral {
    RECTANGLE "Log Repository" as LR {
        - Event Logging
        - Alert Storage
        - Log Rotation
        - Report Generation
    }
    
    RECTANGLE "Model Repository" as MR {
        - Model Storage
        - Metadata Management
        - Version Control
        - Model Caching
    }
    
    RECTANGLE "Config Repository" as CR {
        - Configuration Storage
        - Settings Persistence
        - Backup Management
    }
}

rectangle "CAPA DE DATOS" #lightgray {
    RECTANGLE "File System" as FileSystem
    RECTANGLE "ML Models (.pkl/.onnx)" as Models
    RECTANGLE "Log Files" as Logs
    RECTANGLE "Configuration Files" as Configs
}

' Relaciones entre capas
UI --> SC
API --> SC
UI --> DE
API --> DE

SC --> MLS
SC --> FS
DE --> MLS
DE --> SS
CM --> CR

MLS --> MR
FS --> FileSystem
SS --> FileSystem
LR --> Logs
MR --> Models
CR --> Configs

DE --> LR

note right of UI : "Interfaz de usuario\npara interacción directa"
note right of API : "API REST para\nintegración externa"
note left of MLS : "Servicios de Machine\nLearning especializados"
note left of FS : "Servicios de acceso\nal sistema de archivos"

@enduml
```

## Diagrama de Arquitectura - Arquitectura Hexagonal (Ports & Adapters)

```plantuml
@startuml
!allowmixing

skinparam rectangle {
    BackgroundColor<<core>> lightgreen
    BackgroundColor<<adapter>> lightblue
    BackgroundColor<<port>> lightyellow
}

rectangle "DOMINIO CENTRAL" <<core>> {
    rectangle "Anti-Keylogger Core" as Core {
        note "ScanService\nDetectionService\nMLService\nSecurityService" as CoreServices
    }
}

' Puertos (Interfaces)
rectangle "PUERTOS DE ENTRADA" <<port>> {
    interface IScanPort
    interface IConfigPort
    interface IAlertPort
}

rectangle "PUERTOS DE SALIDA" <<port>> {
    interface IFileSystemPort
    interface IMLModelPort
    interface ILogPort
    interface ISecurityPort
}

' Adaptadores de Entrada
rectangle "ADAPTADORES DE ENTRADA" <<adapter>> {
    rectangle "Console Adapter" as ConsoleAdapter
    rectangle "API Adapter" as APIAdapter
    rectangle "Scheduler Adapter" as SchedulerAdapter
}

' Adaptadores de Salida
rectangle "ADAPTADORES DE SALIDA" <<adapter>> {
    rectangle "File System Adapter" as FSAdapter
    rectangle "Scikit-Learn Adapter" as SKAdapter
    rectangle "ONNX Adapter" as ONNXAdapter
    rectangle "Text Log Adapter" as LogAdapter
    rectangle "Quarantine Adapter" as QuarantineAdapter
}

' Sistemas Externos
rectangle "SISTEMAS EXTERNOS" {
    database "File System" as FS
    database "ML Models" as Models
    database "Log Files" as LogFiles
    cloud "External APIs" as ExtAPI
}

' Relaciones
ConsoleAdapter ..> IScanPort
APIAdapter ..> IScanPort
SchedulerAdapter ..> IScanPort

ConsoleAdapter ..> IConfigPort
APIAdapter ..> IConfigPort

Core ..> IAlertPort

IScanPort <.. Core
IConfigPort <.. Core
IAlertPort <.. Core

Core ..> IFileSystemPort
Core ..> IMLModelPort
Core ..> ILogPort
Core ..> ISecurityPort

IFileSystemPort <.. FSAdapter
IMLModelPort <.. SKAdapter
IMLModelPort <.. ONNXAdapter
ILogPort <.. LogAdapter
ISecurityPort <.. QuarantineAdapter

FSAdapter --> FS
SKAdapter --> Models
ONNXAdapter --> Models
LogAdapter --> LogFiles
QuarantineAdapter --> FS

note top of Core : "Lógica de negocio\npura, independiente\nde tecnologías externas"

note bottom of ConsoleAdapter : "Interfaz de línea\nde comandos"

note bottom of FSAdapter : "Acceso directo al\nsistema de archivos"

@enduml
```

---

## Recomendación de Arquitectura

Para este proyecto, recomiendo la **Arquitectura por Capas** por las siguientes razones:

1. **Simplicidad:** Más fácil de entender e implementar para un prototipo
2. **Separación clara:** Cada capa tiene responsabilidades bien definidas
3. **Escalabilidad:** Permite agregar funcionalidades de forma ordenada
4. **Mantenibilidad:** Facilita la localización y corrección de errores
5. **Testabilidad:** Cada capa puede probarse independientemente

La Arquitectura Hexagonal sería ideal para versiones futuras cuando se requiera mayor flexibilidad de integración.