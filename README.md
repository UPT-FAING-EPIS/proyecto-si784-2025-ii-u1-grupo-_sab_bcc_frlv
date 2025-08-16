# 📌 Sistema de Gestión de Asistencias

![Flutter](https://img.shields.io/badge/Flutter-v3.22-blue?logo=flutter)
![Firebase](https://img.shields.io/badge/Firebase-Auth%20%26%20Firestore-orange?logo=firebase)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-En%20desarrollo-yellow)

---

## 📖 Descripción
El **Sistema de Gestión de Asistencias** es una aplicación móvil multiplataforma desarrollada en **Flutter**, con backend en **Firebase**, que permite registrar y consultar asistencias de manera segura y eficiente mediante escaneo de códigos QR.

---

## 📝 Tabla de Contenidos
1. [Problema](#-problema)
2. [Objetivos](#-objetivos)
3. [Autores](#-autores)
4. [Licencia](#-licencia)

---

## 🚨 Problema
Actualmente, muchas instituciones necesitan un sistema eficiente para el registro y seguimiento de asistencias que incluya:
- Autenticación segura de usuarios con diferentes roles.
- Registro y administración de estudiantes.
- Control de acceso mediante credenciales únicas.
- Interfaz intuitiva y responsiva.
- Gestión integral de perfiles de usuario.

---

## 🎯 Objetivos

### Objetivo Principal
> Desarrollar una aplicación móvil que permita gestionar el registro de asistencias de forma eficiente, segura y accesible desde múltiples dispositivos.

### Objetivos Específicos
| Área                     | Objetivos |
|--------------------------|-----------|
| **Autenticación y Seguridad** | - Inicio de sesión seguro con Firebase Authentication.<br>- Roles diferenciados (estudiantes y administradores).<br>- Recuperación de contraseña vía email o app. |
| **Gestión de Usuarios** | - Registro y actualización de estudiantes.<br>- Administración de perfiles.<br>- Control y asignación de credenciales. |
| **Funcionalidad de Asistencias** | - Escaneo de código QR.<br>- Historial de asistencias filtrable.<br>- Reportes exportables. |
| **Experiencia de Usuario** | - Interfaz siguiendo Material Design 3.<br>- Diseño responsivo.<br>- Retroalimentación visual y auditiva. |

---

## 🛠 Tecnologías

| Tecnología | Descripción |
|------------|-------------|
| **Flutter** | Framework para desarrollo multiplataforma. |
| **Firebase Authentication** | Gestión de usuarios y roles. |
| **Firebase Firestore** | Base de datos en tiempo real. |
| **Material Design 3** | Guías de diseño modernas. |

---

## 📦 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/usuario/sistema-asistencias.git

# Entrar al directorio
cd sistema-asistencias

# Instalar dependencias
flutter pub get

# Ejecutar el proyecto
flutter run
