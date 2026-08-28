/**
 * Main App component.
 */
import { useState, useCallback, useRef } from 'react';
import { GameState, WSMessage } from './types/game';
import { Lobby } from './components/Lobby';
import { GameBoard } from './components/GameBoard';
import { SpaceBackground } from './components/SpaceBackground';
import { useWebSocket } from './hooks/useWebSocket';
import { AttackEvent } from './components/LaserOverlay';
import './styles/tokens.css';
import './styles/App.css';

let _attackCounter = 0;

function App() {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [currentPlayerId, setCurrentPlayerId] = useState<string | null>(null);
  const [attackEvents, setAttackEvents] = useState<AttackEvent[]>([]);
  const [launchingFleet, setLaunchingFleet] = useState(false);
  const launchTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleAttackEvent = useCallback((attackerId: string, targetId: string) => {
    const evt: AttackEvent = {
      id: `atk-${++_attackCounter}`,
      attackerId,
      targetId,
    };
    setAttackEvents(prev => [...prev, evt]);
    setLaunchingFleet(true);
    if (launchTimer.current) clearTimeout(launchTimer.current);
    launchTimer.current = setTimeout(() => setLaunchingFleet(false), 900);
  }, []);

  const handleMessage = useCallback((message: WSMessage) => {
    console.log('WebSocket message:', message);

    if (message.type === 'player_joined' || message.type === 'game_started') {
      if (message.game) setGameState(message.game);
      return;
    }

    if (message.type === 'combat_attack') {
      handleAttackEvent((message as any).attacker_id, (message as any).target_id);
      if (message.game) setGameState(message.game);
      return;
    }

    if (message.game) {
      setGameState(message.game);
    }
  }, []);

  useWebSocket(gameState?.game_id || null, handleMessage);

  const handleGameCreated = (game: GameState, playerId: string) => {
    setGameState(game);
    setCurrentPlayerId(playerId);
  };

  const handleGameStarted = (game: GameState) => {
    setGameState(game);
  };

  return (
    <div className="app">
      <SpaceBackground />
      <main className="app-main">
        {!gameState || gameState.phase === 'lobby' ? (
          <Lobby
            gameState={gameState}
            onGameCreated={handleGameCreated}
            onGameStarted={handleGameStarted}
          />
        ) : (
          <GameBoard
            gameState={gameState}
            currentPlayerId={currentPlayerId}
            onGameUpdate={setGameState}
            attackEvents={attackEvents}
            launchingFleet={launchingFleet}
            onAttackEvent={handleAttackEvent}
          />
        )}
      </main>
    </div>
  );

}

export default App;
