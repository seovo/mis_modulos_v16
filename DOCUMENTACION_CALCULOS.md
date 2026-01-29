# Documentación de Cálculos - Módulo Datawave (Odoo ERP)

Esta documentación detalla la lógica de cálculo utilizada en los modelos intermedios del módulo Datawave, enfocándose en `datawave.intermedio.tienda` y `datawave.intermedio.cd`.

---

## 1. Datawave Intermedio Tienda (`datawave.intermedio.tienda`)

Este modelo gestiona el reabastecimiento a nivel de tienda.

### 1.1. Campos Principales y Origen de Datos
- **Forecast Diario (`forecast_day`)**: Obtenido de `datawave.forecast.tienda`.
- **Sigma (`sigma`)**: Desviación estándar poblacional de las ventas históricas (`datawave.sale`) en una ventana de tiempo definida por el parámetro `datawave.ventana_sigma_dias`.
- **Stock (`stock`)**: Nivel de inventario actual en la tienda obtenido de `datawave.stock.tienda`.
- **LT Días (`lt_days`)**: Lead Time en días definido en la configuración de producto por tienda.

### 1.2. Cálculos de Inventario

#### Stock de Seguridad (SS)
Depende del parámetro de configuración `datawave.z_tienda`:
- **Si `z_tienda` es 1**: `SS = z_tienda * sigma * sqrt(lt_days)`
- **Caso contrario**: `SS = lt_days * forecast_day`

#### Frecuencia (FREQ)
Basado en el método configurado en `datawave.metodo_frecuencia_tienda`:
1. **Fija**: `days_frequency` de la configuración de la tienda.
2. **Delta**: `lt_days + days_delta`.
3. **Target**: `days_target` del pronóstico de la tienda.

#### Máximo (MAX)
Basado en el método configurado en `datawave.metodo_max_tienda`:
1. **Método 1**: `MAX = ((lt_days + freq) * freq) + SS`
2. **Método 2**: `MAX = (14 * forecast_day) + SS`

#### Punto de Reorden (ROP)
`ROP = (forecast_day * lt_days) + SS`

### 1.3. Clasificaciones

#### Riesgo
- **0 (Sin Riesgo)**: `stock >= SS` Y `stock >= ROP`
- **1 (Riesgo 1)**: `stock >= SS` Y `stock < ROP`
- **2 (Riesgo 2)**: `stock > 0` Y `stock < SS`
- **3 (Riesgo 3)**: `stock <= 0`

#### Sobreestock
- **0 (Sin SobreStock)**: `stock <= MAX`
- **1 (SobreStock 1)**: `stock > MAX` (pero `<= MAX + SS`)
- **2 (SobreStock 2)**: `stock > MAX + SS`

### 1.4. Sugerencia de Reposición
- **Cantidad Sugerida (`quantity`)**: `max(stock, MAX)`
  *(Nota: Según la implementación actual en el código. Típicamente esto suele ser `MAX - stock`, por lo que podría requerir revisión).*
- **Cantidad Redondeada (`quantity_round`)**: La cantidad sugerida redondeada al múltiplo superior de `round_tienda` definido para el producto/tienda.

---

## 2. Datawave Intermedio CD (`datawave.intermedio.cd`)

Este modelo gestiona el reabastecimiento a nivel de Centro de Distribución (CD).

### 2.1. Campos Principales
- **Forecast Diario (`forecast_day`)**: Obtenido de `datawave.forecast.cd`.
- **Sigma (`sigma`)**: Desviación estándar poblacional de las ventas del CD (`datawave.sale.cd`) según `datawave.ventana_sigma_dias_cd`.
- **MOQ (Cantidad Mínima de Pedido)**: Definido en `datawave.config.proveedor.cd` o el valor por defecto del proveedor.
- **Stock en Tránsito (`stock_transit`)**: Resumen de inventario en tránsito.
- **Stock Pronosticado (`stock_forecast`)**: `Stock Actual + Stock en Tránsito`.

### 2.2. Cálculos de Inventario

#### Stock de Seguridad (SS)
Depende del parámetro de configuración `datawave.z_cd`:
- **Si `z_cd` es 1**: `SS = z_cd * sigma * sqrt(lt_days)`
- **Caso contrario**: `SS = lt_days * forecast_day`

#### Frecuencia (FREQ)
Basado en `datawave.metodo_frecuencia_cd`:
1. **Empírica**: `frecuency_empirical` de la configuración.
2. **EOQ (Economic Order Quantity)**: `sqrt((2 * forecast_day * 365 * cost_sale) / cost_keep)` (si el costo de mantenimiento no es 0).
3. **Target**: `days_target`.
4. **Delta**: `lt_days + days_delta`.
5. **Basado en MOQ**: `forecast_day / moq`.

#### Máximo (MAX)
Basado en `datawave.metodo_max_cd`:
1. **Método 1**: `MAX = (2 * forecast_day * lt_days) + (forecast_day + freq)`
2. **Método 2**: `MAX = (lt_days * freq) + SS`

#### Punto de Reorden (ROP)
`ROP = forecast_day + lt_days + SS`

### 2.3. Clasificaciones
Utiliza una lógica de Riesgo y Sobreestock similar a la de Tienda, comparando el stock actual contra SS, ROP y MAX.

### 2.4. Sugerencia de Reposición
- **Cantidad Sugerida (`quantity`)**: `max(0, MAX - stock_forecast)`
- **Cantidad Redondeada (`quantity_round`)**:
  - Si `quantity <= MOQ`: Se sugiere el **MOQ**.
  - Si `quantity > MOQ`: Se redondea al múltiplo superior de `round_cd`.
