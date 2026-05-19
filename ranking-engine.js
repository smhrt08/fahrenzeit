/**
 * ranking-engine.js
 * =================
 * Adaptive pairwise car ranking algorithm.
 *
 * DESIGN PRINCIPLES
 * -----------------
 * 1. Transitive closure   — if A > B and B > C, we infer A > C and never ask.
 * 2. Bradley-Terry scores — each comparison updates a continuous rating, not just win count.
 *    Winner gains: Δ = K * (1 - expected)   Loser loses: Δ = K * expected
 *    where expected = scoreA / (scoreA + scoreB)  (same as Elo without the 10^ part)
 * 3. Adaptive pair selection — always pick the most informative unresolved pair:
 *    - Pairs where scores are closest (highest uncertainty)
 *    - Pairs near the "frontier" of the sorted ranking
 *    - Never pairs already resolved by transitivity
 * 4. Soft elimination — cars with many relative losses get deprioritized,
 *    not hard-excluded, so rare upsets surface if warranted.
 * 5. Convergence detection — when the top-N ranking hasn't changed for M
 *    comparisons, the session is considered stable.
 *
 * USAGE
 * -----
 *   const engine = new RankingEngine(cars, { topN: 10 });
 *   engine.loadState(savedState);          // optional: resume session
 *
 *   const pair = engine.nextPair();        // {a, b} or null if converged
 *   engine.recordChoice(winnerId, loserId);
 *
 *   const rankings = engine.getRankings(); // sorted array of {car, score, rank}
 *   const state    = engine.getState();    // serializable snapshot to save
 *
 * EXPORTS (browser + Node)
 * -----
 *   RankingEngine   — main class
 *   transitiveClose — utility: compute full closure from comparison log
 */

const DEFAULT_OPTIONS = {
  topN:            10,     // how many top cars to surface
  kFactor:         32,     // Bradley-Terry update rate (higher = faster movement)
  initialScore:    1000,   // starting score for every car
  eliminationLosses: 4,    // losses before soft-deprioritizing a car
  convergenceRuns: 6,      // stable comparisons before declaring convergence
  maxComparisons:  400,    // hard ceiling to prevent infinite sessions
};

/* ─── Transitive Closure ───────────────────────────────────────────────── */

/**
 * Build the full "beats" set from a comparison log using BFS/DFS.
 * Returns a Map<winnerId, Set<loserId>> representing all inferred wins.
 *
 * Example: log = [{w:'A', l:'B'}, {w:'B', l:'C'}]
 * Result:  A beats {B, C},  B beats {C}
 */
function transitiveClose(log) {
  // Direct wins
  const direct = new Map();
  for (const { w, l } of log) {
    if (!direct.has(w)) direct.set(w, new Set());
    direct.get(w).add(l);
  }

  // BFS to expand each node's reachable set
  const closure = new Map();
  const allIds  = new Set([...log.map(e => e.w), ...log.map(e => e.l)]);

  for (const start of allIds) {
    const reachable = new Set();
    const queue     = [...(direct.get(start) || [])];
    while (queue.length) {
      const node = queue.shift();
      if (reachable.has(node)) continue;
      reachable.add(node);
      for (const next of (direct.get(node) || [])) {
        if (!reachable.has(next)) queue.push(next);
      }
    }
    closure.set(start, reachable);
  }

  return closure;
}

/**
 * Returns true if winner is already known to beat loser (directly or transitively).
 */
function alreadyResolved(closure, winnerId, loserId) {
  return (closure.get(winnerId) || new Set()).has(loserId) ||
         (closure.get(loserId)  || new Set()).has(winnerId);
}

/* ─── Bradley-Terry Score Update ──────────────────────────────────────── */

function expectedScore(scoreA, scoreB) {
  return scoreA / (scoreA + scoreB);
}

function updateScores(scores, winnerId, loserId, k) {
  const sW = scores.get(winnerId) || DEFAULT_OPTIONS.initialScore;
  const sL = scores.get(loserId)  || DEFAULT_OPTIONS.initialScore;
  const exp = expectedScore(sW, sL);
  scores.set(winnerId, sW + k * (1 - exp));
  scores.set(loserId,  Math.max(1, sL - k * exp));  // floor at 1
}

/* ─── Pair Selection ───────────────────────────────────────────────────── */

/**
 * Score how "informative" a potential comparison would be.
 * Higher = more useful to ask.
 *
 * Criteria:
 *  - Score proximity (close scores → uncertain outcome → most info)
 *  - Rank proximity (comparing adjacent-ranked cars is more meaningful)
 *  - Neither car is already soft-eliminated
 *  - Neither has had recent comparisons (avoid over-asking same car)
 */
function pairInfoGain(a, b, scores, lossCount, recentlyAsked, rankedIds) {
  const sA  = scores.get(a.id) || DEFAULT_OPTIONS.initialScore;
  const sB  = scores.get(b.id) || DEFAULT_OPTIONS.initialScore;
  const diff = Math.abs(sA - sB);

  // Score closeness: 0 = identical, penalized as diff grows
  const scoreSimilarity = 1 / (1 + diff / 80);

  // Rank adjacency: pairs close in rank are more meaningful
  const rankA = rankedIds.indexOf(a.id);
  const rankB = rankedIds.indexOf(b.id);
  const rankDiff = Math.abs(rankA - rankB);
  const rankBonus = rankDiff <= 3 ? 1.4 : rankDiff <= 8 ? 1.1 : 0.8;

  // Penalize soft-eliminated cars (many losses)
  const lossA = lossCount.get(a.id) || 0;
  const lossB = lossCount.get(b.id) || 0;
  const lossPenalty = Math.max(0, 1 - 0.12 * Math.max(lossA, lossB));

  // Penalize recently asked (give other pairs a chance)
  const recentPenalty = (recentlyAsked.has(a.id) || recentlyAsked.has(b.id)) ? 0.7 : 1.0;

  return scoreSimilarity * rankBonus * lossPenalty * recentPenalty;
}

/* ─── Main Engine ──────────────────────────────────────────────────────── */

class RankingEngine {
  constructor(cars, options = {}) {
    this.options     = { ...DEFAULT_OPTIONS, ...options };
    this.cars        = cars;       // array of car objects with .id field
    this.carMap      = new Map(cars.map(c => [c.id, c]));

    // State
    this.log         = [];         // [{w, l, ts}]
    this.scores      = new Map();  // carId -> BT score
    this.lossCount   = new Map();  // carId -> # losses
    this.closure     = new Map();  // carId -> Set<carId> (transitive wins)
    this.recentlyAsked = new Set();// carIds asked in last ~8 comparisons
    this.recentQueue = [];         // circular buffer for recency tracking
    this.totalAsked  = 0;
    this.stableRuns  = 0;
    this.lastTopN    = [];

    // Init scores
    for (const car of cars) {
      this.scores.set(car.id, this.options.initialScore);
      this.lossCount.set(car.id, 0);
    }
  }

  /* ── Public API ──────────────────────────────────────────────────────── */

  /**
   * Get the next pair to compare.
   * Returns { a, b } (car objects) or null if converged / max reached.
   */
  nextPair() {
    if (this.isConverged()) return null;

    const eligible = this._eligibleCars();
    if (eligible.length < 2) return null;

    const rankedIds = this._sortedIds();
    let   bestScore = -Infinity;
    let   bestPair  = null;

    // Sample candidates — O(n²) is fine up to ~200 cars; beyond that we sample
    const candidates = eligible.length <= 150
      ? eligible
      : this._sample(eligible, 80);  // sample for large sets

    for (let i = 0; i < candidates.length; i++) {
      for (let j = i + 1; j < candidates.length; j++) {
        const a = candidates[i];
        const b = candidates[j];

        // Skip if already resolved by transitivity
        if (alreadyResolved(this.closure, a.id, b.id)) continue;

        const gain = pairInfoGain(
          a, b, this.scores, this.lossCount, this.recentlyAsked, rankedIds
        );

        if (gain > bestScore) {
          bestScore = gain;
          bestPair  = { a, b };
        }
      }
    }

    return bestPair;
  }

  /**
   * Record the user's choice. winnerId beat loserId.
   * Also applies all new transitive inferences.
   */
  recordChoice(winnerId, loserId) {
    const ts = Date.now();
    this.log.push({ w: winnerId, l: loserId, ts });
    this.totalAsked++;

    // Update BT scores
    updateScores(this.scores, winnerId, loserId, this.options.kFactor);

    // Update loss count
    this.lossCount.set(loserId, (this.lossCount.get(loserId) || 0) + 1);

    // Rebuild transitive closure (fast incremental BFS)
    this._expandClosure(winnerId, loserId);

    // Update recency window (last 8 car IDs asked)
    this.recentQueue.push(winnerId, loserId);
    if (this.recentQueue.length > 16) this.recentQueue.splice(0, 2);
    this.recentlyAsked = new Set(this.recentQueue);

    // Check convergence
    this._checkConvergence();
  }

  /**
   * Get current rankings, sorted by score descending.
   * Returns array of { car, score, rank, lossCount, inferredWins, inferredLosses }
   */
  getRankings() {
    const sorted = [...this.cars].sort((a, b) =>
      (this.scores.get(b.id) || 0) - (this.scores.get(a.id) || 0)
    );

    return sorted.map((car, i) => ({
      rank:           i + 1,
      car,
      score:          Math.round(this.scores.get(car.id) || 0),
      lossCount:      this.lossCount.get(car.id) || 0,
      inferredWins:   (this.closure.get(car.id) || new Set()).size,
      inferredLosses: [...this.closure.values()].filter(s => s.has(car.id)).length,
      directComparisons: this.log.filter(e => e.w === car.id || e.l === car.id).length,
    }));
  }

  /**
   * How many comparisons have been skipped via transitivity so far?
   */
  getEfficiency() {
    const totalPossible = this.cars.length * (this.cars.length - 1) / 2;
    const inferred      = [...this.closure.values()].reduce((s, v) => s + v.size, 0);
    return {
      totalPossibleComparisons: totalPossible,
      directComparisons:        this.totalAsked,
      inferredComparisons:      inferred,
      percentageResolved:       Math.round((this.totalAsked + inferred) / totalPossible * 100),
    };
  }

  isConverged() {
    return this.stableRuns >= this.options.convergenceRuns ||
           this.totalAsked >= this.options.maxComparisons;
  }

  /** Serializable state snapshot for saving/resuming sessions. */
  getState() {
    return {
      log:       this.log,
      scores:    [...this.scores.entries()],
      lossCount: [...this.lossCount.entries()],
      totalAsked: this.totalAsked,
      stableRuns: this.stableRuns,
      lastTopN:   this.lastTopN,
    };
  }

  /** Restore a saved state. */
  loadState(state) {
    if (!state) return;
    this.log        = state.log        || [];
    this.scores     = new Map(state.scores    || []);
    this.lossCount  = new Map(state.lossCount || []);
    this.totalAsked = state.totalAsked || 0;
    this.stableRuns = state.stableRuns || 0;
    this.lastTopN   = state.lastTopN   || [];

    // Rebuild closure from log
    this.closure = transitiveClose(this.log);
  }

  /* ── Private helpers ─────────────────────────────────────────────────── */

  _eligibleCars() {
    const threshold = this.options.eliminationLosses;
    return this.cars.filter(c => (this.lossCount.get(c.id) || 0) <= threshold + 2);
    // +2 gives a soft buffer — cars past threshold still appear occasionally
  }

  _sortedIds() {
    return [...this.cars]
      .sort((a, b) => (this.scores.get(b.id) || 0) - (this.scores.get(a.id) || 0))
      .map(c => c.id);
  }

  /** Fisher-Yates sample of k items from arr */
  _sample(arr, k) {
    const copy = [...arr];
    for (let i = copy.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [copy[i], copy[j]] = [copy[j], copy[i]];
    }
    return copy.slice(0, k);
  }

  /**
   * Incrementally expand the transitive closure after a new w > l result.
   * Much faster than full rebuild: only update nodes that transitively lose to w.
   */
  _expandClosure(w, l) {
    // Direct win
    if (!this.closure.has(w)) this.closure.set(w, new Set());
    this.closure.get(w).add(l);

    // Everything that l beats, w now also beats
    for (const x of (this.closure.get(l) || [])) {
      this.closure.get(w).add(x);
    }

    // Everything that previously beat w, now also beats l (and l's reachables)
    for (const [node, beaten] of this.closure) {
      if (beaten.has(w)) {
        beaten.add(l);
        for (const x of (this.closure.get(l) || [])) {
          beaten.add(x);
        }
      }
    }
  }

  _checkConvergence() {
    const topN = this._sortedIds().slice(0, this.options.topN);
    const same = topN.length === this.lastTopN.length &&
                 topN.every((id, i) => id === this.lastTopN[i]);
    if (same) {
      this.stableRuns++;
    } else {
      this.stableRuns = 0;
      this.lastTopN   = topN;
    }
  }
}

/* ─── Exports ──────────────────────────────────────────────────────────── */

if (typeof module !== 'undefined') {
  module.exports = { RankingEngine, transitiveClose };
} else {
  window.RankingEngine    = RankingEngine;
  window.transitiveClose  = transitiveClose;
}
