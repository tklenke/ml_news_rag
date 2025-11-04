# ABOUTME: LLM configuration for keyword extraction and tagging
# ABOUTME: Defines Ollama host, model settings, and prompt templates

# LLM Configuration
OLLAMA_HOST = "http://localhost:11434"
LLM_MODEL = "gemma3:1b"  # Tom can edit this as needed
#LLM_MODEL = "mistral-openorca:7b"  # Tom can edit this as needed
LLM_TIMEOUT = 30.0  # Timeout in seconds for LLM requests (default: 30s)

# Prompt template for keyword extraction (Phase 4a)
KEYWORD_EXTRACTION_PROMPT = """You are a very exact librarian tasked with analyzing aircraft 
builder messages to build a keyword vocabulary.

The existing list of keywords is: {keywords}

Extract all aircraft-building related keywords from this message.

Message: {message}

Return keywords as a comma-separated list. Focus on:
- Aircraft parts (firewall, cowling, canard, etc.)
- Tools and materials (epoxy, aluminum, fiberglass, etc.)
- Processes (layup, installation, painting, etc.)
- Systems (engine, fuel, electrical, etc.)

Return only the keywords, no explanations, No puntuation. If there is an error, return a 
blank line."""

CHAPTER_CATEGORIZATION_PROMPT = """
Classify this aircraft builder message into the appropriate chapter number(s) from the Cozy IV plans. Return ONLY the chapter number(s), nothing else.

CHAPTER REFERENCE:
1: Introduction, newsletter, bill of materials, ordering information
2: Workshop setup, tools, jigs, workbench construction
3: Education - basic composite techniques, practice layups, epoxy work, fiberglass, foam cutting
4: Fuselage bulkheads - firewall, F22, F28, instrument panel, front seat, rear seat bulkheads
5: Fuselage sides - foam preparation, interior layups, longerons, LWX, LWY reinforcements
6: Fuselage assembly - joining sides, bulkhead installation, bottom, heat duct, landing brake
7: Fuselage exterior - NACA scoop, contouring, bottom attach, step installation
8: Rollover structure, headrest, shoulder support, seat belts, pilot restraints
9: Main landing gear strut - gear leg construction, trailing link, attachment
10: Landing gear cover, wheel wells, gear leg fairings, brake lines
11: Elevators - canard mounting, elevator construction, hinges, torque tubes
12: Canard construction - foam cores, shear web, spar caps, tips
13: Nose gear - strut, steering, shimmy damper, nose wheel, retract mechanism
14: Center section spar - main wing attach, CS spar construction, hard points
15: Firewall preparation, engine mount points, cowling attachment
16: Control system - stick, rudder pedals, cables, pushrods, bellcranks, aileron controls
17: Pitch trim, roll trim, springs, trim handles
18: Canopy - frame, glass, hinges, latch, opening mechanism
19: Wings - cores, spars, shear web, hard points, attach fittings
20: Winglets, rudders - construction, hinges, cable connections, antennas
21: Fuel tanks - strakes, fuel system, sumps, vents, fuel lines, gauges
22: Electrical system, wiring, instruments, avionics, panel, switches, lights
23: Engine installation - baffling, cooling, cowling, exhaust, propeller, spinner
24: Covers, fairings, wheel pants, intersection fairings, doors
25: Finishing - filling, sanding, primer, paint, weight and balance, inspection

MESSAGE:
{message}
"""
# Prompt template for keyword tagging (Phase 4b)
KEYWORD_TAGGING_PROMPT = """You are analyzing aircraft builder messages. Given this list of keywords, return ONLY the keywords that are relevant to the message below.

Keywords: {keywords}

Message: {message}

Return the matching keywords as a comma-separated list. If no keywords match, return "NONE". Do not include explanations or extra text."""
