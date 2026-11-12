import argparse
import base64
import ctypes
import hashlib
import json
import os
import pathlib
import shutil
import time
from typing import Dict, List, Optional, Set, Tuple

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

SAVE_DIR = pathlib.Path(os.path.expandvars(r"%UserProfile%\AppData\LocalLow\mkarpenko\WorldBox"))
PROGRESS_FILE = SAVE_DIR / "worldboxProgress"
STEAM_API_DLL = pathlib.Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\worldbox\worldbox_Data\Plugins\x86_64\steam_api64.dll"
)
STEAM_APP_ID = "1206560"

# Chaves derivadas de Toolbox.encode / Toolbox.decode e Encryption do WorldBox
PASS_PHRASE = b"WorldboxIsAwesome555"
INIT_VECTOR = b"sayHiIfUReadThis"

# 86 conquistas ativas extraidas de AchievementLibrary.init (WorldBox v0.50+ / 0.51.2)
IN_GAME_ACHIEVEMENTS: List[str] = [
    "achievementTheAccomplished",
    "achievementTheKing",
    "achievementTheDemon",
    "achievementTheBroken",
    "achievementTouchTheGrass",
    "achievementGen5Worlds",
    "achievementGen50Worlds",
    "achievementGen100Worlds",
    "achievementLifeIsASim",
    "achievementTheCorruptedTrees",
    "achievementTheHell",
    "achievementLetsNot",
    "achievementWorldWar",
    "achievementPlanetOfApes",
    "achievementSuperMushroom",
    "achievementThePrincess",
    "achievementTORNADO",
    "achievementGodMode",
    "achievementGreg",
    "achievementNinjaTurtle",
    "achievementGreatPlague",
    "achievementLavaStrike",
    "achievementBabyTornado",
    "achievementRainTornado",
    "achievement10000Creatures",
    "achievementManyBombs",
    "achievementMegapolis",
    "achievementMakeWilhelmScream",
    "achievementBurger",
    "achievementPie",
    "achievementMayday",
    "achievementDestroyWorldBox",
    "achievementCustomWorld",
    "achievement4RaceCities",
    "achievementPiranhaLand",
    "achievementPrintHeart",
    "achievementSacrifice",
    "achievementAntWorld",
    "achievementFinalResolution",
    "achievementTntAndHeat",
    "achievementGodFingerLightning",
    "achievementTraitsExplorer40",
    "achievementTraitsExplorer60",
    "achievementTraitsExplorer90",
    "achievementTraitExplorerSubspecies",
    "achievementTraitExplorerCulture",
    "achievementTraitExplorerLanguage",
    "achievementTraitExplorerClan",
    "achievementTraitExplorerReligion",
    "achievementEquipmentExplorer",
    "achievementGenesExplorer",
    "achievementCreaturesExplorer",
    "achievementPlotsExplorer",
    "achievementCursedWorld",
    "achievementBoatsDisposal",
    "achievementEngineeredEvolution",
    "achievementSimpleStupidGenetics",
    "achievementFastLiving",
    "achievementLongLiving",
    "achievementAncientWarOfGeometryAndEvil",
    "achievementCantBeTooMuch",
    "achievementZoo",
    "achievementMindlessHusk",
    "achievementMasterWeaver",
    "achievementNotJustACult",
    "achievementSuccession",
    "achievementMultiplySpoken",
    "achievementChildNamedToto",
    "achievementFlickIt",
    "achievementSegregator",
    "achievementEternalChaos",
    "achievementMinefield",
    "achievementGodlySmithing",
    "achievementMasterOfCombat",
    "achievementClannibals",
    "achievementSocialNetwork",
    "achievementWatchYourMouth",
    "achievementCloneWars",
    "achievementSmellyCity",
    "achievementTLDR",
    "achievementNotOnMyWatch",
    "achievementMayIInterrupt",
    "achievementBallToBall",
    "achievementSwordWithShotgun",
    "achievementBackToBetaTesting",
    "achievementSwarm",
]

CATEGORY_LABELS: Dict[str, str] = {
    "unlocked_traits_actor": "Traits de Criaturas (Actor)",
    "unlocked_traits_culture": "Traits de Cultura",
    "unlocked_traits_language": "Traits de Idioma",
    "unlocked_traits_subspecies": "Traits de Subespecie",
    "unlocked_traits_clan": "Traits de Cla",
    "unlocked_traits_kingdom": "Traits de Reino",
    "unlocked_traits_religion": "Traits de Religiao",
    "unlocked_equipment": "Equipamentos e Armas",
    "unlocked_genes": "Genes",
    "unlocked_actors": "Criaturas e Especies",
    "unlocked_plots": "Planos e Tramas (Plots)",
}

# 658 itens ocultos (needs_to_be_explored=True, unlocked_with_achievement=False) da v0.51.2
HIDDEN_ITEMS_NO_ACHIEVEMENT: Dict[str, List[str]] = {
    "unlocked_traits_actor": [
        "metamorphed",
        "clone",
        "boat",
        "scar_of_divinity",
        "miracle_born",
        "miracle_bearer",
        "contagious",
        "zombie",
        "madness",
        "desire_alien_mold",
        "desire_computer",
        "desire_golden_egg",
        "desire_harp",
        "dash",
        "block",
        "dodge",
        "backstep",
        "deflect_projectile",
        "mute",
        "sunblessed",
        "clumsy",
        "fragile_health",
        "boosted_vitality",
        "hard_skin",
        "soft_skin",
        "long_liver",
        "fire_blood",
        "fire_proof",
        "freeze_proof",
        "regeneration",
        "heliophobia",
        "ugly",
        "fat",
        "attractive",
        "fast",
        "slow",
        "gluttonous",
        "eagle_eyed",
        "short_sighted",
        "infertile",
        "fertile",
        "thorns",
        "bubble_defense",
        "immune",
        "agile",
        "weightless",
        "poisonous",
        "venomous",
        "poison_immune",
        "strong",
        "weak",
        "lustful",
        "miner",
        "psychopath",
        "strong_minded",
        "peaceful",
        "evil",
        "hotheaded",
        "stupid",
        "deceitful",
        "content",
        "honest",
        "paranoid",
        "greedy",
        "moonchild",
        "nightchild",
        "flesh_eater",
        "heart_of_wizard",
        "battle_reflexes",
        "arcane_reflexes",
        "healing_aura",
        "savage",
        "cold_aura",
        "lucky",
        "unlucky",
        "pacifist",
        "veteran",
        "wise",
        "infected",
        "mush_spores",
        "tumor_infection",
        "blessed",
        "kingslayer",
        "mageslayer",
        "dragonslayer",
        "crippled",
        "golden_tooth",
        "eyepatch",
        "skin_burns",
        "energized",
        "bomberman",
        "light_lamp",
        "shiny"
    ],
    "unlocked_traits_culture": [
        "axe_lovers",
        "sword_lovers",
        "bow_lovers",
        "hammer_lovers",
        "spear_lovers",
        "craft_flame_weapon",
        "craft_ice_weapon",
        "craft_evil_staff",
        "craft_white_staff",
        "craft_necro_staff",
        "craft_druid_staff",
        "craft_doctor_staff",
        "craft_blaster",
        "city_layout_architects_eye",
        "city_layout_madman_labyrinth",
        "city_layout_bricks",
        "city_layout_raindrops",
        "city_layout_cross",
        "city_layout_claws",
        "city_layout_pebbles",
        "city_layout_stone_garden",
        "city_layout_titan_footprints",
        "city_layout_silk_web",
        "city_layout_iron_weave",
        "city_layout_monolith_mesh",
        "city_layout_royal_checkers",
        "city_layout_diamond",
        "city_layout_parallels",
        "city_layout_pillars",
        "city_layout_rings",
        "buildings_spread",
        "city_layout_tile_wobbly_pattern",
        "city_layout_the_grand_arrangement",
        "city_layout_tile_moonsteps",
        "roads",
        "expansionists",
        "tiny_legends",
        "animal_whisperers",
        "statue_lovers",
        "tower_lovers",
        "training_potential",
        "elder_reverence",
        "youth_reverence",
        "conscription_female_only",
        "conscription_male_only",
        "fast_learners",
        "pep_talks",
        "expertise_exchange",
        "happiness_from_war",
        "dense_dwellings",
        "solitude_seekers",
        "gossip_lovers",
        "reading_lovers",
        "attentive_readers",
        "join_or_die",
        "true_roots",
        "legacy_keepers",
        "serenity_now",
        "weaponsmith_mastery",
        "armorsmith_mastery",
        "patriarchy",
        "matriarchy",
        "ultimogeniture",
        "diplomatic_ascension",
        "fames_crown",
        "golden_rule",
        "shattered_crown",
        "warriors_ascension",
        "xenophobic",
        "ethnocentric_guard",
        "xenophiles",
        "ethno_sculpted"
    ],
    "unlocked_traits_language": [
        "melodic",
        "stylish_writing",
        "scribble",
        "nicely_structured_grammar",
        "beautiful_calligraphy",
        "font_of_gods",
        "chilly_font",
        "powerful_words",
        "confusing_semantics",
        "raging_paragraphs",
        "scorching_words",
        "enlightening_script",
        "foolish_glyphs",
        "elegant_words",
        "strict_spelling",
        "divine_encryption"
    ],
    "unlocked_traits_subspecies": [
        "metamorphosis_chicken",
        "metamorphosis_wolf",
        "metamorphosis_sword",
        "bioproduct_gems",
        "bioproduct_stone",
        "bioproduct_mushrooms",
        "population_minimal",
        "population_small",
        "population_moderate",
        "population_large",
        "population_expansive",
        "gestation_short",
        "gestation_moderate",
        "gestation_long",
        "gestation_very_long",
        "gestation_extremely_long",
        "gmo",
        "uplifted",
        "exoskeleton",
        "long_lifespan",
        "hyper_intelligence",
        "advanced_hippocampus",
        "wernicke_area",
        "amygdala",
        "prefrontal_cortex",
        "photosynthetic_skin",
        "genetic_psychosis",
        "bioluminescence",
        "accelerated_healing",
        "rapid_aging",
        "slow_builders",
        "cold_resistance",
        "stomach",
        "big_stomach",
        "voracious",
        "diet_frugivore",
        "diet_granivore",
        "diet_florivore",
        "diet_graminivore",
        "diet_xylophagy",
        "diet_geophagy",
        "diet_folivore",
        "diet_carnivore",
        "diet_piscivore",
        "diet_lithotroph",
        "diet_insectivore",
        "diet_algivore",
        "diet_nectarivore",
        "diet_hematophagy",
        "diet_herbivore",
        "diet_omnivore",
        "reproduction_sexual",
        "reproduction_spores",
        "reproduction_fission",
        "reproduction_budding",
        "reproduction_hermaphroditic",
        "reproduction_parthenogenesis",
        "reproduction_vegetative",
        "reproduction_divine",
        "reproduction_soulborne",
        "reproduction_metamorph",
        "reproduction_strategy_oviparity",
        "reproduction_strategy_viviparity",
        "aggressive",
        "super_positivity",
        "telepathic_link",
        "inquisitive_nature",
        "cautious_instincts",
        "hovering",
        "pollinating",
        "hydrophobia",
        "energy_preserver",
        "polyphasic_sleep",
        "monophasic_sleep",
        "prolonged_rest",
        "nocturnal_dormancy",
        "circadian_drift",
        "winter_slumberers",
        "chaos_driven",
        "gift_of_fire",
        "gift_of_thunder",
        "gift_of_void",
        "gift_of_air",
        "gift_of_blood",
        "gift_of_harmony",
        "gift_of_water",
        "gift_of_life",
        "gift_of_death",
        "annoying_fireworks",
        "spicy_kids",
        "parental_care",
        "adaptation_desert",
        "adaptation_swamp",
        "adaptation_wasteland",
        "adaptation_corruption",
        "adaptation_permafrost",
        "adaptation_infernal",
        "mutation_skin_light_orb",
        "mutation_skin_living_rock",
        "mutation_skin_tentacle_horror",
        "mutation_skin_abomination",
        "mutation_skin_fractal",
        "mutation_skin_void",
        "mutation_skin_blood_vortex",
        "mutation_skin_energy",
        "egg_shell_plain",
        "egg_shell_spotted",
        "egg_colored",
        "egg_roe",
        "egg_face",
        "egg_orb",
        "egg_alien",
        "egg_cocoon",
        "egg_metal_box",
        "egg_crystal",
        "egg_ice",
        "egg_blob",
        "egg_candy",
        "egg_bubble",
        "egg_rainbow",
        "egg_flames",
        "phenotype_skin_skin_pale",
        "phenotype_skin_skin_light",
        "phenotype_skin_skin_medium",
        "phenotype_skin_skin_dark",
        "phenotype_skin_skin_black",
        "phenotype_skin_skin_mixed",
        "phenotype_skin_skin_red",
        "phenotype_skin_skin_yellow",
        "phenotype_skin_skin_green",
        "phenotype_skin_skin_blue",
        "phenotype_skin_skin_purple",
        "phenotype_skin_skin_pink",
        "phenotype_skin_white_gray",
        "phenotype_skin_mid_gray",
        "phenotype_skin_gray_black",
        "phenotype_skin_bright_red",
        "phenotype_skin_bright_orange",
        "phenotype_skin_bright_yellow",
        "phenotype_skin_bright_green",
        "phenotype_skin_bright_teal",
        "phenotype_skin_bright_blue",
        "phenotype_skin_bright_violet",
        "phenotype_skin_bright_purple",
        "phenotype_skin_bright_pink",
        "phenotype_skin_bright_salmon",
        "phenotype_skin_dark_red",
        "phenotype_skin_dark_orange",
        "phenotype_skin_dark_yellow",
        "phenotype_skin_dark_green",
        "phenotype_skin_dark_teal",
        "phenotype_skin_dark_blue",
        "phenotype_skin_dark_violet",
        "phenotype_skin_dark_purple",
        "phenotype_skin_dark_pink",
        "phenotype_skin_dark_salmon",
        "phenotype_skin_toxic_green",
        "phenotype_skin_aqua",
        "phenotype_skin_swamp",
        "phenotype_skin_jungle",
        "phenotype_skin_polar",
        "phenotype_skin_savanna",
        "phenotype_skin_corrupted",
        "phenotype_skin_infernal",
        "phenotype_skin_lemon",
        "phenotype_skin_desert",
        "phenotype_skin_crystal",
        "phenotype_skin_candy",
        "phenotype_skin_soil",
        "phenotype_skin_wood",
        "phenotype_skin_pink_yellow_mushroom",
        "phenotype_skin_black_blue",
        "phenotype_skin_magical"
    ],
    "unlocked_traits_clan": [
        "mark_of_becoming",
        "blood_pact",
        "deathbound",
        "stonefists",
        "blood_of_sea",
        "gaia_shield",
        "iron_will",
        "flesh_weavers",
        "endurance_of_titans",
        "void_ban",
        "warlocks_vein",
        "witchs_vein",
        "blood_of_eons",
        "blood_of_giants",
        "silver_tongues",
        "masters_of_propaganda",
        "gods_chosen",
        "divine_dozen",
        "best_five",
        "geb"
    ],
    "unlocked_traits_kingdom": [
        "tax_rate_local_high",
        "tax_rate_local_low",
        "tax_rate_tribute_high",
        "tax_rate_tribute_low"
    ],
    "unlocked_traits_religion": [
        "cast_silence",
        "summon_lightning",
        "summon_tornado",
        "cast_curse",
        "cast_fire",
        "cast_blood_rain",
        "cast_grass_seeds",
        "spawn_vegetation",
        "cast_shield",
        "cast_cure",
        "sands_of_ruin",
        "shadowroot",
        "echo_of_the_void",
        "infernal_rot",
        "cosmic_radiation",
        "minds_awakening",
        "zeal_of_conquest",
        "path_of_unity",
        "hand_of_order",
        "rite_of_change",
        "rite_of_tempest_call",
        "rite_of_infernal_wrath",
        "rite_of_the_abyss",
        "rite_of_infinite_edges",
        "rite_of_restless_dead",
        "rite_of_unbroken_shield",
        "rite_of_entanglement",
        "rite_of_living_harvest",
        "divine_insight",
        "bloodline_bond"
    ],
    "unlocked_equipment": [
        "armor_leather",
        "armor_copper",
        "armor_bronze",
        "armor_silver",
        "armor_iron",
        "armor_steel",
        "armor_mythril",
        "armor_adamantine",
        "boots_leather",
        "boots_copper",
        "boots_bronze",
        "boots_silver",
        "boots_iron",
        "boots_steel",
        "boots_mythril",
        "boots_adamantine",
        "helmet_leather",
        "helmet_copper",
        "helmet_bronze",
        "helmet_silver",
        "helmet_iron",
        "helmet_steel",
        "helmet_mythril",
        "helmet_adamantine",
        "ring_bone",
        "ring_copper",
        "ring_bronze",
        "ring_silver",
        "ring_iron",
        "ring_steel",
        "ring_mythril",
        "ring_adamantine",
        "amulet_bone",
        "amulet_copper",
        "amulet_bronze",
        "amulet_silver",
        "amulet_iron",
        "amulet_steel",
        "amulet_mythril",
        "amulet_adamantine",
        "stick_wood",
        "bow_wood",
        "bow_copper",
        "bow_bronze",
        "bow_silver",
        "bow_iron",
        "bow_steel",
        "bow_mythril",
        "bow_adamantine",
        "sword_wood",
        "sword_stone",
        "sword_copper",
        "sword_bronze",
        "sword_silver",
        "sword_iron",
        "sword_steel",
        "sword_mythril",
        "sword_adamantine",
        "axe_wood",
        "axe_stone",
        "axe_copper",
        "axe_bronze",
        "axe_silver",
        "axe_iron",
        "axe_steel",
        "axe_mythril",
        "axe_adamantine",
        "spear_wood",
        "spear_stone",
        "spear_copper",
        "spear_bronze",
        "spear_silver",
        "spear_iron",
        "spear_steel",
        "spear_mythril",
        "spear_adamantine",
        "hammer_wood",
        "hammer_stone",
        "hammer_copper",
        "hammer_bronze",
        "hammer_silver",
        "hammer_iron",
        "hammer_steel",
        "hammer_mythril",
        "hammer_adamantine",
        "flame_sword",
        "necromancer_staff",
        "evil_staff",
        "white_staff",
        "plague_doctor_staff",
        "druid_staff",
        "boat_cannonball",
        "boat_arrow",
        "boat_snowball",
        "boat_plasma_ball",
        "boat_necro_ball",
        "boat_fireball",
        "boat_freeze_ball",
        "boat_acid_ball",
        "base_attack",
        "hands",
        "fire_hands",
        "jaws",
        "claws",
        "snowball",
        "bite",
        "rocks"
    ],
    "unlocked_genes": [
        "bad",
        "bonus_male",
        "bonus_female",
        "mutagenic",
        "birth_rate_1",
        "offspring_1",
        "offspring_2",
        "offspring_3",
        "offspring_4",
        "lifespan_1",
        "lifespan_2",
        "lifespan_3",
        "lifespan_4",
        "health_1",
        "health_2",
        "health_3",
        "health_4",
        "health_5",
        "stamina_1",
        "stamina_2",
        "stamina_3",
        "speed_1",
        "speed_2",
        "speed_3",
        "armor_1",
        "armor_2",
        "armor_3",
        "damage_1",
        "damage_2",
        "damage_3",
        "diplomacy_1",
        "diplomacy_2",
        "diplomacy_3",
        "warfare_1",
        "warfare_2",
        "warfare_3",
        "stewardship_1",
        "stewardship_2",
        "stewardship_3",
        "intelligence_1",
        "intelligence_2",
        "intelligence_3"
    ],
    "unlocked_actors": [
        "buffalo",
        "hyena",
        "crocodile",
        "rhino",
        "snake",
        "raccoon",
        "ostrich",
        "unicorn",
        "rat",
        "penguin",
        "armadillo",
        "alpaca",
        "capybara",
        "goat",
        "scorpion",
        "turtle",
        "crystal_sword",
        "smore",
        "acid_blob",
        "flower_bud",
        "lemon_snail",
        "garl",
        "jumpy_skull",
        "fire_elemental",
        "fire_elemental_blob",
        "fire_elemental_horse",
        "fire_elemental_slug",
        "fire_elemental_snake",
        "ghost",
        "fire_skull",
        "fairy",
        "snowman",
        "alien",
        "civ_cat",
        "civ_dog",
        "civ_chicken",
        "civ_rabbit",
        "civ_monkey",
        "civ_fox",
        "civ_sheep",
        "civ_cow",
        "civ_armadillo",
        "civ_wolf",
        "civ_bear",
        "civ_rhino",
        "civ_buffalo",
        "civ_hyena",
        "civ_rat",
        "civ_alpaca",
        "civ_capybara",
        "civ_goat",
        "civ_scorpion",
        "civ_crab",
        "civ_penguin",
        "civ_turtle",
        "civ_crocodile",
        "civ_snake",
        "civ_frog",
        "civ_piranha",
        "civ_liliar",
        "civ_garlic_man",
        "civ_lemon_man",
        "civ_acid_gentleman",
        "civ_crystal_golem",
        "civ_candy_man",
        "civ_beetle",
        "civ_seal",
        "civ_unicorn",
        "tumor_monster_unit",
        "tumor_monster_animal",
        "lil_pumpkin",
        "assimilator",
        "bioblob"
    ],
    "unlocked_plots": [
        "rebellion",
        "new_war",
        "alliance_create",
        "alliance_join",
        "alliance_destroy",
        "attacker_stop_war",
        "new_book",
        "new_language",
        "new_religion",
        "new_culture",
        "clan_ascension",
        "culture_divide",
        "religion_schism",
        "language_divergence",
        "summon_meteor_rain",
        "summon_earthquake",
        "summon_thunderstorm",
        "summon_stormfront",
        "summon_hellstorm",
        "summon_demons",
        "summon_angles",
        "summon_skeletons",
        "summon_living_plants",
        "big_cast_coffee",
        "big_cast_bubble_shield",
        "big_cast_madness",
        "big_cast_slowness",
        "cause_rebellion"
    ]
}


def derive_key_pdb(password_bytes: bytes, key_len: int = 32) -> bytes:
    """Replica PasswordDeriveBytes(password, null) (SHA1, 100 iteracoes)."""
    base = password_bytes
    for _ in range(99):
        base = hashlib.sha1(base).digest()
    out = bytearray(hashlib.sha1(base).digest())
    counter = 1
    while len(out) < key_len:
        out.extend(hashlib.sha1(str(counter).encode("ascii") + base).digest())
        counter += 1
    return bytes(out[:key_len])


KEY = derive_key_pdb(PASS_PHRASE, 32)


def decode_worldbox(encoded_text: str) -> str:
    ciphertext = base64.b64decode(encoded_text)
    decryptor = Cipher(algorithms.AES(KEY), modes.CBC(INIT_VECTOR)).decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded) + unpadder.finalize()
    return plaintext.decode("utf-8")


def encode_worldbox(plain_text: str) -> str:
    padder = padding.PKCS7(128).padder()
    padded = padder.update(plain_text.encode("utf-8")) + padder.finalize()
    encryptor = Cipher(algorithms.AES(KEY), modes.CBC(INIT_VECTOR)).encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    return base64.b64encode(ciphertext).decode("ascii")


def load_progress() -> dict:
    if not PROGRESS_FILE.exists():
        raise FileNotFoundError(f"Arquivo de progresso nao encontrado: {PROGRESS_FILE}")
    raw = PROGRESS_FILE.read_text(encoding="utf-8")
    return json.loads(decode_worldbox(raw))


def save_progress(data: dict, dry_run: bool = False) -> None:
    backup_file = PROGRESS_FILE.with_name(PROGRESS_FILE.name + ".bak")
    if not dry_run:
        if not backup_file.exists():
            shutil.copy2(PROGRESS_FILE, backup_file)
            print(f"[Backup] Criado em: {backup_file}")
        else:
            print(f"[Backup] Original preservado em: {backup_file}")

    updated_json = json.dumps(data, indent=2, ensure_ascii=False).replace("\n", "\r\n")
    if dry_run:
        total_hidden = sum(len(data.get(k, [])) for k in HIDDEN_ITEMS_NO_ACHIEVEMENT)
        print(
            f"[Dry-Run] worldboxProgress seria atualizado "
            f"({len(data.get('achievements', []))} conquistas, {total_hidden} itens desbloqueados)."
        )
        return

    encrypted = encode_worldbox(updated_json)
    PROGRESS_FILE.write_text(encrypted, encoding="utf-8", newline="")
    print(f"[Local] Arquivo atualizado: {PROGRESS_FILE}")


class _NullContext:
    initialized = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


class SteamClientSession:
    """Wrapper leve da steam_api64.dll para consultar e desbloquear conquistas na Steam."""

    def __init__(self, dll_path: pathlib.Path = STEAM_API_DLL) -> None:
        self.dll_path = dll_path
        self.dll: Optional[ctypes.CDLL] = None
        self.stats_ptr: Optional[int] = None
        self.initialized = False

    def __enter__(self) -> "SteamClientSession":
        if not self.dll_path.exists():
            print(f"[Steam] DLL nao encontrada: {self.dll_path}")
            return self

        os.environ["SteamAppId"] = STEAM_APP_ID
        os.environ["SteamGameId"] = STEAM_APP_ID

        self.dll = ctypes.CDLL(str(self.dll_path))
        self.dll.SteamAPI_Init.restype = ctypes.c_bool
        if not self.dll.SteamAPI_Init():
            print("[Steam] Nao foi possivel conectar ao cliente Steam (verifique se a Steam esta aberta e logada).")
            return self

        self.initialized = True
        self.dll.SteamAPI_SteamUserStats_v011.restype = ctypes.c_void_p
        self.stats_ptr = self.dll.SteamAPI_SteamUserStats_v011()
        if not self.stats_ptr:
            print("[Steam] Falha ao obter ponteiro ISteamUserStats.")
            return self

        self.dll.SteamAPI_ISteamUserStats_RequestCurrentStats.argtypes = [ctypes.c_void_p]
        self.dll.SteamAPI_ISteamUserStats_RequestCurrentStats.restype = ctypes.c_bool
        self.dll.SteamAPI_ISteamUserStats_GetNumAchievements.argtypes = [ctypes.c_void_p]
        self.dll.SteamAPI_ISteamUserStats_GetNumAchievements.restype = ctypes.c_uint32
        self.dll.SteamAPI_ISteamUserStats_GetAchievementName.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        self.dll.SteamAPI_ISteamUserStats_GetAchievementName.restype = ctypes.c_char_p
        self.dll.SteamAPI_ISteamUserStats_GetAchievement.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_bool),
        ]
        self.dll.SteamAPI_ISteamUserStats_GetAchievement.restype = ctypes.c_bool
        self.dll.SteamAPI_ISteamUserStats_SetAchievement.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.dll.SteamAPI_ISteamUserStats_SetAchievement.restype = ctypes.c_bool
        self.dll.SteamAPI_ISteamUserStats_StoreStats.argtypes = [ctypes.c_void_p]
        self.dll.SteamAPI_ISteamUserStats_StoreStats.restype = ctypes.c_bool
        self.dll.SteamAPI_ISteamUserStats_GetAchievementDisplayAttribute.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]
        self.dll.SteamAPI_ISteamUserStats_GetAchievementDisplayAttribute.restype = ctypes.c_char_p

        self.dll.SteamAPI_ISteamUserStats_RequestCurrentStats(self.stats_ptr)
        for _ in range(15):
            self.dll.SteamAPI_RunCallbacks()
            time.sleep(0.05)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.initialized and self.dll is not None:
            for _ in range(10):
                self.dll.SteamAPI_RunCallbacks()
                time.sleep(0.05)
            self.dll.SteamAPI_Shutdown()
            self.initialized = False

    def get_steam_achievements(self) -> Dict[str, Tuple[str, bool]]:
        """Retorna {api_id: (display_name, unlocked)}."""
        result: Dict[str, Tuple[str, bool]] = {}
        if not self.initialized or not self.stats_ptr or self.dll is None:
            return result

        count = self.dll.SteamAPI_ISteamUserStats_GetNumAchievements(self.stats_ptr)
        for i in range(count):
            raw_name = self.dll.SteamAPI_ISteamUserStats_GetAchievementName(self.stats_ptr, i)
            if not raw_name:
                continue
            api_id = raw_name.decode("utf-8", errors="replace")
            achieved = ctypes.c_bool(False)
            self.dll.SteamAPI_ISteamUserStats_GetAchievement(self.stats_ptr, raw_name, ctypes.byref(achieved))
            disp_raw = self.dll.SteamAPI_ISteamUserStats_GetAchievementDisplayAttribute(
                self.stats_ptr, raw_name, b"name"
            )
            disp_name = disp_raw.decode("utf-8", errors="replace") if disp_raw else api_id
            result[api_id] = (disp_name, bool(achieved.value))
        return result

    def unlock_achievements(self, ids: List[str], dry_run: bool = False) -> Tuple[int, List[str]]:
        """Desbloqueia os IDs validos na Steam e executa StoreStats."""
        if not self.initialized or not self.stats_ptr or self.dll is None:
            return 0, []

        steam_map = self.get_steam_achievements()
        unlocked_now: List[str] = []
        for ach_id in ids:
            if ach_id not in steam_map:
                continue
            _, already = steam_map[ach_id]
            if already:
                continue
            if dry_run:
                unlocked_now.append(ach_id)
                continue
            ok = self.dll.SteamAPI_ISteamUserStats_SetAchievement(self.stats_ptr, ach_id.encode("utf-8"))
            if ok:
                unlocked_now.append(ach_id)

        if unlocked_now and not dry_run:
            stored = self.dll.SteamAPI_ISteamUserStats_StoreStats(self.stats_ptr)
            for _ in range(20):
                self.dll.SteamAPI_RunCallbacks()
                time.sleep(0.05)
            print(f"[Steam] StoreStats enviado (sucesso={stored}) para {len(unlocked_now)} conquista(s).")
        elif dry_run and unlocked_now:
            print(f"[Dry-Run] {len(unlocked_now)} conquista(s) seriam desbloqueadas na Steam.")

        return len(unlocked_now), unlocked_now


def build_catalog(local_set: Set[str], steam_map: Dict[str, Tuple[str, bool]]) -> List[dict]:
    seen: Set[str] = set()
    catalog: List[dict] = []

    for ach_id in IN_GAME_ACHIEVEMENTS:
        seen.add(ach_id)
        steam_info = steam_map.get(ach_id)
        catalog.append(
            {
                "id": ach_id,
                "in_game": True,
                "local_unlocked": ach_id in local_set,
                "in_steam": steam_info is not None,
                "steam_name": steam_info[0] if steam_info else "-",
                "steam_unlocked": steam_info[1] if steam_info else False,
            }
        )

    for ach_id, (disp_name, s_unlocked) in sorted(steam_map.items()):
        if ach_id in seen:
            continue
        catalog.append(
            {
                "id": ach_id,
                "in_game": False,
                "local_unlocked": ach_id in local_set,
                "in_steam": True,
                "steam_name": disp_name,
                "steam_unlocked": s_unlocked,
            }
        )

    return catalog


def print_catalog(catalog: List[dict]) -> None:
    print("\n#  | ID da Conquista                       | Local | Steam | Nome na Steam")
    print("-" * 92)
    for idx, entry in enumerate(catalog, start=1):
        loc = "SIM" if entry["local_unlocked"] else ("NAO" if entry["in_game"] else "N/A")
        stm = "SIM" if entry["steam_unlocked"] else ("NAO" if entry["in_steam"] else "N/A")
        print(f"{idx:2d} | {entry['id']:37s} | {loc:5s} | {stm:5s} | {entry['steam_name']}")

    loc_total = sum(1 for e in catalog if e["in_game"])
    loc_done = sum(1 for e in catalog if e["in_game"] and e["local_unlocked"])
    stm_total = sum(1 for e in catalog if e["in_steam"])
    stm_done = sum(1 for e in catalog if e["in_steam"] and e["steam_unlocked"])
    print("-" * 92)
    print(f"Resumo Conquistas -> Local: {loc_done}/{loc_total} | Steam: {stm_done}/{stm_total}\n")


def print_hidden_summary(data: dict) -> None:
    print("\n=== Resumo dos Itens Ocultos (Sem Conquista) ===")
    total_all = 0
    done_all = 0
    for idx, (cat_key, items) in enumerate(HIDDEN_ITEMS_NO_ACHIEVEMENT.items(), start=1):
        prog_set = set(data.get(cat_key, []))
        done = sum(1 for x in items if x in prog_set)
        total = len(items)
        total_all += total
        done_all += done
        label = CATEGORY_LABELS.get(cat_key, cat_key)
        print(f"{idx:2d} | {cat_key:26s} | {done:3d}/{total:3d} | {label}")
    print(f"Total geral: {done_all}/{total_all} desbloqueados.\n")


def print_hidden_items(data: dict, category: Optional[str] = None) -> None:
    cats = [category] if category else list(HIDDEN_ITEMS_NO_ACHIEVEMENT.keys())
    for cat_key in cats:
        if cat_key not in HIDDEN_ITEMS_NO_ACHIEVEMENT:
            print(f"[Aviso] Categoria desconhecida: {cat_key}")
            continue
        items = HIDDEN_ITEMS_NO_ACHIEVEMENT[cat_key]
        prog_set = set(data.get(cat_key, []))
        label = CATEGORY_LABELS.get(cat_key, cat_key)
        done = sum(1 for x in items if x in prog_set)
        print(f"\n--- {cat_key} ({label}) [{done}/{len(items)}] ---")
        for idx, item_id in enumerate(items, start=1):
            status = "SIM" if item_id in prog_set else "NAO"
            print(f"  {idx:3d}. [{status}] {item_id}")


def resolve_achievement_targets(queries: List[str], catalog: List[dict]) -> List[dict]:
    resolved: List[dict] = []
    seen_ids: Set[str] = set()

    for q in queries:
        q_clean = q.strip()
        if not q_clean:
            continue

        if q_clean.isdigit():
            idx = int(q_clean)
            if 1 <= idx <= len(catalog):
                item = catalog[idx - 1]
                if item["id"] not in seen_ids:
                    resolved.append(item)
                    seen_ids.add(item["id"])
                continue

        exact = [e for e in catalog if e["id"].lower() == q_clean.lower()]
        if exact:
            for item in exact:
                if item["id"] not in seen_ids:
                    resolved.append(item)
                    seen_ids.add(item["id"])
            continue

        q_norm = q_clean.lower().replace("_", "")
        matches = [
            e
            for e in catalog
            if q_clean.lower() in e["id"].lower()
            or q_norm in e["id"].lower()
            or q_clean.lower() in e["steam_name"].lower()
        ]
        if len(matches) == 1:
            item = matches[0]
            if item["id"] not in seen_ids:
                resolved.append(item)
                seen_ids.add(item["id"])
        elif len(matches) > 1:
            print(f"[Aviso] Termo '{q_clean}' corresponde a multiplas conquistas:")
            for m in matches:
                print(f"  - {m['id']} ({m['steam_name']})")
        else:
            print(f"[Aviso] Nenhuma conquista encontrada para '{q_clean}'.")

    return resolved


def resolve_hidden_targets(queries: List[str], category_filter: Optional[str] = None) -> List[Tuple[str, str]]:
    """Resolve consultas para lista de (categoria, item_id). Aceita 'categoria:id', 'id' exato ou busca parcial."""
    all_pairs: List[Tuple[str, str]] = []
    cats = [category_filter] if category_filter else list(HIDDEN_ITEMS_NO_ACHIEVEMENT.keys())
    for cat_key in cats:
        if cat_key in HIDDEN_ITEMS_NO_ACHIEVEMENT:
            for item_id in HIDDEN_ITEMS_NO_ACHIEVEMENT[cat_key]:
                all_pairs.append((cat_key, item_id))

    resolved: List[Tuple[str, str]] = []
    seen: Set[Tuple[str, str]] = set()

    for q in queries:
        q_clean = q.strip()
        if not q_clean:
            continue

        target_cat = category_filter
        term = q_clean
        if ":" in q_clean:
            left, right = q_clean.split(":", 1)
            if left in HIDDEN_ITEMS_NO_ACHIEVEMENT:
                target_cat = left
                term = right

        pool = [p for p in all_pairs if (target_cat is None or p[0] == target_cat)]

        if target_cat and term.isdigit():
            idx = int(term)
            if 1 <= idx <= len(pool):
                pair = pool[idx - 1]
                if pair not in seen:
                    resolved.append(pair)
                    seen.add(pair)
                continue

        exact = [p for p in pool if p[1].lower() == term.lower()]
        if exact:
            for pair in exact:
                if pair not in seen:
                    resolved.append(pair)
                    seen.add(pair)
            continue

        matches = [p for p in pool if term.lower() in p[1].lower()]
        if len(matches) == 1:
            pair = matches[0]
            if pair not in seen:
                resolved.append(pair)
                seen.add(pair)
        elif len(matches) > 1:
            print(f"[Aviso] Termo '{q_clean}' corresponde a {len(matches)} itens ocultos:")
            for cat_k, item_id in matches[:15]:
                print(f"  - {cat_k}:{item_id}")
            if len(matches) > 15:
                print(f"  ... e mais {len(matches) - 15} ocorrencia(s). Use categoria:id para especificar.")
        else:
            print(f"[Aviso] Nenhum item oculto encontrado para '{q_clean}'.")

    return resolved


def apply_unlock_achievements(
    targets: List[dict],
    do_local: bool = True,
    do_steam: bool = True,
    dry_run: bool = False,
    steam_session: Optional[SteamClientSession] = None,
) -> None:
    if not targets:
        print("Nenhuma conquista selecionada para desbloqueio.")
        return

    data = load_progress()
    achievements_list: List[str] = data.setdefault("achievements", [])
    local_set = set(achievements_list)

    added_local: List[str] = []
    steam_candidates: List[str] = []

    for item in targets:
        ach_id = item["id"]
        if do_local and item["in_game"] and ach_id not in local_set:
            achievements_list.append(ach_id)
            local_set.add(ach_id)
            added_local.append(ach_id)
        if do_steam and item["in_steam"]:
            steam_candidates.append(ach_id)

    if do_local:
        if added_local:
            print(f"[Local] Adicionadas {len(added_local)} conquista(s) ao worldboxProgress:")
            for aid in added_local:
                print(f"  + {aid}")
            save_progress(data, dry_run=dry_run)
        else:
            print("[Local] Todas as conquistas selecionadas ja estavam desbloqueadas no worldboxProgress.")

    if do_steam:
        if steam_candidates:
            if steam_session is not None and steam_session.initialized:
                count, unlocked_steam = steam_session.unlock_achievements(steam_candidates, dry_run=dry_run)
                if count:
                    print(f"[Steam] Desbloqueadas {count} conquista(s) na Steam:")
                    for aid in unlocked_steam:
                        print(f"  + {aid}")
                else:
                    print("[Steam] Todas as conquistas selecionadas que existem na Steam ja estavam desbloqueadas.")
            else:
                print("[Steam] Cliente Steam indisponivel no momento; sincronize abrindo o jogo ou com a Steam ativa.")
        else:
            print("[Steam] Nenhuma das conquistas selecionadas possui registro na Steam (apenas in-game).")


def apply_unlock_hidden(
    pairs: List[Tuple[str, str]],
    dry_run: bool = False,
) -> None:
    if not pairs:
        print("Nenhum item oculto selecionado para desbloqueio.")
        return

    data = load_progress()
    added_by_cat: Dict[str, List[str]] = {}

    for cat_key, item_id in pairs:
        cat_list: List[str] = data.setdefault(cat_key, [])
        if item_id not in cat_list:
            cat_list.append(item_id)
            added_by_cat.setdefault(cat_key, []).append(item_id)

    total_added = sum(len(v) for v in added_by_cat.values())
    if total_added == 0:
        print("[Itens Ocultos] Todos os itens selecionados ja estavam desbloqueados.")
        return

    print(f"[Itens Ocultos] Adicionados {total_added} novo(s) item(ns) ao worldboxProgress:")
    for cat_key, added_ids in added_by_cat.items():
        if len(added_ids) <= 10:
            print(f"  * {cat_key} (+{len(added_ids)}): {', '.join(added_ids)}")
        else:
            print(f"  * {cat_key} (+{len(added_ids)}): {', '.join(added_ids[:5])}, ...")

    save_progress(data, dry_run=dry_run)


def interactive_menu(do_local: bool, do_steam: bool, dry_run: bool) -> None:
    with SteamClientSession() as steam:
        while True:
            data = load_progress()
            local_set = set(data.get("achievements", []))
            steam_map = steam.get_steam_achievements() if steam.initialized else {}
            catalog = build_catalog(local_set, steam_map)

            loc_done = sum(1 for e in catalog if e["in_game"] and e["local_unlocked"])
            loc_total = sum(1 for e in catalog if e["in_game"])
            stm_done = sum(1 for e in catalog if e["in_steam"] and e["steam_unlocked"])
            stm_total = sum(1 for e in catalog if e["in_steam"])

            hid_total = sum(len(v) for v in HIDDEN_ITEMS_NO_ACHIEVEMENT.values())
            hid_done = sum(
                sum(1 for x in items if x in set(data.get(k, [])))
                for k, items in HIDDEN_ITEMS_NO_ACHIEVEMENT.items()
            )

            print("\n=== Gerenciador Completo do WorldBox (Conquistas + Steam + Itens Ocultos) ===")
            print(
                f"Status -> Conquistas Local: {loc_done}/{loc_total} | Steam: {stm_done}/{stm_total} | "
                f"Itens Ocultos: {hid_done}/{hid_total}"
            )
            print("1) Listar conquistas (Local + Steam)")
            print("2) Desbloquear conquista(s) unitariamente (Local + Steam)")
            print("3) Desbloquear TODAS as conquistas de uma vez (Local + Steam)")
            print("4) Sincronizar conquistas ja desbloqueadas localmente para a Steam")
            print("5) Listar itens ocultos sem conquista (resumo ou categoria)")
            print("6) Desbloquear item(ns) oculto(s) unitariamente (por ID, categoria:id ou busca)")
            print("7) Desbloquear todos os itens ocultos de uma categoria")
            print("8) Desbloquear TODOS os itens ocultos sem conquista (658 itens)")
            print("9) Desbloquear TUDO de uma vez (Conquistas + Steam + Todos os Itens Ocultos)")
            print("0) Sair")

            choice = input("Escolha uma opcao: ").strip()
            if choice == "0":
                break
            elif choice == "1":
                print_catalog(catalog)
            elif choice == "2":
                raw = input("Informe indice(s), ID(s) ou parte do nome (separados por virgula): ").strip()
                queries = [x.strip() for x in raw.split(",") if x.strip()]
                targets = resolve_achievement_targets(queries, catalog)
                apply_unlock_achievements(
                    targets, do_local=do_local, do_steam=do_steam, dry_run=dry_run, steam_session=steam
                )
            elif choice == "3":
                confirm = input("Desbloquear TODAS as conquistas no save local e na Steam? [s/N]: ").strip().lower()
                if confirm in {"s", "sim", "y", "yes"}:
                    apply_unlock_achievements(
                        catalog, do_local=do_local, do_steam=do_steam, dry_run=dry_run, steam_session=steam
                    )
                else:
                    print("Operacao cancelada.")
            elif choice == "4":
                to_sync = [e for e in catalog if e["local_unlocked"] and e["in_steam"] and not e["steam_unlocked"]]
                apply_unlock_achievements(
                    to_sync, do_local=False, do_steam=True, dry_run=dry_run, steam_session=steam
                )
            elif choice == "5":
                print_hidden_summary(data)
                cat_in = input("Digite numero/nome da categoria para detalhar (ou Enter para voltar): ").strip()
                if cat_in:
                    cats = list(HIDDEN_ITEMS_NO_ACHIEVEMENT.keys())
                    cat_sel = cats[int(cat_in) - 1] if cat_in.isdigit() and 1 <= int(cat_in) <= len(cats) else cat_in
                    print_hidden_items(data, cat_sel)
            elif choice == "6":
                raw = input("Informe ID(s), categoria:id ou parte do nome (separados por virgula): ").strip()
                queries = [x.strip() for x in raw.split(",") if x.strip()]
                pairs = resolve_hidden_targets(queries)
                apply_unlock_hidden(pairs, dry_run=dry_run)
            elif choice == "7":
                print_hidden_summary(data)
                cat_in = input("Escolha o numero ou nome da categoria para desbloquear inteira: ").strip()
                cats = list(HIDDEN_ITEMS_NO_ACHIEVEMENT.keys())
                cat_sel = cats[int(cat_in) - 1] if cat_in.isdigit() and 1 <= int(cat_in) <= len(cats) else cat_in
                if cat_sel in HIDDEN_ITEMS_NO_ACHIEVEMENT:
                    pairs = [(cat_sel, x) for x in HIDDEN_ITEMS_NO_ACHIEVEMENT[cat_sel]]
                    apply_unlock_hidden(pairs, dry_run=dry_run)
                else:
                    print("Categoria invalida.")
            elif choice == "8":
                confirm = input(f"Desbloquear TODOS os {hid_total} itens ocultos no worldboxProgress? [s/N]: ").strip().lower()
                if confirm in {"s", "sim", "y", "yes"}:
                    all_pairs = [(k, x) for k, items in HIDDEN_ITEMS_NO_ACHIEVEMENT.items() for x in items]
                    apply_unlock_hidden(all_pairs, dry_run=dry_run)
                else:
                    print("Operacao cancelada.")
            elif choice == "9":
                confirm = input("Desbloquear TUDO (Conquistas + Steam + 658 Itens Ocultos)? [s/N]: ").strip().lower()
                if confirm in {"s", "sim", "y", "yes"}:
                    apply_unlock_achievements(
                        catalog, do_local=do_local, do_steam=do_steam, dry_run=dry_run, steam_session=steam
                    )
                    all_pairs = [(k, x) for k, items in HIDDEN_ITEMS_NO_ACHIEVEMENT.items() for x in items]
                    apply_unlock_hidden(all_pairs, dry_run=dry_run)
                else:
                    print("Operacao cancelada.")
            else:
                print("Opcao invalida.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Desbloqueia conquistas (Local + Steam) e itens ocultos sem conquista do WorldBox."
    )
    parser.add_argument("--list", action="store_true", help="Lista todas as conquistas e seus status (Local e Steam).")
    parser.add_argument(
        "--unlock",
        nargs="+",
        metavar="ID_OU_NOME",
        help="Desbloqueia uma ou mais conquistas (indice, ID exato ou busca parcial).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Desbloqueia TODAS as conquistas (86 no worldboxProgress + 54 na Steam).",
    )
    parser.add_argument(
        "--sync-steam",
        action="store_true",
        help="Sincroniza para a Steam as conquistas ja desbloqueadas no worldboxProgress.",
    )
    parser.add_argument("--list-hidden", action="store_true", help="Lista itens ocultos que nao dependem de conquista.")
    parser.add_argument(
        "--category",
        metavar="CATEGORIA",
        help="Filtra ou seleciona uma categoria de itens ocultos (ex: unlocked_genes, unlocked_actors).",
    )
    parser.add_argument(
        "--unlock-hidden",
        nargs="+",
        metavar="ITEM",
        help="Desbloqueia item(ns) oculto(s) unitariamente (ID, categoria:id ou busca parcial).",
    )
    parser.add_argument(
        "--all-hidden",
        action="store_true",
        help="Desbloqueia todos os 658 itens ocultos sem conquista (ou todos da --category especificada).",
    )
    parser.add_argument(
        "--all-everything",
        action="store_true",
        help="Desbloqueia TUDO de uma vez: todas as conquistas (Local + Steam) e todos os 658 itens ocultos.",
    )
    parser.add_argument("--local-only", action="store_true", help="Altera apenas o arquivo local worldboxProgress.")
    parser.add_argument("--steam-only", action="store_true", help="Envia conquistas apenas para a Steam.")
    parser.add_argument("--dry-run", action="store_true", help="Simula a execucao sem gravar alteracoes.")
    args = parser.parse_args()

    do_local = not args.steam_only
    do_steam = not args.local_only

    has_action = any(
        [
            args.list,
            args.unlock,
            args.all,
            args.sync_steam,
            args.list_hidden,
            args.unlock_hidden,
            args.all_hidden,
            args.all_everything,
        ]
    )

    if not has_action:
        interactive_menu(do_local=do_local, do_steam=do_steam, dry_run=args.dry_run)
        return

    if args.list_hidden:
        data = load_progress()
        if args.category:
            print_hidden_items(data, args.category)
        else:
            print_hidden_summary(data)
        return

    if args.unlock_hidden:
        pairs = resolve_hidden_targets(args.unlock_hidden, category_filter=args.category)
        apply_unlock_hidden(pairs, dry_run=args.dry_run)
        return

    if args.all_hidden:
        if args.category:
            if args.category not in HIDDEN_ITEMS_NO_ACHIEVEMENT:
                raise ValueError(f"Categoria invalida: {args.category}")
            pairs = [(args.category, x) for x in HIDDEN_ITEMS_NO_ACHIEVEMENT[args.category]]
        else:
            pairs = [(k, x) for k, items in HIDDEN_ITEMS_NO_ACHIEVEMENT.items() for x in items]
        apply_unlock_hidden(pairs, dry_run=args.dry_run)
        return

    need_steam = do_steam or args.list
    with SteamClientSession() if need_steam else _NullContext() as steam:
        data = load_progress()
        local_set = set(data.get("achievements", []))
        steam_map = steam.get_steam_achievements() if (steam and steam.initialized) else {}
        catalog = build_catalog(local_set, steam_map)

        if args.list:
            print_catalog(catalog)
            return

        if args.all or args.all_everything:
            apply_unlock_achievements(
                catalog, do_local=do_local, do_steam=do_steam, dry_run=args.dry_run, steam_session=steam
            )
            if args.all_everything:
                all_pairs = [(k, x) for k, items in HIDDEN_ITEMS_NO_ACHIEVEMENT.items() for x in items]
                apply_unlock_hidden(all_pairs, dry_run=args.dry_run)
            return

        if args.sync_steam:
            to_sync = [e for e in catalog if e["local_unlocked"] and e["in_steam"] and not e["steam_unlocked"]]
            apply_unlock_achievements(
                to_sync, do_local=False, do_steam=True, dry_run=args.dry_run, steam_session=steam
            )
            return

        if args.unlock:
            targets = resolve_achievement_targets(args.unlock, catalog)
            apply_unlock_achievements(
                targets, do_local=do_local, do_steam=do_steam, dry_run=args.dry_run, steam_session=steam
            )


if __name__ == "__main__":
    main()
