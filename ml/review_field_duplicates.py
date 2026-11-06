"""Build a duplicate-review queue; similarity never authorizes split assignment."""
import json
from collections import defaultdict
from ml.inventory_field import BASE


def duplicate_review(rows):
    decoded = [r for r in rows if 'pixel_sha256' in r]
    pixels = defaultdict(list)
    for r in decoded: pixels[r['pixel_sha256']].append(r)
    exact = [dict(ids=[r['id'] for r in group], labels=sorted({r['label'] for r in group}),
                  conflicting_labels=len({r['label'] for r in group}) > 1)
             for group in pixels.values() if len(group) > 1]
    near = []
    for i, a in enumerate(decoded):
        for b in decoded[i+1:]:
            if a['pixel_sha256'] == b['pixel_sha256']: continue
            distance = (int(a['dhash'], 16) ^ int(b['dhash'], 16)).bit_count()
            if distance <= 4:
                near.append(dict(first=a['id'], second=b['id'], hamming_distance=distance,
                                 labels=[a['label'], b['label']], decision='pending_visual_review'))
    return dict(exact_pixel_duplicate_groups=exact, near_duplicate_candidates=near,
                note='dHash<=4 is a review heuristic, not a duplicate verdict. Misses crops/rotations and some recompressions. Physical leaf/capture independence and prior-cohort perceptual overlap still need review. No roles assigned.')


def main():
    rows = json.loads((BASE/'download-audit.json').read_text())
    review = duplicate_review(rows)
    (BASE/'duplicate-review.json').write_text(json.dumps(review, indent=2))
    print(json.dumps(dict(exact_groups=len(review['exact_pixel_duplicate_groups']),
                          near_pairs=len(review['near_duplicate_candidates']),
                          conflicting_groups=sum(g['conflicting_labels'] for g in review['exact_pixel_duplicate_groups']))))


if __name__ == '__main__': main()
