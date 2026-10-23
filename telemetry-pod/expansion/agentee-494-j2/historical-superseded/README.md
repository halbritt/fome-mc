# SUPERSEDED: DO NOT USE

`SUPERSEDED-DO-NOT-USE_SMA_Amphenol_132134_494_Conditional.kicad_mod` is the superseded enlarged-hole variant: centre drill **2.0 mm**, four ground drills **2.4 mm**. It is **NOT the Amphenol published pattern** and is retained only as historical evidence outside the selectable `Agentee494.pretty` library.

Use [`../Agentee494.pretty/SMA_Amphenol_132134_Manufacturer.kicad_mod`](../Agentee494.pretty/SMA_Amphenol_132134_Manufacturer.kicad_mod), per the retained Amphenol RF 132134 Rev C [`../132134-revC.pdf`](../132134-revC.pdf), SHA256 `1ec1d365bf5bf9e1598cf7cf2c90747ba11f06607f4c6a28ca6d30a0aab56034`, primary URL https://www.amphenolrf.com/en-us/assets/file/4065789557/ . Sheet 3, **PCB MOUNTING HOLES**, gives the printed callouts **"1,5 [.059]"** centre, **"4- 1,7 [.067]"** ground and **"5,08 [.200]"** square; diameter symbols accompany the hole callouts. The dimensions belong to Amphenol. Agent-519's all-five-1.7 over-read was corrected by `de8f30ed-ea69-4eb3-93ff-ed53bfe1c8e1@1`.

F8 relocation: the enlarged-hole file moved byte-for-byte from `Agentee494.pretty` to this historical directory. `native494.json` and 494b `analysis/*` retain their original observed content unchanged; see `../native494.NOTE.md`. The current `native494.py` helper loads only the Manufacturer footprint.
