from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE = Path('/opt/data/website-zamania')
AUTOMATION_DIR = BASE / '.automation'
HISTORY_PATH = AUTOMATION_DIR / 'zamania-topic-memory.json'
DEFAULT_RULES = {
    'recent_window': 2,
    'history_window': 6,
    'high_similarity_threshold': 0.72,
    'warn_similarity_threshold': 0.55,
    'intra_batch_threshold': 0.48,
}

LOW_SIGNAL_WORDS = {
    'a', 'afin', 'ai', 'ainsi', 'alors', 'and', 'angle', 'argent', 'as', 'au', 'aucun', 'aussi', 'autour',
    'avec', 'avoir', 'business', 'car', 'cas', 'ce', 'ces', 'cet', 'cette', 'comment', 'concret', 'concrets',
    'contre', 'dans', 'de', 'decideur', 'decideurs', 'des', 'du', 'elle', 'elles', 'en', 'encore', 'entre',
    'entreprise', 'entreprises', 'est', 'et', 'etre', 'faire', 'font', 'fort', 'fr', 'gain', 'gains', 'grace',
    'growth', 'how', 'ia', 'il', 'ils', 'impact', 'intelligent', 'intelligente', 'les', 'leur', 'leurs', 'mais',
    'marge', 'mesurable', 'moins', 'new', 'nouveau', 'nous', 'notre', 'nos', 'ou', 'par', 'part', 'plus',
    'pour', 'pourquoi', 'priorite', 'processus', 'productivite', 'promesse', 'quelles', 'rentabilite', 'rentable',
    'rentables', 'roi', 'sans', 'service', 'ses', 'smart', 'son', 'sont', 'strategique', 'sur', 'the', 'un',
    'une', 'value', 'visible', 'votre', 'vos', 'where', 'who', 'yet', 'your', 'automation', 'automatisation',
    'automatiser', 'automatise', 'automatises', 'automatisee', 'automatisee', 'temps', 'argent', 'entreprise',
}

THEME_PATTERNS = {
    'manual-work-cost': [
        r'taches? repetitives?',
        r'micro[ -]?taches?',
        r'saisie manuelle',
        r'resaisie',
        r'paperasse',
        r'cout cache',
        r'fuite silencieuse',
        r'temps perdu',
        r'charge administrative',
        r'travail manuel',
    ],
    'ai-agents-productivity': [
        r'agents? ia',
        r'ai agents?',
        r'copilotes? ia',
        r'assistants? ia',
        r'faire plus sans recruter',
        r'sans recruter plus',
        r'levier de productivite',
    ],
    'automation-priorities': [
        r'quelles? taches? deleguer',
        r'deleguer en priorite',
        r'par ou commencer',
        r'5 processus',
        r'90 jours',
        r'ou automatiser',
        r'prioriser l automatisation',
    ],
    'lead-qualification': [
        r'qualification de leads?',
        r'qualification des leads?',
        r'lead scoring',
        r'mql',
        r'sql',
        r'traitement des leads?',
    ],
    'customer-support': [
        r'support client',
        r'service client',
        r'ticket',
        r'sav',
        r'helpdesk',
        r'centre d appel',
    ],
    'document-processing': [
        r'documents?',
        r'piece jointe',
        r'contrat',
        r'facture',
        r'ocr',
        r'extraction de donnees',
        r'traitement documentaire',
    ],
    'reporting-analytics': [
        r'reporting',
        r'tableaux? de bord',
        r'kpi',
        r'syntheses?',
        r'compte rendu',
        r'analyse hebdomadaire',
    ],
    'crm-data-sync': [
        r'crm',
        r'erp',
        r'synchronisation',
        r'mise a jour des donnees',
        r'donnees clients?',
    ],
}

OPEN_THEME_IDEAS = [
    'qualification de leads et réponse commerciale',
    'support client et tri automatique des demandes',
    'traitement de documents, devis, contrats ou factures',
    'reporting et synthèses automatiques pour dirigeants',
    'CRM / ERP / synchronisation des données',
    'onboarding RH et collecte documentaire',
    'relances commerciales et suivi post-devis',
]


class GuardError(Exception):
    pass


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')


def strip_accents(text: str) -> str:
    normalized = unicodedata.normalize('NFKD', text)
    return ''.join(ch for ch in normalized if not unicodedata.combining(ch))


def normalize_text(text: str) -> str:
    text = strip_accents(text or '').lower()
    text = re.sub(r'[^a-z0-9\s-]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def signal_tokens(text: str) -> set[str]:
    normalized = normalize_text(text)
    tokens = set()
    for token in normalized.split():
        if len(token) < 3 or token.isdigit() or token in LOW_SIGNAL_WORDS:
            continue
        tokens.add(token)
    if 'taches repetitives' in normalized or 'micro taches' in normalized:
        tokens.add('repetitive_work')
    if 'saisie manuelle' in normalized or 'ressaisie' in normalized:
        tokens.add('manual_entry')
    if 'agents ia' in normalized or 'agent ia' in normalized or 'ai agents' in normalized:
        tokens.add('ai_agents')
    if 'support client' in normalized or 'service client' in normalized:
        tokens.add('customer_support')
    if 'lead' in normalized and ('qualification' in normalized or 'scoring' in normalized):
        tokens.add('lead_qualification')
    if 'reporting' in normalized or 'tableau de bord' in normalized or 'tableaux de bord' in normalized:
        tokens.add('reporting')
    if 'crm' in normalized or 'erp' in normalized:
        tokens.add('crm_erp')
    if 'document' in normalized or 'facture' in normalized or 'contrat' in normalized:
        tokens.add('document_ops')
    return tokens


def detect_theme_families(text: str) -> set[str]:
    normalized = normalize_text(text)
    families = set()
    for family, patterns in THEME_PATTERNS.items():
        if any(re.search(pattern, normalized) for pattern in patterns):
            families.add(family)
    return families


def proposal_text(proposal: dict[str, Any]) -> str:
    parts = [
        proposal.get('title_fr', ''),
        proposal.get('angle', ''),
        proposal.get('promise', ''),
        proposal.get('business_positioning', ''),
        ' '.join(proposal.get('keywords', []) or []),
    ]
    return ' '.join(part for part in parts if part)


def normalized_title(text: str) -> str:
    return normalize_text(text)


def lexical_similarity(text_a: str, text_b: str) -> float:
    tokens_a = signal_tokens(text_a)
    tokens_b = signal_tokens(text_b)
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union)


def family_overlap_bonus(families_a: set[str], families_b: set[str]) -> float:
    return 0.18 if families_a and families_b and families_a & families_b else 0.0


def combined_similarity(text_a: str, text_b: str, families_a: set[str], families_b: set[str]) -> float:
    base = lexical_similarity(text_a, text_b)
    return min(1.0, base + family_overlap_bonus(families_a, families_b))


def parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.min.replace(tzinfo=timezone.utc)
    cleaned = value.replace('Z', '+00:00')
    try:
        dt = datetime.fromisoformat(cleaned)
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def load_history() -> dict[str, Any]:
    if not HISTORY_PATH.exists():
        return {
            'project': 'zamania-blog',
            'version': 1,
            'updated_at': now_iso(),
            'rules': dict(DEFAULT_RULES),
            'articles': [],
        }
    data = json.loads(HISTORY_PATH.read_text(encoding='utf-8'))
    data.setdefault('project', 'zamania-blog')
    data.setdefault('version', 1)
    data.setdefault('updated_at', now_iso())
    rules = dict(DEFAULT_RULES)
    rules.update(data.get('rules', {}))
    data['rules'] = rules
    data.setdefault('articles', [])
    return data


def save_history(history: dict[str, Any]) -> None:
    history['updated_at'] = now_iso()
    AUTOMATION_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(json.dumps(history, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def entry_theme_families(entry: dict[str, Any], *, infer_from_text: bool = False) -> set[str]:
    explicit = entry.get('theme_family')
    families = {explicit} if explicit else set()
    if infer_from_text or not families:
        families |= detect_theme_families(' '.join([
            entry.get('title_fr', ''),
            entry.get('summary_fr', ''),
            entry.get('angle', ''),
            ' '.join(entry.get('keywords', []) or []),
        ]))
    return {family for family in families if family}


def recent_articles(history: dict[str, Any], limit: int | None = None) -> list[dict[str, Any]]:
    articles = sorted(history.get('articles', []), key=lambda item: parse_datetime(item.get('published_at')), reverse=True)
    if limit is not None:
        return articles[:limit]
    return articles


def guard_context(history: dict[str, Any]) -> dict[str, Any]:
    rules = history['rules']
    recent = recent_articles(history, rules['history_window'])
    hottest = recent_articles(history, rules['recent_window'])

    recent_counts = Counter()
    blocked = set()
    for entry in recent:
        for family in entry_theme_families(entry):
            recent_counts[family] += 1
    for family, count in recent_counts.items():
        if count >= 2:
            blocked.add(family)
    hot_families = Counter()
    for entry in hottest:
        for family in entry_theme_families(entry):
            hot_families[family] += 1
    for family, count in hot_families.items():
        if count >= 1 and recent_counts[family] >= 2:
            blocked.add(family)

    signature_phrases = []
    for entry in recent[:4]:
        title = entry.get('title_fr', '')
        lowered = normalize_text(title)
        if 'cout cache' in lowered:
            signature_phrases.append('coût caché')
        if 'taches repetitives' in lowered:
            signature_phrases.append('tâches répétitives')
        if 'saisie manuelle' in lowered:
            signature_phrases.append('saisie manuelle')
        if 'faire plus sans recruter' in lowered or 'sans recruter plus' in lowered:
            signature_phrases.append('faire plus sans recruter plus')
        if 'agents ia' in lowered:
            signature_phrases.append('agents IA')
    signature_phrases = sorted(set(signature_phrases))

    return {
        'history_count': len(history.get('articles', [])),
        'recent_articles': [
            {
                'slug': entry.get('slug'),
                'published_at': entry.get('published_at'),
                'title_fr': entry.get('title_fr'),
                'theme_family': entry.get('theme_family'),
            }
            for entry in recent
        ],
        'blocked_theme_families': sorted(blocked),
        'recent_theme_counts': dict(sorted(recent_counts.items())),
        'recent_signature_phrases': signature_phrases,
        'open_theme_ideas': OPEN_THEME_IDEAS,
        'rules': rules,
    }


def history_conflicts(candidate: dict[str, Any], history: dict[str, Any]) -> tuple[list[dict[str, Any]], float]:
    rules = history['rules']
    candidate_text = proposal_text(candidate)
    candidate_title = normalized_title(candidate.get('title_fr', ''))
    candidate_families = entry_theme_families(candidate)
    conflicts: list[dict[str, Any]] = []
    max_score = 0.0

    for entry in recent_articles(history, rules['history_window']):
        entry_text = ' '.join([
            entry.get('title_fr', ''),
            entry.get('summary_fr', ''),
            entry.get('angle', ''),
            ' '.join(entry.get('keywords', []) or []),
        ])
        entry_title = normalized_title(entry.get('title_fr', ''))
        entry_families = entry_theme_families(entry)
        score = combined_similarity(candidate_text, entry_text, candidate_families, entry_families)
        max_score = max(max_score, score)
        same_title = candidate_title and candidate_title == entry_title
        same_family = bool(candidate_families & entry_families)
        if same_title or score >= rules['warn_similarity_threshold'] or (same_family and score >= 0.38):
            conflicts.append({
                'slug': entry.get('slug'),
                'title_fr': entry.get('title_fr'),
                'published_at': entry.get('published_at'),
                'theme_family': entry.get('theme_family'),
                'similarity': round(score, 3),
                'same_title': same_title,
                'same_family': same_family,
            })
    conflicts.sort(key=lambda item: item['similarity'], reverse=True)
    return conflicts[:5], round(max_score, 3)


def validate_batch(proposals: list[dict[str, Any]], history: dict[str, Any]) -> dict[str, Any]:
    context = guard_context(history)
    blocked_families = set(context['blocked_theme_families'])
    rules = history['rules']
    results = []

    for idx, proposal in enumerate(proposals):
        candidate = dict(proposal)
        choice = str(candidate.get('choice') or idx + 1)
        candidate['choice'] = choice
        candidate.setdefault('theme_family', next(iter(entry_theme_families(candidate)), None))
        families = entry_theme_families(candidate)
        conflicts, max_similarity = history_conflicts(candidate, history)
        reasons: list[str] = []
        severity = 'ok'

        if not candidate.get('title_fr'):
            reasons.append('titre manquant')
        if not candidate.get('angle'):
            reasons.append('angle manquant')

        if families & blocked_families:
            reasons.append(
                'famille thématique en cooldown: ' + ', '.join(sorted(families & blocked_families))
            )
        if conflicts:
            top = conflicts[0]
            if top['same_title']:
                reasons.append(f"titre déjà publié: {top['title_fr']}")
            if top['similarity'] >= rules['high_similarity_threshold']:
                reasons.append(
                    f"article trop proche de '{top['title_fr']}' (similarité {top['similarity']})"
                )
            elif top['same_family'] and top['similarity'] >= 0.38:
                reasons.append(
                    f"angle trop proche de la famille déjà couverte par '{top['title_fr']}'"
                )

        for previous in results:
            prev_families = set(previous.get('families', []))
            intra = combined_similarity(
                proposal_text(candidate),
                proposal_text(previous['proposal']),
                families,
                prev_families,
            )
            if intra >= rules['intra_batch_threshold']:
                reasons.append(
                    f"trop proche de la proposition {previous['choice']} du même lot (similarité {round(intra, 3)})"
                )
            elif families and prev_families and families & prev_families:
                reasons.append(
                    f"même famille thématique que la proposition {previous['choice']}: {', '.join(sorted(families & prev_families))}"
                )

        if reasons:
            severity = 'blocked'
        elif max_similarity >= rules['warn_similarity_threshold']:
            severity = 'warning'

        results.append({
            'choice': choice,
            'proposal': candidate,
            'theme_family': candidate.get('theme_family'),
            'families': sorted(families),
            'max_similarity': max_similarity,
            'history_conflicts': conflicts,
            'status': severity,
            'reasons': reasons,
        })

    valid_choices = [item['choice'] for item in results if item['status'] != 'blocked']
    return {
        'ok': all(item['status'] != 'blocked' for item in results),
        'valid_choices': valid_choices,
        'blocked_choices': [item['choice'] for item in results if item['status'] == 'blocked'],
        'results': [
            {
                'choice': item['choice'],
                'status': item['status'],
                'theme_family': item['theme_family'],
                'families': item['families'],
                'max_similarity': item['max_similarity'],
                'reasons': item['reasons'],
                'history_conflicts': item['history_conflicts'],
            }
            for item in results
        ],
        'context': context,
    }


def load_proposals(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise GuardError(f'fichier de propositions introuvable: {path}')
    payload = json.loads(path.read_text(encoding='utf-8'))
    proposals = payload.get('proposals')
    if not isinstance(proposals, list) or not proposals:
        raise GuardError('le fichier de propositions ne contient pas de liste `proposals` valide')
    for idx, item in enumerate(proposals, start=1):
        item.setdefault('choice', str(item.get('choice') or idx))
        item.setdefault('keywords', [])
    return payload


def cmd_context(_: argparse.Namespace) -> dict[str, Any]:
    history = load_history()
    return guard_context(history)


def cmd_validate_proposals(args: argparse.Namespace) -> dict[str, Any]:
    payload = load_proposals(Path(args.proposals_file))
    history = load_history()
    result = validate_batch(payload['proposals'], history)
    result['proposal_date'] = payload.get('proposal_date')
    return result


def cmd_validate_selection(args: argparse.Namespace) -> dict[str, Any]:
    payload = load_proposals(Path(args.proposals_file))
    history = load_history()
    validation = validate_batch(payload['proposals'], history)
    requested_choice = str(args.choice)
    by_choice = {item['choice']: item for item in validation['results']}
    selected = by_choice.get(requested_choice)
    if not selected:
        raise GuardError(f'choix introuvable dans le lot: {requested_choice}')
    alternative = next((choice for choice in validation['valid_choices'] if choice != requested_choice), None)
    return {
        'ok': selected['status'] != 'blocked',
        'requested_choice': requested_choice,
        'selected': selected,
        'suggested_alternative_choice': alternative,
        'valid_choices': validation['valid_choices'],
        'blocked_choices': validation['blocked_choices'],
        'proposal_date': payload.get('proposal_date'),
        'context': validation['context'],
    }


def cmd_record_publication(args: argparse.Namespace) -> dict[str, Any]:
    proposals_path = Path(args.proposals_file)
    payload = load_proposals(proposals_path)
    choice = str(args.choice)
    proposal = next((item for item in payload['proposals'] if str(item.get('choice')) == choice), None)
    if not proposal:
        raise GuardError(f'choix introuvable dans le lot: {choice}')

    history = load_history()
    slug = args.slug
    published_at = args.published_at or now_iso()
    links = json.loads(args.links_json) if args.links_json else {}
    entry = {
        'slug': slug,
        'published_at': published_at,
        'title_fr': proposal.get('title_fr'),
        'summary_fr': proposal.get('promise') or proposal.get('angle') or '',
        'angle': proposal.get('angle', ''),
        'business_positioning': proposal.get('business_positioning', ''),
        'theme_family': proposal.get('theme_family') or next(iter(entry_theme_families(proposal)), None),
        'angle_family': proposal.get('angle_family'),
        'keywords': proposal.get('keywords', []) or [],
        'proposal_date': payload.get('proposal_date'),
        'choice': choice,
        'links': links,
    }

    articles = [item for item in history.get('articles', []) if item.get('slug') != slug]
    articles.append(entry)
    articles.sort(key=lambda item: parse_datetime(item.get('published_at')))
    history['articles'] = articles
    save_history(history)

    return {
        'ok': True,
        'recorded': entry,
        'history_count': len(history['articles']),
        'history_path': str(HISTORY_PATH),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='ZamanIA anti-duplicate guard')
    sub = parser.add_subparsers(dest='command', required=True)

    context_parser = sub.add_parser('context', help='Afficher le contexte anti-doublon')
    context_parser.set_defaults(func=cmd_context)

    validate_parser = sub.add_parser('validate-proposals', help='Valider un lot de propositions')
    validate_parser.add_argument('proposals_file')
    validate_parser.set_defaults(func=cmd_validate_proposals)

    selection_parser = sub.add_parser('validate-selection', help='Valider le choix à publier')
    selection_parser.add_argument('proposals_file')
    selection_parser.add_argument('choice')
    selection_parser.set_defaults(func=cmd_validate_selection)

    record_parser = sub.add_parser('record-publication', help='Enregistrer une publication dans l’historique')
    record_parser.add_argument('proposals_file')
    record_parser.add_argument('choice')
    record_parser.add_argument('slug')
    record_parser.add_argument('--published-at', dest='published_at')
    record_parser.add_argument('--links-json', dest='links_json')
    record_parser.set_defaults(func=cmd_record_publication)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = args.func(args)
    except GuardError as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
