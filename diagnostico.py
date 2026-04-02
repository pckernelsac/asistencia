#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para el servidor cPanel
Ejecutar en el servidor para verificar configuración
"""

import sys
import os

def main():
    print("=" * 80)
    print("DIAGNÓSTICO DE SERVIDOR - Sistema de Asistencia")
    print("=" * 80)
    print()

    # 1. Información de Python
    print("🐍 PYTHON:")
    print("-" * 80)
    print(f"Versión: {sys.version}")
    print(f"Ejecutable: {sys.executable}")
    print(f"Directorio actual: {os.getcwd()}")
    print()

    # 2. Verificar archivos necesarios
    print("📄 ARCHIVOS NECESARIOS:")
    print("-" * 80)
    archivos = [
        "passenger_wsgi.py",
        "app.py",
        ".htaccess",
        "requirements.txt",
        ".env"
    ]

    for archivo in archivos:
        existe = "✓" if os.path.exists(archivo) else "✗"
        print(f"{existe} {archivo}")
    print()

    # 3. Verificar directorios
    print("📁 DIRECTORIOS:")
    print("-" * 80)
    directorios = [
        "templates",
        "static",
        "static/uploads",
        "instance",
        "tmp"
    ]

    for directorio in directorios:
        existe = "✓" if os.path.isdir(directorio) else "✗"
        print(f"{existe} {directorio}")
    print()

    # 4. Intentar importar la aplicación
    print("🔧 IMPORTACIÓN DE APLICACIÓN:")
    print("-" * 80)
    try:
        from app import app
        print("✓ Aplicación importada correctamente")
        print(f"✓ Secret Key configurada: {bool(app.secret_key)}")
        print(f"✓ Upload folder: {app.config.get('UPLOAD_FOLDER')}")
        print(f"✓ Debug mode: {app.debug}")
    except Exception as e:
        print(f"✗ Error al importar aplicación: {str(e)}")
        import traceback
        traceback.print_exc()
    print()

    # 5. Verificar módulos instalados
    print("📦 MÓDULOS INSTALADOS:")
    print("-" * 80)
    modulos_requeridos = [
        "flask",
        "openpyxl",
        "qrcode",
        "PIL",
        "werkzeug"
    ]

    for modulo in modulos_requeridos:
        try:
            __import__(modulo)
            print(f"✓ {modulo}")
        except ImportError:
            print(f"✗ {modulo} - NO INSTALADO")
    print()

    # 6. Verificar base de datos
    print("🗄️  BASE DE DATOS:")
    print("-" * 80)
    if os.path.exists("instance/asistencia.db"):
        import sqlite3
        try:
            conn = sqlite3.connect("instance/asistencia.db")
            cursor = conn.cursor()

            # Verificar tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tablas = [row[0] for row in cursor.fetchall()]
            print(f"✓ Base de datos existe")
            print(f"✓ Tablas: {', '.join(tablas)}")

            # Verificar WAL mode
            cursor.execute("PRAGMA journal_mode")
            modo = cursor.fetchone()[0]
            print(f"✓ Journal mode: {modo}")

            conn.close()
        except Exception as e:
            print(f"✗ Error al verificar base de datos: {str(e)}")
    else:
        print("⚠ Base de datos no existe (se creará al iniciar la aplicación)")
    print()

    # 7. Verificar permisos
    print("🔐 PERMISOS:")
    print("-" * 80)
    archivos_permisos = [
        ("passenger_wsgi.py", 0o755),
        ("app.py", 0o755),
        (".htaccess", 0o644),
    ]

    for archivo, perm_esperado in archivos_permisos:
        if os.path.exists(archivo):
            perm_actual = oct(os.stat(archivo).st_mode)[-3:]
            perm_esperado_str = oct(perm_esperado)[-3:]
            if perm_actual == perm_esperado_str:
                print(f"✓ {archivo}: {perm_actual}")
            else:
                print(f"⚠ {archivo}: {perm_actual} (esperado: {perm_esperado_str})")
        else:
            print(f"✗ {archivo}: No existe")
    print()

    # 8. Variables de entorno
    print("🔧 VARIABLES DE ENTORNO:")
    print("-" * 80)
    env_vars = ["FLASK_ENV", "SECRET_KEY", "HOME", "PYTHONPATH"]
    for var in env_vars:
        valor = os.environ.get(var, "NO DEFINIDA")
        if var == "SECRET_KEY" and valor != "NO DEFINIDA":
            print(f"✓ {var}: {'*' * 20} (configurada)")
        else:
            print(f"  {var}: {valor}")
    print()

    # 9. Resumen
    print("=" * 80)
    print("RESUMEN:")
    print("=" * 80)

    errores = []

    if not os.path.exists("passenger_wsgi.py"):
        errores.append("Falta passenger_wsgi.py")

    if not os.path.exists("app.py"):
        errores.append("Falta app.py")

    try:
        from app import app
    except:
        errores.append("No se puede importar la aplicación")

    if errores:
        print("✗ PROBLEMAS ENCONTRADOS:")
        for error in errores:
            print(f"  - {error}")
    else:
        print("✓ ¡Todo parece estar bien!")

    print()
    print("📝 PRÓXIMOS PASOS:")
    print("-" * 80)
    print("1. Si hay módulos faltantes: pip install -r requirements.txt")
    print("2. Si hay permisos incorrectos: chmod 755 passenger_wsgi.py app.py")
    print("3. Reiniciar Passenger: touch tmp/restart.txt")
    print("4. Ver logs: tail -f ~/logs/error.log")
    print("=" * 80)

if __name__ == "__main__":
    main()
