import { useState } from 'react';
import { GameState } from '../types/game';
import { api } from '../services/api';
import '../styles/Lobby.css';

interface LobbyProps {
  gameState: GameState | null;
  onGameCreated: (game: GameState, playerId: string) => void;
  onGameStarted: (game: GameState) => void;
}

export function Lobby({ gameState, onGameCreated, onGameStarted }: LobbyProps) {
  const [tab, setTab] = useState<'create' | 'join'>('create');
  const [copied, setCopied] = useState(false);
  const [showHelp, setShowHelp] = useState(false);

  const copyGameCode = (code: string) => {
    const doFallback = () => {
      const el = document.createElement('textarea');
      el.value = code;
      el.style.position = 'fixed';
      el.style.opacity = '0';
      document.body.appendChild(el);
      el.focus();
      el.select();
      document.execCommand('copy');
      document.body.removeChild(el);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    };
    if (navigator.clipboard) {
      navigator.clipboard.writeText(code).then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }).catch(doFallback);
    } else {
      doFallback();
    }
  };
  const [playerName, setPlayerName] = useState('');
  const [joinGameId, setJoinGameId] = useState('');
  const [aiCount, setAiCount] = useState(1);
  const [startingAuthority, setStartingAuthority] = useState(50);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCreateGame = async () => {
    if (!playerName.trim()) { setError('Please enter your name'); return; }
    setLoading(true); setError(null);
    try {
      const gameId = `game_${Date.now()}`;
      const response = await api.createGame(gameId, [playerName], aiCount, startingAuthority);
      if (response.game) {
        onGameCreated(response.game, response.game.players[0].player_id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create game');
    } finally { setLoading(false); }
  };

  const handleJoinGame = async () => {
    if (!playerName.trim()) { setError('Please enter your name'); return; }
    if (!joinGameId.trim()) { setError('Please enter a game code'); return; }
    setLoading(true); setError(null);
    try {
      const response = await api.joinGame(joinGameId.trim(), playerName.trim());
      if (response.game && response.player_id) {
        onGameCreated(response.game, response.player_id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to join game');
    } finally { setLoading(false); }
  };

  const handleStartGame = async () => {
    if (!gameState) return;
    setLoading(true); setError(null);
    try {
      const response = await api.startGame(gameState.game_id);
      if (response.game) onGameStarted(response.game);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start game');
    } finally { setLoading(false); }
  };

  if (gameState) {
    return (
      <div className="lobby">
        <div className="lobby-card">
          <h2>⭐ Star Realms</h2>
          <div className="lobby-waiting">
            <div className="game-code-box">
              <span className="game-code-label">Game Code</span>
              <span className="game-code">{gameState.game_id}</span>
              <button className="btn-copy" onClick={() => copyGameCode(gameState.game_id)}>
                {copied ? '✓ Copied!' : 'Copy'}
              </button>
            </div>
            <p className="game-code-hint">Share this code so others can join</p>

            <div className="players-list">
              <h4>Players ({gameState.players.length})</h4>
              {gameState.players.map(p => (
                <div key={p.player_id} className="player-item">
                  {p.is_ai? '🤖' : '👤'} {p.name}
                </div>
              ))}
            </div>

            {error && <div className="error-message">{error}</div>}

            <button className="btn-primary" onClick={handleStartGame} disabled={loading}>
              {loading ? 'Starting...' : 'Start Game'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="lobby">
      {showHelp && (
        <div className="help-overlay" onClick={() => setShowHelp(false)}>
          <div className="help-modal" onClick={e => e.stopPropagation()}>
            <h3>How to Play</h3>
            <button className="help-close" onClick={() => setShowHelp(false)}>✕</button>
            <div className="help-content">
              <p><strong>Objective:</strong> Reduce all opponents' Authority to 0.</p>
              <p><strong>Each turn:</strong> All cards in your hand play automatically. Use the Trade and Combat they generate.</p>
              <p><strong>Trade:</strong> Buy cards from the Trade Row to strengthen your deck.</p>
              <p><strong>Combat:</strong> Attack opponent bases and players. You must destroy all bases before hitting a player directly.</p>
              <p><strong>Bases &amp; Outposts:</strong> Bases stay in play and give bonuses every turn. Outposts must be destroyed before you can attack the player. All bases block direct attacks.</p>
              <p><strong>Scrap:</strong> Some cards let you scrap (permanently remove) a card — great for thinning your deck.</p>
              <p><strong>Factions:</strong> Playing multiple cards of the same faction unlocks Ally bonuses.</p>
              <p><strong>End Turn:</strong> Draw 5 new cards and pass to the next player.</p>
            </div>
          </div>
        </div>
      )}
      <div className="lobby-card">
        <h2>⭐ Star Realms</h2>
        <button className="help-btn" onClick={() => setShowHelp(true)}>How to Play</button>

        <div className="lobby-tabs">
          <button className={`lobby-tab ${tab === 'create' ? 'lobby-tab--active' : ''}`} onClick={() => { setTab('create'); setError(null); }}>
            Create Game
          </button>
          <button className={`lobby-tab ${tab === 'join' ? 'lobby-tab--active' : ''}`} onClick={() => { setTab('join'); setError(null); }}>
            Join Game
          </button>
        </div>

        <div className="lobby-form">
          <div className="form-group">
            <label>Your Name</label>
            <input
              type="text"
              value={playerName}
              onChange={e => setPlayerName(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && (tab === 'create' ? handleCreateGame() : handleJoinGame())}
              placeholder="Enter your name"
              disabled={loading}
              autoFocus
            />
          </div>

          {tab === 'create' ? (
            <>
              <div className="form-group">
                <label>Robot Opponents</label>
                <select value={aiCount} onChange={e => setAiCount(Number(e.target.value))} disabled={loading}>
                  <option value={0}>Invite a friend</option>
                  <option value={1}>1 Robot</option>
                  <option value={2}>2 Robot</option>
                  <option value={3}>3 Robot</option>
                  <option value={4}>4 Robot</option>
                  <option value={5}>5 Robot</option>
                </select>
              </div>
              <div className="form-group">
                <label>Starting Authority</label>
                <select value={startingAuthority} onChange={e => setStartingAuthority(Number(e.target.value))} disabled={loading}>
                  <option value={30}>30 — Quick</option>
                  <option value={50}>50 — Standard</option>
                  <option value={75}>75 — Epic</option>
                  <option value={100}>100 — Marathon</option>
                </select>
              </div>
            </>
          ) : (
            <div className="form-group">
              <label>Game Code</label>
              <input
                type="text"
                value={joinGameId}
                onChange={e => setJoinGameId(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleJoinGame()}
                placeholder="Paste game code here"
                disabled={loading}
              />
            </div>
          )}

          {error && <div className="error-message">{error}</div>}

          <button
            className="btn-primary"
            onClick={tab === 'create' ? handleCreateGame : handleJoinGame}
            disabled={loading}
          >
            {loading ? '...' : tab === 'create' ? 'Create Game' : 'Join Game'}
          </button>
        </div>
      </div>
    </div>
  );
}
