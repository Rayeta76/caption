# 🌿 Estrategia de Ramas - StockPrep Pro v2.0

## 📋 Resumen de Ramas

### **🛡️ `main` - Rama Estable (Seguro de Vida)**
- **Propósito**: Código estable y funcional
- **Estado**: ✅ Estable y probado
- **Uso**: Releases oficiales y producción
- **Protección**: Solo merge desde ramas de desarrollo

### **🚀 `mejora_modelo` - Rama de Desarrollo Principal**
- **Propósito**: Mejoras del modelo y funcionalidades
- **Estado**: 🔄 En desarrollo activo
- **Uso**: Nuevas características y optimizaciones
- **Origen**: Creada desde `main` el 28/06/2025

## 🔄 Flujo de Trabajo

### **Estructura de Ramas**
```
main (estable)
├── mejora_modelo (desarrollo principal)
│   ├── feature/nueva-funcionalidad
│   ├── fix/correccion-bug
│   └── refactor/mejora-codigo
└── hotfix/urgente (si es necesario)
```

### **Proceso de Desarrollo**

#### **1. Trabajo en `mejora_modelo`**
```bash
# Asegurarse de estar en la rama de desarrollo
git checkout mejora_modelo

# Crear rama específica para nueva funcionalidad
git checkout -b feature/nueva-funcionalidad

# Trabajar en la funcionalidad
# ... hacer cambios ...

# Commit y push
git add .
git commit -m "✨ Agregar nueva funcionalidad"
git push origin feature/nueva-funcionalidad

# Merge a mejora_modelo
git checkout mejora_modelo
git merge feature/nueva-funcionalidad
git push origin mejora_modelo
```

#### **2. Release a `main`**
```bash
# Cuando mejora_modelo esté estable
git checkout main
git merge mejora_modelo
git tag v2.1.0
git push origin main
git push origin v2.1.0
```

## 🎯 Convenciones de Nombrado

### **Ramas de Funcionalidad**
- `feature/nombre-funcionalidad`
- `feature/optimizacion-gpu`
- `feature/nuevo-modelo`

### **Ramas de Corrección**
- `fix/nombre-bug`
- `fix/memoria-gpu`
- `fix/interfaz-gui`

### **Ramas de Refactorización**
- `refactor/nombre-modulo`
- `refactor/model-manager`
- `refactor/gui-components`

### **Ramas de Hotfix**
- `hotfix/urgente-critico`
- `hotfix/seguridad`
- `hotfix/crash-aplicacion`

## 📝 Mensajes de Commit

### **Formato**
```
🎯 Tipo: Descripción breve

📋 Descripción detallada de los cambios

🔧 Cambios técnicos:
- Cambio 1
- Cambio 2

📚 Documentación:
- Actualización 1
```

### **Tipos de Commit**
- 🚀 **feat**: Nueva funcionalidad
- 🐛 **fix**: Corrección de bug
- 🔧 **refactor**: Refactorización de código
- 📚 **docs**: Documentación
- ⚡ **perf**: Mejoras de rendimiento
- 🧪 **test**: Tests
- 🔄 **chore**: Tareas de mantenimiento

## 🛡️ Protección de Ramas

### **Rama `main`**
- ✅ **Requiere Pull Request**
- ✅ **Requiere revisión de código**
- ✅ **Requiere tests pasando**
- ✅ **No permite push directo**

### **Rama `mejora_modelo`**
- ✅ **Requiere Pull Request** (para cambios grandes)
- ✅ **Permite push directo** (para cambios menores)
- ✅ **Requiere tests pasando**

## 📊 Estado Actual

### **Ramas Activas**
| Rama | Estado | Último Commit | Propósito |
|------|--------|---------------|-----------|
| `main` | ✅ Estable | v2.0.0 | Producción |
| `mejora_modelo` | 🔄 Desarrollo | Refactorización | Nuevas características |

### **Próximas Mejoras en `mejora_modelo`**
- [ ] Optimización adicional del modelo
- [ ] Nuevos niveles de detalle
- [ ] Mejoras en la interfaz
- [ ] Soporte para más formatos de salida
- [ ] Integración con otros modelos

## 🔧 Comandos Útiles

### **Gestión de Ramas**
```bash
# Ver todas las ramas
git branch -a

# Cambiar a rama
git checkout nombre-rama

# Crear y cambiar a nueva rama
git checkout -b nueva-rama

# Eliminar rama local
git branch -d nombre-rama

# Eliminar rama remota
git push origin --delete nombre-rama
```

### **Sincronización**
```bash
# Actualizar rama con main
git checkout mejora_modelo
git merge main

# Actualizar desde remoto
git fetch origin
git pull origin mejora_modelo
```

### **Comparación**
```bash
# Ver diferencias entre ramas
git diff main..mejora_modelo

# Ver commits únicos
git log main..mejora_modelo
```

## 🚨 Reglas Importantes

### **✅ Hacer**
- Trabajar siempre en `mejora_modelo` para nuevas funcionalidades
- Crear ramas específicas para features grandes
- Hacer commits frecuentes y descriptivos
- Probar antes de mergear a `main`
- Documentar cambios importantes

### **❌ No Hacer**
- Trabajar directamente en `main`
- Mergear código no probado a `main`
- Hacer commits sin mensaje descriptivo
- Ignorar tests antes del merge
- Olvidar actualizar documentación

## 📈 Próximos Pasos

### **Corto Plazo**
1. Completar refactorización en `mejora_modelo`
2. Probar todas las funcionalidades
3. Preparar release v2.1.0

### **Mediano Plazo**
1. Implementar nuevas optimizaciones
2. Agregar soporte para más modelos
3. Mejorar la interfaz de usuario

### **Largo Plazo**
1. Integración con APIs externas
2. Soporte para procesamiento distribuido
3. Versión web del sistema

---

**Fecha**: 28 de Junio, 2025
**Versión**: StockPrep Pro v2.0
**Estrategia**: Git Flow Simplificado 