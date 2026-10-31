"""Sample parts catalogue chunks for a made-up company. All text is invented for the demo."""

CHUNKS = [
    "XR-7720-B pump housing: tighten the four M6 bolts to 9 N·m. Replace the O-ring at every service.",
    "XR-7720-A pump housing: tighten the four M6 bolts to 7 N·m. Use the older grey O-ring.",
    "XR-7730-B pump impeller: check for cracks and clean with warm water before refitting.",
    "KT-4410 filter cartridge: replace every 6 months or when the pressure light turns amber.",
    "KT-4415 filter cartridge, extended life: replace every 12 months or when the pressure light turns amber.",
    "Troubleshooting low flow: check the inlet screen, then the filter cartridge, then the impeller.",
    "Troubleshooting noise: a rattle usually means a loose housing bolt; a whine usually means a worn bearing.",
    "Storage: keep spare cartridges sealed, between 5 and 30 degrees, away from direct sunlight.",
    "Safety: switch off and unplug the pump before opening the housing.",
    "Ordering: parts ship within 2 business days. Quote the part number from the label on the housing.",
]

# (query, index of the chunk that answers it, kind of query)
QUESTIONS = [
    ("XR-7720-B bolt torque", 0, "part number"),
    ("XR-7720-A bolt torque", 1, "part number"),
    ("KT-4415 replacement interval", 4, "part number"),
    ("XR-7730-B cleaning", 2, "part number"),
    ("the pump is making a grinding whining sound", 6, "plain words"),
    ("water barely comes out", 5, "plain words"),
    ("how should I store spare filters", 7, "plain words"),
    ("is it safe to open the casing while it is running", 8, "plain words"),
]
