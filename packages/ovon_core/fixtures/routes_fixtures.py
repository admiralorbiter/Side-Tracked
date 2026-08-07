"""Centralized Domain Fixtures for Sidetrack Route Options and Field Packs."""

from packages.ovon_core.domain import (
    FieldCue,
    RouteOption,
    RoutePersona,
    RouteSegment,
    TaxonRef,
)

# Canonical Taxa Fixtures
ROBIN = TaxonRef.create("American Robin", "Turdus migratorius", "amerob")
CARDINAL = TaxonRef.create("Northern Cardinal", "Cardinalis cardinalis", "norcar")
BLUE_JAY = TaxonRef.create("Blue Jay", "Cyanocitta cristata", "blujay")
WOODPECKER = TaxonRef.create("Red-headed Woodpecker", "Melanerpes erythrocephalus", "rehwoo")
TITMOUSE = TaxonRef.create("Tufted Titmouse", "Baeolophus bicolor", "tuftit")
WREN = TaxonRef.create("Carolina Wren", "Thryothorus ludovicianus", "carwre")
WAXWING = TaxonRef.create("Cedar Waxwing", "Bombycilla cedrorum", "cedwax")

# Invariant-compliant Field Cues (matching focal species)
CUE_ROBIN = FieldCue(
    ROBIN, "Scan low lawn areas and open park paths.", "Listen for cheery liquid warbling songs."
)
CUE_CARDINAL = FieldCue(
    CARDINAL, "Scan low dogwood shrubs near pond edge.", "Listen for sharp metallic 'chip' call."
)
CUE_WOODPECKER = FieldCue(
    WOODPECKER,
    "Inspect dead tree snags near Brush Creek.",
    "Listen for loud rolling churring calls.",
)
CUE_WAXWING = FieldCue(
    WAXWING,
    "Look high in fruiting cedar tree branches.",
    "Listen for high-pitched thin lisping whistles.",
)

# Segments
SEGMENT_EASY_1 = RouteSegment(
    index=1,
    name="Loose Park Lawn Loop",
    habitat_name="Open Parkland",
    distance_meters=1800.0,
    duration_minutes=45.0,
    focal_species=(ROBIN, CARDINAL, BLUE_JAY),
    field_cue=CUE_ROBIN,
)

SEGMENT_BIRDY_1 = RouteSegment(
    index=1,
    name="Park Perimeter & Pond Edge",
    habitat_name="Pond & Grassland",
    distance_meters=800.0,
    duration_minutes=15.0,
    focal_species=(CARDINAL, BLUE_JAY),
    field_cue=CUE_CARDINAL,  # Corrected from CUE_ROBIN to CUE_CARDINAL
)

SEGMENT_BIRDY_2 = RouteSegment(
    index=2,
    name="Brush Creek Canopy Trail",
    habitat_name="Mature Hardwood Forest",
    distance_meters=1400.0,
    duration_minutes=30.0,
    focal_species=(WOODPECKER, TITMOUSE, WREN),
    field_cue=CUE_WOODPECKER,
)

SEGMENT_WEIRD_1 = RouteSegment(
    index=1,
    name="Old Orchard Tree Line",
    habitat_name="Overgrown Orchard Edge",
    distance_meters=2100.0,
    duration_minutes=45.0,
    focal_species=(WAXWING, TITMOUSE),
    field_cue=CUE_WAXWING,
)

# Route Options
ROUTE_EASY = RouteOption(
    id="easy-1",
    persona=RoutePersona.EASY,
    name="The Easy One",
    tagline="Shortest path with paved trails and low elevation change.",
    duration_minutes=45,
    distance_meters=1800.0,
    badge_label="Lowest effort",
    tradeoff_description="Paved park paths with standard suburban bird activity.",
    segments=(SEGMENT_EASY_1,),
)

ROUTE_BIRDY = RouteOption(
    id="birdy-1",
    persona=RoutePersona.BIRDY,
    name="The Birdy One",
    tagline="Diverges into dense tree canopy and creek bed edge habitat.",
    duration_minutes=45,
    distance_meters=2200.0,
    badge_label="Best bird opportunity",
    tradeoff_description="Adds 400m of dirt trail near Brush Creek for double species diversity.",
    segments=(SEGMENT_BIRDY_1, SEGMENT_BIRDY_2),
)

ROUTE_WEIRD = RouteOption(
    id="weird-1",
    persona=RoutePersona.WEIRD,
    name="The Weird One",
    tagline="Explores lesser-known perimeter tree line and old orchard edge.",
    duration_minutes=45,
    distance_meters=2100.0,
    badge_label="Unusual habitat",
    tradeoff_description="Uneven terrain along forgotten overgrown fence line.",
    segments=(SEGMENT_WEIRD_1,),
)

ALL_FIXTURE_ROUTES: dict[str, RouteOption] = {
    "easy-1": ROUTE_EASY,
    "birdy-1": ROUTE_BIRDY,
    "weird-1": ROUTE_WEIRD,
}
