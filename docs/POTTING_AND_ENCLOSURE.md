# Enclosure, Thermal Stackup & Encapsulation (Potting) Guide

This guide specifies the mechanical enclosure, thermal dissipation path, and two-stage selective encapsulation process for **`fome-mc`**.

![fome-mc Annotated Floorplan & Thermal Zones](renders/fome-mc-floorplan-zones.png)

---

## 1. Enclosure & Mechanical Stackup Diagram

```mermaid
flowchart TB
  subgraph LID["Top Enclosure Cover (Anodized 6061-T6 Aluminum, 166 × 120 × 32 mm Outer)"]
    direction TB
    AIR["6–8 mm Upper Air Headspace (Thermal Expansion Cushion)"]
  end

  subgraph POT["Stage 2 Encapsulant Layer (12 mm Pour Depth)"]
    direction TB
    UR["Soft Thermally Conductive 2-Part Polyurethane\nElectrolube UR5634 or MG Chemicals 832TC\n(Shore A 55–65, k ≥ 0.85 W/m·K, Tg < -45 °C)"]
    COAT["Stage 1 Base Coat: 25–50 µm Acrylic Conformal Coat\n(Electrolube HPA / Humiseal 1B31) over U26, U25, U302, U402, 0402/0603 Passives"]
  end

  subgraph BOARD["fome-mc 4-Layer FR-4 TG170 PCB (162.0 × 115.0 × 1.6 mm)"]
    direction LR
    L1["L1 (F.Cu): Components + High-Current Pours"]
    L2["L2 (In1.Cu): Solid GND Plane + Star AGND"]
    L3["L3 (In2.Cu): +5V / +3.3V / +12V_MR Islands"]
    L4["L4 (B.Cu): Bottom GND + Thermal Via Arrays"]
  end

  subgraph BASE["Bottom Thermal Interface & Baseplate"]
    direction TB
    TIM["1.5 mm Compressible Silicone Thermal Gap Pad (k ≥ 3.0 W/m·K, 30 Shore 00)\nUnder Q201–Q204 (IGBTs), Q301/Q401 (WBO Heaters), U201–U203 (H-Bridges/Stepper), U3 (5V Buck)"]
    CASE["3.0 mm Aluminum Baseplate + 4× M4×10 Bosses (154.0 × 107.0 mm Centers)"]
  end

  LID --> POT --> BOARD --> BASE
```

---

## 2. Worst-Case Thermal Dissipation Budget (`13.4 W` Total)

| Subsystem | Active Devices | Continuous Cruise (`4,000 RPM`) | Worst-Case Redline (`10,500 RPM`) | Primary Heat Path |
| :--- | :--- | :---: | :---: | :--- |
| **Dual Wideband Heaters** | `Q301`, `Q401` (`VND14NV04`) + `D201..208` | `0.7 W` | `1.8 W` | Thermal vias under DPAK tabs $\to$ `B.Cu` $\to$ `1.5 mm` gap pad |
| **4× Ignition IGBTs** | `Q201..Q204` (`FGD3040G2-F085C`) | `1.6 W` (`0.8 W` in 2-coil mode) | `4.2 W` | Left-wing DPAK copper pours + thermal vias $\to$ `B.Cu` $\to$ gap pad |
| **Injectors & Low-Side Switches** | `U1001..U1202` (`VNLD5090TR-E`) | `0.8 W` | `1.9 W` | `In1.Cu`/`B.Cu` `GND` planes + polyurethane top conduction |
| **Stepper (`ISC`) & Dual H-Bridge (`STVA`)** | `U202` (`DRV8825`) + `U201, U203` (`TLE9201SG`) | `1.4 W` | `2.4 W` | Exposed thermal pads (`HTSSOP-28` / `PG-DSO-12`) $\to$ `B.Cu` $\to$ gap pad |
| **Power Supply (`VBoost`, `5V`, `LDOs`)** | `U46`, `L3`, `U3` (`LMR14020`), `U1, U2` (`TLS115D0E`), `U13` (`BD3571`) | `1.3 W` | `2.1 W` | Top-edge power copper pours + thermal vias $\to$ `B.Cu` |
| **3× MCUs & Transceivers** | `U26` (`STM32H753`), `U302, U402` (`STM32F042`), `U4, U5, U200` (`TJA1051`) | `0.9 W` | `1.0 W` | `In1.Cu` `GND` plane + top polyurethane conduction |
| **Total Board Dissipation** | **All Subsystems** | **`6.7 W`** | **`13.4 W`** | **Max $\Delta T_{j\text{-case}} < 9\,^\circ\text{C}$ across `1.5 mm` pad + potting** |

---

## 3. Barometric Sensor Strategy: Single-Pour Flood Potting vs. Unpotted Chimney Dam

As tracked in Plane work item **`FOMEMC-1`**:

1. **Recommended Potted Production Build (Single-Pour Flood Potting + External GM/Delphi 1-Bar Sensor)**:
   - Wire an external **GM `12614970` / Delphi `PS10150` 1-bar sensor** (`MT_GM_1_BAR`, `10–105 kPa`) to `J1-29` (`5V_SENSOR_1`), `J1-31` (`SGND`), and `J2-6` (`MAP2_REAR` / `PA2` `EFI_ADC_2`).
   - Leave `U24` (`LPS25HBTR`) unpopulated (`DNP`) or pot directly over it with **no chimney dam and no lid vent hole**, achieving a 100% solid, single-pour potted enclosure with zero capillary wicking risk.
2. **Unpotted / Bench Build (or Vented Chimney Dam Build)**:
   - Populate `U24` (`LPS25HBTR`, `C87898` at `121.62, 100.61 mm` on `I2C2` `PB10/PB11`). If potting with `U24` active, bond an `ID 8.0 mm × OD 11.0 mm` silicone/ABS chimney dam around `U24` prior to pouring Stage 2 polyurethane and vent the pocket through an `M6×0.75` **Amphenol LTW `VE80410`** or **Gore `PMF100321`** hydrophobic ePTFE membrane in the top lid.

---

## 4. Step-by-Step Encapsulation Workflow

```mermaid
flowchart LR
  S1["1. Pre-Pot Bench Gate\nVerify all rails, DFU,\nOpenBLT, SDMMC1, CAN1/2,\nWBO1/2, VR1/2, INJ & IGBT\n(VALIDATION.md §2)"] --> S2["2. Ultrasonic Clean & Bake\nClean flux with IPA/deionized\nwater; bake PCB 2 hr @ 70 °C\nto remove moisture"]
  S2 --> S3["3. Stage 1 Conformal Coat\nMask J1/J2 mating pins;\nspray 25–50 µm acrylic coat\n(Electrolube HPA / Humiseal 1B31)\nCure 2 hr @ 60 °C"]
  S3 --> S4["4. Mount PCB in Case\nPlace 1.5 mm thermal gap pad;\ntorque 4× M4 screws to 1.2 N·m;\nseate J1/J2 flange gasket"]
  S4 --> S5["5. Stage 2 Polyurethane Pour\nMix & vacuum-degas UR5634 / 832TC;\npour to 12 mm depth at 45 °C;\ncure 24 hr @ 25 °C (or 4 hr @ 60 °C)"]
  S5 --> S6["6. Post-Pot Acceptance\nRe-run USB/CAN OpenBLT,\nSDMSD log handoff, and\nthermal soak test"]
```
