"""30 Curated Greater Kansas City Species Domain Fixtures and Field Cue Profiles."""

from packages.ovon_core.domain import FieldCue, FieldCueProfile, TaxonRef, TaxonSupport

# 1. Woodland & Canopy (8 Taxa)
DOWWO = TaxonRef.create("Downy Woodpecker", "Dryobates pubescens", "dowwoo")
REBWOO = TaxonRef.create("Red-bellied Woodpecker", "Melanerpes carolinus", "rebwoo")
WBNUT = TaxonRef.create("White-breasted Nuthatch", "Sitta carolinensis", "wbnut")
BKCCHI = TaxonRef.create("Black-capped Chickadee", "Poecile atricapillus", "bkcchi")
TUFTIT = TaxonRef.create("Tufted Titmouse", "Baeolophus bicolor", "tuftit")
GHOWL = TaxonRef.create("Great Horned Owl", "Bubo virginianus", "ghowl")
COOHAW = TaxonRef.create("Cooper's Hawk", "Accipiter cooperii", "coohaw")
BAROWL = TaxonRef.create("Barred Owl", "Strix varia", "barowl")

# 2. Parkland, Open & Edges (10 Taxa)
AMEROB = TaxonRef.create("American Robin", "Turdus migratorius", "amerob")
NORCAR = TaxonRef.create("Northern Cardinal", "Cardinalis cardinalis", "norcar")
BLUJAY = TaxonRef.create("Blue Jay", "Cyanocitta cristata", "blujay")
REHWOO = TaxonRef.create("Red-headed Woodpecker", "Melanerpes erythrocephalus", "rehwoo")
EASBLU = TaxonRef.create("Eastern Bluebird", "Sialia sialis", "easblu")
AMEGFI = TaxonRef.create("American Goldfinch", "Spinus tristis", "amegfi")
SONSPA = TaxonRef.create("Song Sparrow", "Melospiza melodia", "sonspa")
HOUWRE = TaxonRef.create("House Wren", "Troglodytes aedon", "houwre")
MOUDOV = TaxonRef.create("Mourning Dove", "Zenaida macroura", "moudov")
NORFLI = TaxonRef.create("Northern Flicker", "Colaptes auratus", "norfli")

# 3. Water & Riparian Edge (6 Taxa)
GRBHER = TaxonRef.create("Great Blue Heron", "Ardea herodias", "grbher")
BELKIN = TaxonRef.create("Belted Kingfisher", "Megaceryle alcyon", "belkin")
MALLAR = TaxonRef.create("Mallard", "Anas platyrhynchos", "mallar3")
WOODUC = TaxonRef.create("Wood Duck", "Aix sponsa", "wooduc")
GREHER = TaxonRef.create("Green Heron", "Butorides virescens", "greher")
SPOSAND = TaxonRef.create("Spotted Sandpiper", "Actitis macularius", "sposand")

# 4. Aerial & High Canopy (6 Taxa)
CEDWAX = TaxonRef.create("Cedar Waxwing", "Bombycilla cedrorum", "cedwax")
BARSWA = TaxonRef.create("Barn Swallow", "Hirundo rustica", "barswa")
CHISWI = TaxonRef.create("Chimney Swift", "Chaetura pelagica", "chiswi")
BALORI = TaxonRef.create("Baltimore Oriole", "Icterus galbula", "balori")
RBGROS = TaxonRef.create("Rose-breasted Grosbeak", "Pheucticus ludovicianus", "rbgros")
RETHAW = TaxonRef.create("Red-tailed Hawk", "Buteo jamaicensis", "rethaw")

ALL_KC_TAXA: tuple[TaxonRef, ...] = (
    # Woodland & Canopy
    DOWWO, REBWOO, WBNUT, BKCCHI, TUFTIT, GHOWL, COOHAW, BAROWL,
    # Parkland & Open
    AMEROB, NORCAR, BLUJAY, REHWOO, EASBLU, AMEGFI, SONSPA, HOUWRE, MOUDOV, NORFLI,
    # Water & Riparian
    GRBHER, BELKIN, MALLAR, WOODUC, GREHER, SPOSAND,
    # Aerial & High Canopy
    CEDWAX, BARSWA, CHISWI, BALORI, RBGROS, RETHAW,
)

# Invariant-compliant Field Cues
KC_FIELD_CUES: dict[str, FieldCue] = {
    # Woodland
    "dowwoo": FieldCue(DOWWO, "Inspect lower tree trunks and dead oak branches.", "Listen for light rapid tapping and squeaky 'pik' calls.", "Look-alikes: Hairy Woodpecker (larger bill)."),
    "rebwoo": FieldCue(REBWOO, "Scan thick tree trunks and main canopy limbs.", "Listen for rolling 'churr-churr' rattling calls.", "Look-alikes: Red-headed Woodpecker (full red head)."),
    "wbnut": FieldCue(WBNUT, "Watch for small birds walking head-first down tree trunks.", "Listen for nasal 'yank-yank' calls echoing through woods.", "Look-alikes: Red-breasted Nuthatch."),
    "bkcchi": FieldCue(BKCCHI, "Look in mid-story branches and feeder edges.", "Listen for clear 'fee-bee' song and cheerful 'chick-a-dee-dee'.", "Look-alikes: Carolina Chickadee."),
    "tuftit": FieldCue(TUFTIT, "Scan oak/hickory canopy and shrub layers.", "Listen for clear whistled 'peter-peter-peter' songs.", "Look-alikes: Black-crested Titmouse."),
    "ghowl": FieldCue(GHOWL, "Look high in evergreen pine stands or deep ravine woods.", "Listen for deep resonant 'hoo-h'hoo-hoo-hoo' hooting at dusk.", "Look-alikes: Barred Owl."),
    "coohaw": FieldCue(COOHAW, "Watch for medium hawks flying through woodland clearings with rapid wingflaps.", "Listen for harsh nasal 'kew-kew-kew' alarm calls near nest sites.", "Look-alikes: Sharp-shinned Hawk."),
    "barowl": FieldCue(BAROWL, "Look in dense mature woodland ravines and river bottoms.", "Listen for rhythmic 'who-cooks-for-you, who-cooks-for-you-all'.", "Look-alikes: Great Horned Owl."),

    # Parkland & Open
    "amerob": FieldCue(AMEROB, "Scan open lawn areas and moist park paths.", "Listen for cheery liquid warbling songs.", "Look-alikes: Varied Thrush."),
    "norcar": FieldCue(NORCAR, "Scan low thickets and dogwood shrubs.", "Listen for sharp metallic 'chip' call and clear cheer whistles.", "Look-alikes: Pyrrhuloxia."),
    "blujay": FieldCue(BLUJAY, "Watch oak trees for bright blue plumage and crest.", "Listen for loud 'jay-jay' calls and hawk imitations.", "Look-alikes: Scrub Jay."),
    "rehwoo": FieldCue(REHWOO, "Inspect standing dead snags near park clearings.", "Listen for loud rolling churring calls.", "Look-alikes: Red-bellied Woodpecker."),
    "easblu": FieldCue(EASBLU, "Look on fence posts and park nest box tops.", "Listen for soft warbling 'turr-wee' songs.", "Look-alikes: Indigo Bunting."),
    "amegfi": FieldCue(AMEGFI, "Scan thistle patches and open meadow weeds.", "Listen for lively twittering songs and 'per-chic-o-ree' flight calls.", "Look-alikes: Yellow Warbler."),
    "sonspa": FieldCue(SONSPA, "Look in brush piles and low meadow grass edges.", "Listen for sweet introductory notes followed by a buzz and trill.", "Look-alikes: Lincoln's Sparrow."),
    "houwre": FieldCue(HOUWRE, "Inspect nest boxes, brush piles, and garden fence lines.", "Listen for rapid bubbling energetic warbles.", "Look-alikes: Carolina Wren."),
    "moudov": FieldCue(MOUDOV, "Look along utility lines, gravel paths, and open lawn edges.", "Listen for soft mournful 'coo-oo, coo, coo' calls.", "Look-alikes: Eurasian Collared-Dove."),
    "norfli": FieldCue(NORFLI, "Scan open park lawns for feeding birds and yellow wing undersides.", "Listen for loud ringing 'wick-wick-wick' calls.", "Look-alikes: Red-shafted Flicker."),

    # Water & Riparian
    "grbher": FieldCue(GRBHER, "Scan shallow creek edges, pond banks, and wetland mudflats.", "Listen for deep harsh croaking flight squawks.", "Look-alikes: Great Egret."),
    "belkin": FieldCue(BELKIN, "Watch overhanging branches near Brush Creek or pond edges.", "Listen for loud harsh rattling calls along water corridors.", "Look-alikes: Green Kingfisher."),
    "mallar3": FieldCue(MALLAR, "Look in open park ponds, creeks, and wetland shallows.", "Listen for classic female 'quack-quack' calls.", "Look-alikes: American Black Duck."),
    "wooduc": FieldCue(WOODUC, "Scan wooded creek corridors and tree-lined pond banks.", "Listen for rising 'oo-eek' squeals in flight.", "Look-alikes: Mandarin Duck."),
    "greher": FieldCue(GREHER, "Look among willow branches near water edges.", "Listen for sharp explosive 'skeeow' alarm calls when flushed.", "Look-alikes: Little Blue Heron."),
    "sposand": FieldCue(SPOSAND, "Look along shoreline mudflats and rocky stream banks teetering tail up-and-down.", "Listen for high shrill 'weet-weet' flight calls.", "Look-alikes: Solitary Sandpiper."),

    # Aerial & High Canopy
    "cedwax": FieldCue(CEDWAX, "Look high in fruiting cedar trees and berry bushes.", "Listen for high-pitched thin lisping whistles.", "Look-alikes: Bohemian Waxwing."),
    "barswa": FieldCue(BARSWA, "Watch over open fields and ponds for deeply forked tail flight.", "Listen for cheerful squeaky chattering flight calls.", "Look-alikes: Cliff Swallow."),
    "chiswi": FieldCue(CHISWI, "Look high overhead for 'cigar with wings' rapid flight.", "Listen for loud sputtering chattering flight notes.", "Look-alikes: Vaux's Swift."),
    "balori": FieldCue(BALORI, "Look high in deciduous elm/sycamore canopy.", "Listen for rich whistling flute-like songs.", "Look-alikes: Orchard Oriole."),
    "rbgros": FieldCue(RBGROS, "Scan high tree canopy and fruiting tree edges.", "Listen for rich robin-like song with sweet mellifluous tone.", "Look-alikes: Black-headed Grosbeak."),
    "rethaw": FieldCue(RETHAW, "Watch open skies soaring over park clearings or utility poles.", "Listen for piercing raspy 'keeer-aah' screams.", "Look-alikes: Red-shouldered Hawk."),
}

# Detailed Region and Season Aware Field Cue Profiles
KC_FIELD_CUE_PROFILES: dict[str, FieldCueProfile] = {
    t.ebird_code: FieldCueProfile(
        taxon_id=t.taxon_id,
        region_scope="US-MO-KC",
        season_scope="all_year",
        audience="beginner",
        look_for=(KC_FIELD_CUES[t.ebird_code].where_to_look,),
        where_to_look=KC_FIELD_CUES[t.ebird_code].where_to_look,
        listen_for=KC_FIELD_CUES[t.ebird_code].what_to_listen_for,
        where_to_listen=KC_FIELD_CUES[t.ebird_code].where_to_look,
        confusion_taxa=(KC_FIELD_CUES[t.ebird_code].look_alikes,),
        source="Sidetrack Field Team",
        reviewer="Lead Ornithologist",
        version="v1.0",
    )
    for t in ALL_KC_TAXA
}

# Taxon Support Records (Decoupling Scientific Support from Media Completeness)
KC_TAXON_SUPPORT: dict[str, TaxonSupport] = {
    t.ebird_code: TaxonSupport(
        taxonomy_known=True,
        occurrence_data_available=True,
        effort_model_available=True,
        calibrated_model_available=False,
        field_cue_reviewed=True,
        photo_available=True,
        song_available=True,
        call_available=True,
        audio_available=True,
        sensitive=False,
    )
    for t in ALL_KC_TAXA
}
