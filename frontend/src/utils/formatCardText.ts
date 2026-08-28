/**
 * Format card text for better readability.
 */

export interface FormattedAbility {
  label: string;
  text: string;
  type: 'primary' | 'ally' | 'double_ally' | 'scrap' | 'paid';
}

export function hasScrapAbility(text: string): boolean {
  if (!text) return false;
  return text.toLowerCase().includes('{scrap}:') || text.toLowerCase().includes('{scrap}');
}

export function formatCardText(text: string): FormattedAbility[] {
  if (!text) return [];

  const abilities: FormattedAbility[] = [];

  // Split by <hr> tags
  const sections = text.split(/<hr>/i).map(s => s.trim());

  sections.forEach((section) => {
    if (!section) return;

    // Clean up formatting
    section = section
      .replace(/\{Gain/g, '+')
      .replace(/\}/g, '')
      .replace(/\{/g, '')
      .replace(/\n/g, ' ');

    // Scrap ability
    if (section.toLowerCase().includes('scrap:')) {
      const abilityText = section.replace(/scrap:/i, '').trim();
      abilities.push({
        label: '🗑️ Scrap',
        text: abilityText,
        type: 'scrap',
      });
    }
    // Double ally
    else if (section.toLowerCase().includes('double') && section.toLowerCase().includes('ally')) {
      const match = section.match(/^(.*?)\s*Double\s+(Trade Federation|Machine Cult|Star Empire|Blob)\s+Ally:?\s*(.*)/i);
      if (match) {
        const prefix = match[1].trim();
        const faction = match[2].trim();
        const abilityText = match[3].trim();
        if (prefix) {
          abilities.push({ label: '', text: prefix, type: 'primary' });
        }
        abilities.push({
          label: `⭐⭐ ${faction}`,
          text: abilityText,
          type: 'double_ally',
        });
      }
    }
    // Regular ally
    else if (section.toLowerCase().includes('ally')) {
      const match = section.match(/^(.*?)\s*(Trade Federation|Machine Cult|Star Empire|Blob)\s+Ally:?\s*(.*)/i);
      if (match) {
        const prefix = match[1].trim();
        const faction = match[2].trim();
        const abilityText = match[3].trim();
        if (prefix) {
          abilities.push({ label: '', text: prefix, type: 'primary' });
        }
        abilities.push({
          label: `⭐ ${faction}`,
          text: abilityText,
          type: 'ally',
        });
      }
    }
    // Paid ability
    else if (section.toLowerCase().startsWith('pay')) {
      const match = section.match(/Pay\s+(.+?):\s*(.*)/i);
      if (match) {
        const cost = match[1].trim();
        const abilityText = match[2].trim();
        abilities.push({
          label: `💰 Pay ${cost}`,
          text: abilityText,
          type: 'paid',
        });
      }
    }
    // Primary ability
    else {
      abilities.push({
        label: '',
        text: section,
        type: 'primary',
      });
    }
  });

  return abilities;
}
