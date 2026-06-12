# Local Renewable (Solar) Calculation Service

A DOTS-helics calculation service that simulates a local Photovoltaic (PV) solar installation, converting historical solar irradiance data into electrical power generation while enforcing curtailment setpoints.

## Table of Contents
- [Overview](#overview)
- [ESDL Asset Mapping](#esdl-asset-mapping)
- [Calculations & HELICS Federation](#calculations--helics-federation)
- [Data Config & Irradiance Prefetching](#data-config--irradiance-prefetching)
- [Physical Generation Model](#physical-generation-model)
- [Project Structure](#project-structure)
- [How to Build & Run](#how-to-build--run)

---

## Overview

The **Renewable Service** simulates local solar generation. It retrieves historical solar irradiance data from InfluxDB (or generates a clear-sky fallback profile), models the physics of solar cells and inverters, and applies real-time curtailment limits commanded by the Network Balancer (EMS).

The service logic is implemented in [renewableservice.py](src/RenewableService/renewableservice.py) and inherits from the generated [RenewableServiceBase](src/RenewableService/renewable_service_base.py) class.

---

## ESDL Asset Mapping

During simulation initialization (in `init_calculation_service`), the service parses the incoming Energy System Description Language (ESDL) topology to configure its PV properties:

- **ESDL Asset Type:** `PVInstallation`
- **Properties Handled:**
  - `power`: Max nameplate inverter capacity in Watts. Defaults to `1_000_000.0` W (1 MW).
  - `surfaceArea`: Total solar array aperture area in square meters ($m^2$). Defaults to `5000.0` $m^2$.
  - `panelEfficiency`: Conversion efficiency factor of solar panels (0.0 to 1.0). Defaults to `0.20` (20%).
  - `inverterEfficiency`: Conversion efficiency factor of the inverter (0.0 to 1.0). Defaults to `0.98` (98%).
  - `name`: Friendly name of the solar asset.
- **InfluxDB Profile Integration:** Parses any `InfluxDBProfile` associated with the asset's ports to configure solar irradiance data prefetching.

---

## Calculations & HELICS Federation

The service defines three core calculations configured in [input.json](input.json):

### 1. `renewable_state`
- **Execution Interval:** 900 seconds (15 minutes)
- **Offset:** 0 seconds
- **Purpose:** Publishes available solar potential and current actual generation.
- **HELICS Outputs:**
  - `potential_available_generation_ID` (Unit: `W`, Type: `DOUBLE`): The maximum power that could be generated given current irradiance.
  - `supplied_power_ID` (Unit: `W`, Type: `DOUBLE`): Actual power supplied after applying curtailment limits.

### 2. `renewable_dispatch`
- **Execution Interval:** 900 seconds (15 minutes)
- **Offset:** 20 seconds (runs after optimization)
- **Purpose:** Consumes curtailment limits from the Network Balancer.
- **HELICS Inputs:**
  - `current_max_power_limit` (Unit: `W`, Type: `DOUBLE`, Published by `ElectricityNetwork`): The maximum power generation limit commanded by the EMS.
- **Curtailment Logic:**supplied power is calculated as:
  $$\text{Supplied Power} = \min(\text{Potential Generation}, \text{Curtailment Setpoint})$$
  A limit value of $1.0 \times 10^9$ W (1 GW) is used to represent an uncapped (no curtailment) condition.

### 3. `day_ahead_renewables`
- **Execution Interval:** 43200 seconds (12 hours / twice a day)
- **Offset:** 1 second
- **Purpose:** Outputs a 24-hour day-ahead solar generation forecast (96 steps) for the optimization LP.
- **HELICS Outputs:**
  - `planned_generation_DA` (Unit: `VECTOR`, Type: `VECTOR`): JSON array of solar forecast plans.

---

## Data Config & Irradiance Prefetching

At startup, the service pre-fetches the entire simulation window's weather data from InfluxDB to avoid high runtime latency.

- **Profile Configuration:** If an ESDL `InfluxDBProfile` is defined, the service uses its host, port, database, measurement, field, multiplier, and filters.
- **Default Fallbacks:** If no profile is defined, the service queries measurement `historical_solar_irradiance` with the field `Irradiance_W_m2` and filter tag `name = <Asset Name>`.
- **Physics-based Fallback Model:** If InfluxDB data is missing or queries fail, it falls back to a deterministic clear-sky model:
  $$\text{Irradiance}(t) = \max\left(0.0, 1000 \times \sin\left(\pi \times \frac{\text{Hour} - 6}{12}\right)\right)$$
  for hours between 6:00 and 18:00 (returns `0.0` at night).
- **InfluxDB Writing:** Writes `Irradiance_W_m2`, `Potential_Generation_W`, `Supplied_Power_W`, `Curtailment_Limit_W` and day-ahead plans (`planned_generation_DA`) once a day (96 steps).

---

## Physical Generation Model

The electrical power output is calculated using solar panel physics:
$$\text{Raw Generation (W)} = \text{Irradiance} \times \text{surfaceArea} \times \text{panelEfficiency} \times \text{inverterEfficiency}$$
- Capped at inverter nameplate `capacity_w`.
- Multiplied by a small atmospheric variance factor ($\pm 2\%$) utilizing a pseudo-random number generator seeded with simulation time to model realistic clouds.

---

## Project Structure

- [pyproject.toml](pyproject.toml): Package configuration and dependency list.
- [Dockerfile](Dockerfile): Container build using `python:3.13-slim`.
- [code_gen.py](code_gen.py): Code generator invocation script to rebuild base classes.
- [input.json](input.json): Federation calculation specifications.
- **src/RenewableService/**
  - [renewableservice.py](src/RenewableService/renewableservice.py): Primary logic overrides.
  - [renewable_service_base.py](src/RenewableService/renewable_service_base.py): Base class handling HELICS boilerplate.
  - [renewable_service_dataclasses.py](src/RenewableService/renewable_service_dataclasses.py): Return types for service calculations.

---

## How to Build & Run

### Local Execution
Run the script directly to start the calculation service:
```bash
python src/RenewableService/renewableservice.py
```

### Docker Build
Build the container image using the local context:
```bash
docker build -t local-renewable-service:latest .
```
        

---

## Thesis modifications (MSc)

- **Nameplate-driven generation (PV-sizing fix).** Generation was previously `irradiance x surfaceArea x panel_eff x inverter_eff`, capped at nameplate. Because `surfaceArea` was a fixed ESDL value, sweeping the PV nameplate `power` was a no-op (only the cap, which rarely binds, changed), so every non-zero PV size produced the same yield. The effective collector area is now derived from the nameplate rating, `area = P_nom / (G_STC x panel_eff x inverter_eff)` with `G_STC = 1000 W/m^2`, so generation scales linearly with the swept capacity. This is what makes the RQ3 PV-sizing sweep meaningful.
