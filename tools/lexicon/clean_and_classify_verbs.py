#!/usr/bin/env python3
"""
Clean verb lexicon and assign linguistically accurate conjugation classes.

This script:
1. Removes non-infinitive entries (conjugated forms, participles, truncations)
2. Assigns correct verb classes: regular, stem_change, irregular, modal
3. Adds English translations (placeholder)
4. Outputs schema-compliant YAML

Author: Wortschatzspiel Project
Date: 2026-01-12
"""

import yaml
import re
from pathlib import Path
from datetime import date

# === LINGUISTIC CLASSIFICATION DATA ===

# Modal verbs (special conjugation, always irregular)
MODAL_VERBS = {
    'dürfen', 'können', 'mögen', 'müssen', 'sollen', 'wollen'
}

# Irregular verbs (unpredictable patterns)
IRREGULAR_VERBS = {
    'sein', 'haben', 'werden', 'wissen', 'tun',
    'gehen', 'stehen', 'bringen', 'denken', 'kennen', 'nennen', 'rennen',
    'brennen', 'senden', 'wenden'
}

# Stem-change verbs: a→ä
STEM_CHANGE_A_AE = {
    'fahren', 'abfahren', 'losfahren', 'mitfahren', 'wegfahren', 'hinfahren',
    'tragen', 'schlagen', 'waschen', 'wachsen', 'laden', 'einladen', 'ausladen',
    'fangen', 'anfangen', 'fallen', 'gefallen', 'auffallen', 'einfallen',
    'halten', 'anhalten', 'aufhalten', 'festhalten', 'behalten', 'erhalten',
    'lassen', 'verlassen', 'zulassen', 'entlassen',
    'schlafen', 'einschlafen', 'verschlafen',
    'laufen', 'ablaufen', 'weglaufen',
    'graben', 'backen', 'braten', 'raten', 'geraten', 'verraten',
    'blasen', 'stoßen'
}

# Stem-change verbs: e→i
STEM_CHANGE_E_I = {
    'geben', 'abgeben', 'angeben', 'ausgeben', 'vergeben', 'zugeben', 'aufgeben',
    'nehmen', 'annehmen', 'aufnehmen', 'mitnehmen', 'teilnehmen', 'abnehmen', 'zunehmen',
    'sprechen', 'ansprechen', 'aussprechen', 'besprechen', 'versprechen',
    'treffen', 'helfen', 'sterben', 'werfen', 'verbergen',
    'brechen', 'zerbrechen', 'unterbrechen',
    'erschrecken', 'essen', 'fressen', 'messen', 'vergessen',
    'treten', 'betreten', 'vertreten', 'eintreten', 'austreten'
}

# Stem-change verbs: e→ie
STEM_CHANGE_E_IE = {
    'sehen', 'ansehen', 'aussehen', 'fernsehen', 'nachsehen', 'wiedersehen', 'absehen',
    'lesen', 'vorlesen', 'durchlesen',
    'empfehlen', 'befehlen', 'stehlen',
    'geschehen'
}

# Strong verbs (irregular past, but may have regular present)
STRONG_VERBS = {
    'beginnen', 'gewinnen', 'schwimmen', 'finden', 'erfinden', 'binden', 'verbinden',
    'singen', 'trinken', 'sinken', 'springen', 'klingen', 'zwingen',
    'bleiben', 'schreiben', 'beschreiben', 'unterschreiben', 'treiben', 'vertreiben',
    'steigen', 'einsteigen', 'aussteigen', 'umsteigen',
    'schweigen', 'reiten', 'schneiden', 'entscheiden', 'leiden', 'meiden',
    'fliegen', 'abfliegen', 'biegen', 'abbiegen',
    'liegen', 'ziehen', 'anziehen', 'ausziehen', 'umziehen', 'einziehen',
    'bieten', 'anbieten', 'verbieten',
    'fließen', 'genießen', 'gießen', 'schließen', 'abschließen', 'beschließen',
    'verlieren', 'frieren', 'rufen', 'anrufen',
    'kommen', 'ankommen', 'bekommen', 'mitkommen', 'zurückkommen'
}

# Entries to REMOVE (not valid infinitives)
INVALID_ENTRIES = {
    'ableitbaren',
    'associ',
    'ausgewählten',
    'begeg',
    'bist',
    'brauchst',
    'bekommsen',
    'fahr',
    'findest',
    'frühstück',
    'gebraucht',
    'gemeinsam',
    'gebären',
}

# Entries to CORRECT (misspellings)
CORRECTIONS = {
    'gefällen': 'gefallen',
}

# English translations
TRANSLATIONS = {
    'abfahren': 'to depart, leave',
    'abfliegen': 'to take off (plane)',
    'abgeben': 'to hand in, submit',
    'abholen': 'to pick up, collect',
    'anerkennen': 'to recognize, acknowledge',
    'anfangen': 'to begin, start',
    'anführen': 'to lead, cite',
    'anklicken': 'to click on',
    'ankommen': 'to arrive',
    'ankreuzen': 'to mark with a cross',
    'anmachen': 'to turn on',
    'anmelden': 'to register, sign up',
    'anrufen': 'to call (phone)',
    'antworten': 'to answer',
    'anziehen': 'to put on (clothes), attract',
    'arbeiten': 'to work',
    'aufhören': 'to stop, cease',
    'auflisten': 'to list',
    'aufstehen': 'to get up, stand up',
    'ausfüllen': 'to fill out',
    'ausmachen': 'to turn off, matter',
    'ausnehmen': 'to exclude, gut (fish)',
    'aussehen': 'to look, appear',
    'aussteigen': 'to get off, exit',
    'ausziehen': 'to take off (clothes), move out',
    'baden': 'to bathe, swim',
    'bedeuten': 'to mean, signify',
    'befinden': 'to be located, feel',
    'begegnen': 'to meet, encounter',
    'beginnen': 'to begin',
    'bekommen': 'to receive, get',
    'benutzen': 'to use',
    'besetzen': 'to occupy',
    'besichtigen': 'to visit, tour',
    'bestellen': 'to order',
    'besuchen': 'to visit',
    'bezahlen': 'to pay',
    'bezeichnen': 'to designate, call',
    'bilden': 'to form, educate',
    'bitten': 'to ask, request',
    'bleiben': 'to stay, remain',
    'brauchen': 'to need',
    'bringen': 'to bring',
    'buchstabieren': 'to spell',
    'danken': 'to thank',
    'dauern': 'to last, take (time)',
    'denken': 'to think',
    'dokumentieren': 'to document',
    'drucken': 'to print',
    'drücken': 'to press, push',
    'dürfen': 'to be allowed to, may',
    'einkaufen': 'to shop',
    'einladen': 'to invite',
    'einsteigen': 'to get in, board',
    'empfehlen': 'to recommend',
    'enden': 'to end',
    'enthalten': 'to contain',
    'entschuldigen': 'to excuse, apologize',
    'erbringen': 'to produce, provide',
    'erfolgen': 'to occur, take place',
    'erfüllen': 'to fulfill',
    'ergänzen': 'to complete, supplement',
    'erklären': 'to explain',
    'erlauben': 'to allow, permit',
    'ermöglichen': 'to enable, make possible',
    'erschließen': 'to open up, develop',
    'erzählen': 'to tell, narrate',
    'essen': 'to eat',
    'fahren': 'to drive, go (by vehicle)',
    'fallen': 'to fall',
    'fangen': 'to catch',
    'fehlen': 'to be missing, lack',
    'feiern': 'to celebrate',
    'finden': 'to find',
    'fliegen': 'to fly',
    'folgen': 'to follow',
    'fragen': 'to ask',
    'freuen': 'to be happy, please',
    'frühstücken': 'to have breakfast',
    'geben': 'to give',
    'gefallen': 'to please, like',
    'gehen': 'to go, walk',
    'gehören': 'to belong',
    'gewinnen': 'to win',
    'glauben': 'to believe',
    'gratulieren': 'to congratulate',
    'haben': 'to have',
    'halten': 'to hold, stop',
    'heißen': 'to be called',
    'helfen': 'to help',
    'hören': 'to hear',
    'kaufen': 'to buy',
    'kennen': 'to know (person/thing)',
    'kommen': 'to come',
    'können': 'to be able to, can',
    'kosten': 'to cost',
    'lassen': 'to let, leave',
    'laufen': 'to run, walk',
    'leben': 'to live',
    'legen': 'to lay, put',
    'lernen': 'to learn',
    'lesen': 'to read',
    'lieben': 'to love',
    'liegen': 'to lie, be located',
    'machen': 'to make, do',
    'meinen': 'to mean, think',
    'mögen': 'to like',
    'müssen': 'to must, have to',
    'nehmen': 'to take',
    'nennen': 'to name, call',
    'öffnen': 'to open',
    'passen': 'to fit, suit',
    'passieren': 'to happen',
    'rauchen': 'to smoke',
    'rechnen': 'to calculate',
    'reden': 'to talk',
    'reisen': 'to travel',
    'sagen': 'to say',
    'schaffen': 'to manage, create',
    'schauen': 'to look',
    'schenken': 'to give (as gift)',
    'schicken': 'to send',
    'schlafen': 'to sleep',
    'schließen': 'to close',
    'schmecken': 'to taste',
    'schreiben': 'to write',
    'schwimmen': 'to swim',
    'sehen': 'to see',
    'sein': 'to be',
    'setzen': 'to set, put',
    'singen': 'to sing',
    'sitzen': 'to sit',
    'sollen': 'should, ought to',
    'spielen': 'to play',
    'sprechen': 'to speak',
    'stehen': 'to stand',
    'stellen': 'to put, place',
    'stimmen': 'to be correct, vote',
    'studieren': 'to study (at university)',
    'suchen': 'to search, look for',
    'tanzen': 'to dance',
    'tragen': 'to carry, wear',
    'treffen': 'to meet',
    'treiben': 'to do (sports), drive',
    'trinken': 'to drink',
    'tun': 'to do',
    'üben': 'to practice',
    'vergessen': 'to forget',
    'vergleichen': 'to compare',
    'verkaufen': 'to sell',
    'verlieren': 'to lose',
    'verstehen': 'to understand',
    'versuchen': 'to try',
    'warten': 'to wait',
    'waschen': 'to wash',
    'wechseln': 'to change, exchange',
    'werden': 'to become',
    'wiederholen': 'to repeat',
    'wissen': 'to know (fact)',
    'wohnen': 'to live, reside',
    'wollen': 'to want',
    'wünschen': 'to wish',
    'zahlen': 'to pay',
    'zeigen': 'to show',
    'ziehen': 'to pull, move',
}


def classify_verb(lemma: str) -> str:
    """Assign correct conjugation class based on linguistic rules."""
    if lemma in MODAL_VERBS:
        return 'modal'
    if lemma in IRREGULAR_VERBS:
        return 'irregular'
    if lemma in STEM_CHANGE_A_AE:
        return 'stem_change_a_ae'
    if lemma in STEM_CHANGE_E_I:
        return 'stem_change_e_i'
    if lemma in STEM_CHANGE_E_IE:
        return 'stem_change_e_ie'
    if lemma in STRONG_VERBS:
        return 'strong'
    
    # Check for compound verbs (separable prefix + known stem)
    prefixes = ['ab', 'an', 'auf', 'aus', 'bei', 'ein', 'mit', 'nach', 
                'vor', 'zu', 'zurück', 'weg', 'hin', 'her', 'los', 'fest',
                'weiter', 'über', 'unter', 'um', 'durch', 'wieder']
    
    for prefix in sorted(prefixes, key=len, reverse=True):
        if lemma.startswith(prefix) and len(lemma) > len(prefix) + 2:
            stem = lemma[len(prefix):]
            stem_class = classify_verb(stem)
            if stem_class != 'regular':
                return stem_class
    
    return 'regular'


def is_valid_infinitive(lemma: str) -> bool:
    """Check if entry appears to be a valid German infinitive."""
    if lemma in INVALID_ENTRIES:
        return False
    
    # German infinitives typically end in -en, -ern, or -eln
    if not (lemma.endswith('en') or lemma.endswith('ern') or lemma.endswith('eln')):
        return False
    
    # Reject very short entries
    if len(lemma) < 4:
        return False
    
    # Reject entries with unusual characters
    if not re.match(r'^[a-zäöüß]+$', lemma.lower()):
        return False
    
    return True


def generate_item_id(index: int) -> str:
    """Generate schema-compliant item ID."""
    return f"A1-V-{index:04d}"


def clean_and_classify_verbs(input_path: str, output_path: str):
    """Main processing function."""
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    cleaned_items = []
    removed_items = []
    corrected_items = []
    seen_lemmas = set()
    item_index = 1
    
    # Track classification counts for report
    class_counts = {
        'regular': 0,
        'stem_change_a_ae': 0,
        'stem_change_e_i': 0,
        'stem_change_e_ie': 0,
        'strong': 0,
        'irregular': 0,
        'modal': 0
    }
    
    missing_translations = []
    
    for item in data.get('items', []):
        lemma = item.get('lemma', '').strip().lower()
        
        # Skip empty entries
        if not lemma:
            continue
        
        # Apply corrections
        if lemma in CORRECTIONS:
            old_lemma = lemma
            lemma = CORRECTIONS[lemma]
            corrected_items.append((old_lemma, lemma))
        
        # Skip duplicates
        if lemma in seen_lemmas:
            removed_items.append((lemma, 'duplicate'))
            continue
        
        # Validate
        if not is_valid_infinitive(lemma):
            removed_items.append((lemma, 'invalid infinitive'))
            continue
        
        seen_lemmas.add(lemma)
        
        # Classify
        verb_class = classify_verb(lemma)
        class_counts[verb_class] += 1
        
        # Track missing translations
        english = TRANSLATIONS.get(lemma, '')
        if not english:
            missing_translations.append(lemma)
        
        # Build schema-compliant entry
        new_item = {
            'item_id': generate_item_id(item_index),
            'type': 'verb',
            'de': lemma,
            'en': english,
            'lemma': lemma,
            'conjugation_class': verb_class,
            'seen_in_course': item.get('seen_in_course', False),
            'notes': item.get('notes', ''),
            'source': item.get('source', 'cefr_a1_core')
        }
        
        cleaned_items.append(new_item)
        item_index += 1
    
    # Build output structure
    output_data = {
        'schema': 'lexical_schema_v1',
        'language': 'de',
        'cefr_level': 'A1',
        'source': 'cefr_a1_core',
        'last_updated': str(date.today()),
        'items': cleaned_items
    }
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(output_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
        # Generate report
    print("\n" + "=" * 60)
    print("VERB LEXICON CLEANUP REPORT")
    print("=" * 60)
    print(f"Input file:  {input_path}")
    print(f"Output file: {output_path}")
    print("-" * 60)
    print(f"Input items:    {len(data.get('items', []))}")
    print(f"Output items:   {len(cleaned_items)}")
    print(f"Removed:        {len(removed_items)}")
    print(f"Corrected:      {len(corrected_items)}")
    print("-" * 60)
    
    print("\nCLASSIFICATION DISTRIBUTION:")
    for verb_class, count in sorted(class_counts.items()):
        if count > 0:
            print(f"  {verb_class}: {count}")
    
    print(f"\nMISSING TRANSLATIONS: {len(missing_translations)}")
    if missing_translations and len(missing_translations) <= 20:
        for lemma in missing_translations:
            print(f"  - {lemma}")
    elif missing_translations:
        print(f"  (First 20 shown)")
        for lemma in missing_translations[:20]:
            print(f"  - {lemma}")
    
    if removed_items:
        print("\nREMOVED ENTRIES:")
        for lemma, reason in removed_items:
            print(f"  - {lemma} ({reason})")
    
    if corrected_items:
        print("\nCORRECTED ENTRIES:")
        for old, new in corrected_items:
            print(f"  - {old} → {new}")
    
    print("\n" + "=" * 60)
    print("CLEANUP COMPLETE")
    print("=" * 60)


def main():
    """Entry point."""
    input_path = Path("linguistic_rules/lexicon/verbs.yaml")
    output_path = Path("linguistic_rules/lexicon/verbs_cleaned.yaml")
    
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        return
    
    clean_and_classify_verbs(str(input_path), str(output_path))
    
    print(f"\nNext steps:")
    print(f"  1. Review {output_path}")
    print(f"  2. If satisfied, replace original:")
    print(f"     mv {output_path} {input_path}")
    print(f"  3. Commit changes:")
    print(f"     git add {input_path}")
    print(f"     git commit -m 'Phase 1: Verb lexicon cleaned and classified'")


if __name__ == "__main__":
    main()
