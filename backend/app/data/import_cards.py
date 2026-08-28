"""
Simple card import from cleaned Excel file.
"""
import pandas as pd
import json
from pathlib import Path


def import_cards(excel_path: str) -> dict:
    """Import cards from cleaned Excel file."""
    df = pd.read_excel(excel_path, sheet_name='Star Realms')

    cards = []

    for idx, row in df.iterrows():
        card = {
            'id': f"card_{idx}",
            'name': str(row['Name']),
            'type': str(row['Type']),
            'faction': str(row['Faction / Color']) if pd.notna(row['Faction / Color']) else 'Unaligned',
            'cost': int(row['Cost']) if pd.notna(row['Cost']) else 0,
            'defense': int(row['Defense']) if pd.notna(row['Defense']) else None,
            'is_outpost': bool(row['IsOutpost']) if pd.notna(row['IsOutpost']) else False,
            'text': str(row['Text']) if pd.notna(row['Text']) else '',
            'quantity': int(row['Qty']),
            'role': str(row['Role'])
        }

        cards.append(card)

    # Separate by role
    personal_deck = [c for c in cards if c['role'] == 'Personal Deck']
    explorer_pile = [c for c in cards if c['role'] == 'Explorer Pile']
    trade_deck = [c for c in cards if c['role'] == 'Trade Deck']

    return {
        'personal_deck': personal_deck,
        'explorer_pile': explorer_pile,
        'trade_deck': trade_deck,
        'all_cards': cards
    }


def main():
    """Import and save cards."""
    excel_path = '/Users/81035495/Downloads/Star Realms.xlsx'

    print("Importing cards from Excel...")
    data = import_cards(excel_path)

    print(f"✓ Personal Deck: {len(data['personal_deck'])} card types")
    print(f"✓ Explorer Pile: {len(data['explorer_pile'])} card types")
    print(f"✓ Trade Deck: {len(data['trade_deck'])} card types")
    print(f"✓ Total: {len(data['all_cards'])} cards")

    # Save to JSON
    output_path = Path(__file__).parent / 'cards.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved to {output_path}")

    # Print faction distribution
    factions = {}
    for card in data['trade_deck']:
        faction = card['faction']
        factions[faction] = factions.get(faction, 0) + 1

    print("\nTrade Deck by faction:")
    for faction, count in sorted(factions.items()):
        print(f"  {faction}: {count}")


if __name__ == '__main__':
    main()
