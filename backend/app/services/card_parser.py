"""
Card text parser and effect executor.
Handles all card abilities: primary, ally, scrap, paid effects.
"""
import re
from typing import List, Dict, Any, Optional
from enum import Enum


class EffectType(str, Enum):
    """Types of card effects."""
    GAIN_COMBAT = "gain_combat"
    GAIN_TRADE = "gain_trade"
    GAIN_AUTHORITY = "gain_authority"
    DRAW_CARDS = "draw_cards"
    DISCARD_CARD = "discard_card"
    SCRAP_CARD = "scrap_card"
    DESTROY_BASE = "destroy_base"
    OPTIONAL = "optional"  # "You may..." effects
    CHOICE = "choice"  # "Or" effects
    CONDITIONAL = "conditional"  # "If you have X bases..." effects
    NEXT_ACQUIRE_TO_TOP = "next_acquire_to_top"  # "put next ship/base you acquire on top of deck"
    ACQUIRE_FREE_TO_TOP = "acquire_free_to_top"  # "acquire a ship/base for free, put on top of deck"
    BASE_FROM_DISCARD_TO_TOP = "base_from_discard_to_top"  # "put a base from discard on top of deck"
    GAIN_COMBAT_PER_SCRAPPED = "gain_combat_per_scrapped"  # × scrapped_this_turn
    DRAW_PER_FACTION_PLAYED = "draw_per_faction_played"    # × faction_played_count[faction]
    DISCARD_ANY_NUMBER = "discard_any_number"              # discard N cards, gain per each
    COPY_SHIP = "copy_ship"                                # copy another ship played this turn


class ParsedAbility:
    """A parsed card ability."""
    def __init__(self, text: str):
        self.text = text
        self.effects: List[Dict[str, Any]] = []
        self.is_optional = False
        self.is_choice = False
        self._parse()

    def _parse(self):
        """Parse the ability text into structured effects."""
        text = self.text

        # Check if optional
        if text.lower().startswith('you may'):
            self.is_optional = True

        # Check if choice (OR) — only split when OR separates two effect clauses.
        # Valid: "{Gain X} OR {Gain Y}", "{Gain X} OR\nDo something"
        # Invalid: "ship or base", "two or more", "hand or discard"
        or_match = re.split(r'(\{[^}]+\}|[^\s]+)\s+OR\s+(?!more\b|less\b|discard\b|base\b)', text, maxsplit=1, flags=re.IGNORECASE)
        # re.split with a capturing group returns [before, captured, after] — reassemble if needed
        if len(or_match) == 3:
            or_match = [or_match[0] + or_match[1], or_match[2]]
        else:
            or_match = re.split(r'\s+OR\s+', text, maxsplit=1, flags=re.IGNORECASE)
            # Validate it's not a noun-phrase OR (ship or base, hand or discard, two or more)
            if len(or_match) == 2:
                before_word = or_match[0].strip().split()[-1].lower() if or_match[0].strip() else ''
                after_word = or_match[1].strip().split()[0].lower() if or_match[1].strip() else ''
                noun_words = {'base', 'bases', 'discard', 'more', 'less', 'an', 'a', 'any'}
                if before_word in noun_words or after_word in noun_words:
                    or_match = [text]  # don't split
        if len(or_match) == 2:
            self.is_choice = True
            option_a = ParsedAbility(or_match[0].strip())
            option_b = ParsedAbility(or_match[1].strip())
            # Only emit a choice if both sides parsed at least one known effect
            if option_a.effects and option_b.effects:
                self.effects.append({
                    'type': EffectType.CHOICE,
                    'options': [option_a.effects, option_b.effects],
                    'labels': [or_match[0].strip(), or_match[1].strip()],
                    'optional': self.is_optional,
                })
                return
            # Fallback: unknown option shape, parse whole text normally

        self._parse_effects(text)

    def _extract_for_each_effects(self, text: str):
        """Extract effects that apply 'for each card scrapped/played this way'."""
        m = re.search(r'(draw\s+a\s+card|gain\s+\{(\d+)\s+Combat\})\s+for each', text, re.IGNORECASE)
        if not m:
            return []
        if 'draw' in m.group(1).lower():
            return [{'type': EffectType.DRAW_CARDS, 'amount': 1}]
        else:
            return [{'type': EffectType.GAIN_COMBAT, 'amount': int(m.group(2))}]

    def _parse_effects(self, text: str):
        """Extract individual effects from a text segment."""
        # Strip conditional clauses from main text so they don't parse as standalone effects.
        # Keep original for blocks that need to find the clauses.
        original_text = text

        # "If you have N or more bases in play, <effects>" — extract as conditional
        bases_cond = re.search(
            r'if you have\s+(\w+)\s+or more bases in play,?\s+(.*)',
            text, re.IGNORECASE | re.DOTALL
        )
        if bases_cond:
            num_word = bases_cond.group(1).lower()
            word_to_num_local = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}
            min_bases = word_to_num_local.get(num_word, int(num_word) if num_word.isdigit() else 2)
            cond_text = bases_cond.group(2).strip()
            cond_ability = ParsedAbility(cond_text)
            if cond_ability.effects:
                self.effects.append({
                    'type': EffectType.CONDITIONAL,
                    'condition': 'min_bases',
                    'min_bases': min_bases,
                    'effects': cond_ability.effects,
                })
            text = re.sub(r'if you have\s+\w+\s+or more bases in play,?.*', '', text, flags=re.IGNORECASE | re.DOTALL).strip()

        text = re.sub(r'\.\s*if you do,?.*', '', text, flags=re.IGNORECASE).strip()

        # "copy another ship" — Stealth Needle
        if re.search(r'copy another ship', text, re.IGNORECASE):
            self.effects.append({'type': EffectType.COPY_SHIP})
            return

        # "gain {X Combat} for each ... scrapped this turn" — Reclamation Station
        scrapped_turn_m = re.search(
            r'gain\s+\{(\d+)\s+Combat\}\s+for each.*?scrapped this turn',
            text, re.IGNORECASE
        )
        if scrapped_turn_m:
            self.effects.append({'type': EffectType.GAIN_COMBAT_PER_SCRAPPED, 'amount': int(scrapped_turn_m.group(1))})
            return

        # "discard any number of cards and gain {X Combat} for each"
        discard_any_m = re.search(
            r'discard any number of cards and gain\s+\{(\d+)\s+Combat\}\s+for each',
            text, re.IGNORECASE
        )
        if discard_any_m:
            per_combat = int(discard_any_m.group(1))
            draw_after = re.search(r'\.\s*draw\s+a\s+card', text, re.IGNORECASE)
            on_complete = [{'type': EffectType.DRAW_CARDS, 'amount': 1}] if draw_after else []
            self.effects.append({
                'type': EffectType.DISCARD_ANY_NUMBER,
                'per_discard_effects': [{'type': EffectType.GAIN_COMBAT, 'amount': per_combat}],
                'on_complete_effects': on_complete,
            })
            return

        # Extract gain combat — matches "{Gain 4 Combat}" and "gain {4 Combat}"
        combat_matches = re.findall(r'(?:\{Gain\s+(\d+)\s+Combat\}|gain\s+\{(\d+)\s+Combat\})', text, re.IGNORECASE)
        for m1, m2 in combat_matches:
            self.effects.append({'type': EffectType.GAIN_COMBAT, 'amount': int(m1 or m2)})

        # Extract gain trade
        trade_matches = re.findall(r'(?:\{Gain\s+(\d+)\s+Trade\}|gain\s+\{(\d+)\s+Trade\})', text, re.IGNORECASE)
        for m1, m2 in trade_matches:
            self.effects.append({'type': EffectType.GAIN_TRADE, 'amount': int(m1 or m2)})

        # Extract gain authority
        authority_matches = re.findall(r'(?:\{Gain\s+(\d+)\s+Authority\}|gain\s+\{(\d+)\s+Authority\})', text, re.IGNORECASE)
        for m1, m2 in authority_matches:
            self.effects.append({'type': EffectType.GAIN_AUTHORITY, 'amount': int(m1 or m2)})

        # "draw a card for each X card" — Blob World
        faction_draw_m = re.search(
            r"draw\s+a\s+card\s+for\s+each\s+(\w+)\s+card",
            text, re.IGNORECASE
        )
        if faction_draw_m:
            faction_name = faction_draw_m.group(1).capitalize()
            self.effects.append({'type': EffectType.DRAW_PER_FACTION_PLAYED, 'faction': faction_name})
            text = re.sub(r"draw\s+a\s+card\s+for\s+each\s+\w+\s+card[^.]*", '', text, flags=re.IGNORECASE)

        # Extract Draw effects — handles "draw a card", "draw 1 card", "draw two cards", "draw 2 cards"
        word_to_num = {'a': 1, 'an': 1, 'one': 1, 'two': 2, 'three': 3, 'four': 4}
        draw_matches = re.findall(r'draw\s+(\d+|a|an|one|two|three|four)\s+cards?(?!\s+for each)', text, re.IGNORECASE)
        for match in draw_matches:
            m = match.lower()
            amount = word_to_num.get(m, int(m) if m.isdigit() else 1)
            self.effects.append({'type': EffectType.DRAW_CARDS, 'amount': amount})

        # Extract self-discard effects ("then discard a card", "discard a card")
        # Distinct from opponent-discard — targets self
        self_discard = re.findall(
            r'(?:then\s+)?discard\s+(\d+|a|an|one|two|three|four)\s+cards?',
            text, re.IGNORECASE
        )
        for match in self_discard:
            m = match.lower()
            amount = word_to_num.get(m, int(m) if m.isdigit() else 1)
            self.effects.append({'type': EffectType.DISCARD_CARD, 'target': 'self', 'amount': amount, 'optional': False})

        # Extract opponent discard effects
        if 'opponent discards' in text.lower() or 'target opponent discards' in text.lower() or 'target player discards' in text.lower():
            self.effects.append({
                'type': EffectType.DISCARD_CARD,
                'target': 'opponent',
                'optional': 'may' in text.lower()
            })

        # Extract scrap effects — "scrap a card" (single) or "scrap up to N cards"
        scrap_count_match = re.search(r'scrap\s+up\s+to\s+(\d+|two|three)\s+cards?', text, re.IGNORECASE)
        if scrap_count_match:
            m = scrap_count_match.group(1).lower()
            count = word_to_num.get(m, int(m) if m.isdigit() else 1)
            location = 'hand_or_discard'
            if 'in the trade row' in text.lower():
                location = 'trade_row'
            scrap_effect = {
                'type': EffectType.SCRAP_CARD,
                'location': location,
                'max_count': count,
                'optional': True,
            }
            for_each = self._extract_for_each_effects(text)
            if for_each:
                scrap_effect['for_each_effects'] = for_each
            self.effects.append(scrap_effect)
        elif 'scrap a card' in text.lower():
            location = 'hand'
            if 'in the trade row' in text.lower():
                location = 'trade_row'
            elif 'in your hand or discard' in text.lower():
                location = 'hand_or_discard'
            elif 'in your discard' in text.lower():
                location = 'discard'

            scrap_effect = {
                'type': EffectType.SCRAP_CARD,
                'location': location,
                'optional': 'may' in text.lower()
            }

            # "gain {Combat} equal to its cost" — applied after scrap resolves
            if 'equal to its cost' in text.lower():
                scrap_effect['gain_cost_as_combat'] = True

            # "draw/gain X for each card scrapped this way"
            for_each = self._extract_for_each_effects(text)
            if for_each:
                scrap_effect['for_each_effects'] = for_each
                scrap_effect['max_count'] = scrap_effect.get('max_count', 1)

            # "if you do, gain {X Combat/Trade/Authority}" — conditional bonus after scrap
            if_you_do = re.search(
                r'if you do,?\s*(.*)',
                original_text, re.IGNORECASE
            )
            if if_you_do:
                bonus_text = if_you_do.group(1).strip()
                bonus_ability = ParsedAbility(bonus_text)
                if bonus_ability.effects:
                    scrap_effect['on_resolve_effects'] = bonus_ability.effects

            self.effects.append(scrap_effect)

        # Extract destroy base effect
        if 'destroy target base' in text.lower() or 'destroy any base' in text.lower():
            self.effects.append({
                'type': EffectType.DESTROY_BASE,
                'optional': 'may' in text.lower()
            })

        # "put the next ship/base you acquire this turn on top of your deck"
        next_top = re.search(
            r'put the next (ship|base|ship or base)\s+you acquire.*?on top of your deck',
            text, re.IGNORECASE
        )
        if next_top:
            card_type = next_top.group(1).lower().replace(' or ', '_or_')
            self.effects.append({
                'type': EffectType.NEXT_ACQUIRE_TO_TOP,
                'card_type': card_type,  # 'ship', 'base', or 'ship_or_base'
                'optional': 'may' in text.lower()
            })

        # "acquire a/any ship/base/ship or base [of cost X or less] for free ... top of your deck"
        if 'acquire' in text.lower() and 'for free' in text.lower() and 'top of your deck' in text.lower():
            cost_match = re.search(r'of cost\s+(\w+)\s+or less', text, re.IGNORECASE)
            cost_words = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8}
            if cost_match:
                c = cost_match.group(1).lower()
                max_cost = cost_words.get(c, int(c) if c.isdigit() else 999)
            else:
                max_cost = 999
            tl = text.lower()
            if 'ship or base' in tl or 'base or ship' in tl:
                card_type = 'ship_or_base'
            elif 'base' in tl:
                card_type = 'base'
            else:
                card_type = 'ship'
            self.effects.append({
                'type': EffectType.ACQUIRE_FREE_TO_TOP,
                'card_type': card_type,
                'max_cost': max_cost,
            })

        # "put a base from your discard pile on top of your deck"
        if 'base from your discard pile on top of your deck' in text.lower():
            self.effects.append({
                'type': EffectType.BASE_FROM_DISCARD_TO_TOP,
                'optional': 'may' in text.lower()
            })


class ParsedCard:
    """A card with all its abilities parsed."""
    def __init__(self, card_text: str, faction: str):
        self.faction = faction
        self.primary_ability: Optional[ParsedAbility] = None
        self.ally_ability: Optional[ParsedAbility] = None
        self.double_ally_ability: Optional[ParsedAbility] = None
        self.scrap_ability: Optional[ParsedAbility] = None
        self.paid_abilities: List[Dict[str, Any]] = []

        self._parse(card_text)

    def _parse(self, text: str):
        """Parse card text into separate abilities."""
        if not text or text == 'nan':
            return

        # Split by <hr> tags
        sections = re.split(r'\s*<hr>\s*', text)

        for section in sections:
            section = section.strip()
            if not section:
                continue

            # Scrap ability: {Scrap}: effect
            if section.lower().startswith('{scrap}'):
                ability_text = re.sub(r'\{scrap\}:?\s*', '', section, flags=re.IGNORECASE)
                self.scrap_ability = ParsedAbility(ability_text)

            # Double ally ability
            elif '{double' in section.lower() and 'ally}' in section.lower():
                match = re.search(r'\{Double\s+[^}]+\s+Ally\}:?\s*(.*)', section, re.IGNORECASE | re.DOTALL)
                if match:
                    ability_text = match.group(1).strip()
                    self.double_ally_ability = ParsedAbility(ability_text)

            # Regular ally ability
            elif 'ally}' in section.lower():
                match = re.search(r'\{[^}]+\s+Ally\}:?\s*(.*)', section, re.IGNORECASE | re.DOTALL)
                if match:
                    ability_text = match.group(1).strip()
                    self.ally_ability = ParsedAbility(ability_text)

            # Paid ability: Pay {X}: effect
            elif section.lower().startswith('pay {'):
                match = re.search(r'Pay\s+\{([^}]+)\}:?\s*(.*)', section, re.IGNORECASE | re.DOTALL)
                if match:
                    cost = match.group(1).strip()
                    ability_text = match.group(2).strip()
                    self.paid_abilities.append({
                        'cost': cost,
                        'ability': ParsedAbility(ability_text)
                    })

            # Primary ability (first section or any section with direct effects)
            else:
                if not self.primary_ability:
                    self.primary_ability = ParsedAbility(section)

    def get_primary_effects(self) -> List[Dict[str, Any]]:
        """Get primary ability effects."""
        return self.primary_ability.effects if self.primary_ability else []

    def get_ally_effects(self, ally_count: int) -> List[Dict[str, Any]]:
        """Get ally effects based on number of same-faction cards in play."""
        effects = []

        if ally_count >= 1 and self.ally_ability:
            effects.extend(self.ally_ability.effects)

        if ally_count >= 2 and self.double_ally_ability:
            effects.extend(self.double_ally_ability.effects)

        return effects

    def has_scrap_ability(self) -> bool:
        """Check if card has a scrap ability."""
        return self.scrap_ability is not None

    def get_scrap_effects(self) -> List[Dict[str, Any]]:
        """Get scrap ability effects."""
        return self.scrap_ability.effects if self.scrap_ability else []


def parse_card(card_text: str, faction: str) -> ParsedCard:
    """Parse a card's text into structured abilities."""
    return ParsedCard(card_text, faction)


# Test the parser
if __name__ == '__main__':
    test_cards = [
        ("Scout", "{Gain 1 Trade}", "Unaligned"),
        ("Viper", "{Gain 1 Combat}", "Unaligned"),
        ("Explorer", "{Gain 2 Trade}\n<hr>\n{Scrap}: {Gain 2 Combat}", "Unaligned"),
        ("Battle Pod", "{Gain 4 Combat}\nYou may scrap a card in the trade row.\n<hr>\n{Blob Ally}: {Gain 2 Combat}", "Blob"),
        ("Blob Fighter", "{Gain 3 Combat}\n<hr>\n{Blob Ally}: Draw a card.", "Blob"),
        ("Ram", "{Gain 5 Combat}\n<hr>\n{Blob Ally}: {Gain 2 Combat}\n<hr>\n{Scrap}: {Gain 3 Trade}", "Blob"),
    ]

    for name, text, faction in test_cards:
        print(f"\n=== {name} ===")
        parsed = parse_card(text, faction)
        print(f"Primary effects: {parsed.get_primary_effects()}")
        print(f"Ally effects (1): {parsed.get_ally_effects(1)}")
        print(f"Ally effects (2): {parsed.get_ally_effects(2)}")
        if parsed.has_scrap_ability():
            print(f"Scrap effects: {parsed.get_scrap_effects()}")
