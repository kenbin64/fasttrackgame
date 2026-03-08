// GameState for Brickbreaker 3D
// Tracks lives, paddle integrity, current brick layer set, and detects high-intensity ceiling<->brick cadence
// to drive AudioManager intensity states.
// This module is engine-agnostic; consumers should call recordEvent() with gameplay events.

(function(global){
  class GameState{
    constructor(opts={}){
      this.maxLives = opts.maxLives ?? 3;
      this.lives = opts.lives ?? this.maxLives;

      // Paddle integrity: 1.0 = pristine, 0 = destroyed
      this.paddleIntegrity = 1.0;
      // Active paddle fragment id (if fractured system is used)
      this.activePaddleId = null;

      // Brick layers metadata: array of { id, color, density, hardness, rows, cols }
      this.layers = Array.isArray(opts.layers) ? opts.layers : [];
      this.currentLevel = opts.currentLevel ?? 1; // progression counter

      // Event buffer for cadence detection
      this.eventWindowSec = opts.eventWindowSec ?? 2.5; // time window to analyze cadence
      this.highIntensityThreshold = opts.highIntensityThreshold ?? 4; // min alternating hits in window
      this._events = []; // {t, type}
      this._time = 0;

      // Audio callback (optional): function setState({ intensity: 'base'|'high', defeatCue?:bool, victoryCue?:bool })
      this.setAudioState = opts.setAudioState || null;

      // Internal state for last emitted intensity
      this._intensity = 'base';
    }

    // Advance simulation time; prune old events and update audio intensity
    tick(dt){
      this._time += Math.max(0, dt || 0);
      const cutoff = this._time - this.eventWindowSec;
      // Drop old events
      while(this._events.length && this._events[0].t < cutoff){ this._events.shift(); }
      // Recompute cadence-based intensity
      const intensity = this._computeCadenceIntensity();
      if(intensity !== this._intensity){
        this._intensity = intensity;
        if(this.setAudioState){ this.setAudioState({ intensity }); }
      }
    }

    // Record notable gameplay events
    // Supported types: 'ceiling_hit', 'brick_hit', 'ball_lost', 'level_clear', 'paddle_damaged'
    recordEvent(type, payload){
      const now = this._time;
      this._events.push({ t: now, type, payload });

      if(type === 'ball_lost'){
        this.lives = Math.max(0, this.lives - 1);
        if(this.setAudioState){ this.setAudioState({ intensity: 'base', defeatCue: true }); }
      }
      if(type === 'level_clear'){
        this.currentLevel += 1;
        if(this.setAudioState){ this.setAudioState({ intensity: 'base', victoryCue: true }); }
      }
      if(type === 'paddle_damaged' && payload && typeof payload.integrity === 'number'){
        this.paddleIntegrity = Math.max(0, Math.min(1, payload.integrity));
      }
    }

    isGameOver(){
      return this.lives <= 0 || this.paddleIntegrity <= 0;
    }

    // Compute whether recent events indicate rapid ceiling<->brick alternation
    _computeCadenceIntensity(){
      // Filter only ceiling/brick events in window
      const seq = this._events.filter(e => e.type === 'ceiling_hit' || e.type === 'brick_hit');
      if(seq.length < this.highIntensityThreshold) return 'base';

      // Count alternations: C->B or B->C transitions, weighted by recency
      let alternations = 0;
      for(let i=1;i<seq.length;i++){
        if(seq[i].type !== seq[i-1].type){ alternations++; }
      }

      // Also enforce tempo: average delta should be fast enough
      let dtSum = 0; let pairs = 0;
      for(let i=1;i<seq.length;i++){ dtSum += (seq[i].t - seq[i-1].t); pairs++; }
      const avgDt = pairs ? dtSum / pairs : Infinity;

      const fastTempo = avgDt <= (this.eventWindowSec / (this.highIntensityThreshold + 1));
      if(alternations >= this.highIntensityThreshold && fastTempo){ return 'high'; }
      return 'base';
    }

    // Utility: set or replace layer set
    setLayers(layers){
      this.layers = Array.isArray(layers) ? layers : [];
    }

    // Utility: update active paddle fragment id after fracture
    setActivePaddle(id){ this.activePaddleId = id; }
  }

  if(typeof module !== 'undefined' && module.exports){ module.exports = GameState; }
  else { global.GameState = GameState; }
})(this);
