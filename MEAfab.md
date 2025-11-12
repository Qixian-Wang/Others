### Spin coating

-500 5sec -> 3000 30sec (ramp: 1000)

-Bake 60 for 2mins, 110 for 50s

### First Lithography
When loading new gds design, do review and select exposure mode: fast
1. Laser 375nm, dose 210, click box "expose with subtrate angle"
2. Develop 30s using AZ400K 1:4
3. Bake 110 for 50s

### E-beam
Before it: 1. Check Ti and Pt are available; 2. bring metal plates.
1. Read SOP for guides until after selecting recipe.
2. Fast Ti -> 0.15KA
3. Pt -> 0.85KA

### Lift-off
1. Actone
2. Use ultra sound if necessary, not too much.

### PECVD
1. Before it, use Actone, IPA, and water to wash the wafer.
2. Follow SOP to operate. Recipe: SiN-HF/LF low stress new.
3. Two epochs, 5 mins rest in between.

### Second Lithography
1. Create one empty layer, in the second layer, load the pattern
2. Dose 210
The side facing the left in the machine is the bottom side in gds file.
Other are the same as first lithography

### RIE
Bring multimeter
1. Login as: ID: **SU** Pass: **Self**, so we can edit recipe
2. Use *ZS SIN*, which is:CF4:20; Ar:5; CHF3:15; Init Pres:4; RF Power:150; Process: 10mins each, 3 epochs.

