/**
 * Main game board component.
 */
import { useState, useEffect, useRef } from 'react';
import { GameState, CardInstance } from '../types/game';
import { api } from '../services/api';
import { ActionLog } from './ActionLog';
import { TradeRow } from './TradeRow';
import { PlayerSidebar } from './PlayerSidebar';
import { CombatZone } from './CombatZone';
import { PlayerMine } from './PlayerMine';
import { DamageDistributor } from './DamageDistributor';
import { CardPicker } from './CardPicker';
import { ChoicePicker } from './ChoicePicker';
import { YourTurnToast } from './YourTurnToast';
import { LaserOverlay, AttackEvent } from './LaserOverlay';
import '../styles/GameBoard.css';

interface GameBoardProps {
  gameState: GameState;
  currentPlayerId: string | null;
  onGameUpdate: (game: GameState) => void;
  attackEvents?: AttackEvent[];
  launchingFleet?: boolean;
  onAttackEvent?: (attackerId: string, targetId: string) => void;
}

export function GameBoard({ gameState, currentPlayerId, onGameUpdate, attackEvents = [], launchingFleet = false, onAttackEvent }: GameBoardProps) {
  const [error, setError] = useState<string | null>(null);
  const [aiExecuting, setAiExecuting] = useState(false);
  const [showDamageDistributor, setShowDamageDistributor] = useState(false);
  const [aiTrigger, setAiTrigger] = useState(0);
  const executingAiRef = useRef(false);
  const autoPlayingRef = useRef(false);

  const currentPlayer = gameState.players.find((p) => p.player_id === currentPlayerId);
  const isMyTurn = gameState.players[gameState.current_player_index]?.player_id === currentPlayerId;
  const opponents = gameState.players.filter((p) => p.player_id !== currentPlayerId);

  // Auto-play all hand cards at turn start, and resume after a pending effect clears
  useEffect(() => {
    if (!isMyTurn || !currentPlayerId || !currentPlayer) return;
    if (gameState.pending_effect) return;
    if (autoPlayingRef.current) return;
    if (currentPlayer.hand.length === 0) return;

    const playAll = async () => {
      autoPlayingRef.current = true;
      let state = gameState;
      for (const card of [...currentPlayer.hand]) {
        if (state.pending_effect) break;
        try {
          const response = await api.playCard(state.game_id, currentPlayerId, card.instance_id);
          if (response.game) {
            state = response.game;
            onGameUpdate(response.game);
          }
        } catch {
          break;
        }
      }
      autoPlayingRef.current = false;
    };

    playAll();
  }, [isMyTurn, gameState.current_player_index, gameState.game_id, gameState.pending_effect]);

  // Auto-execute AIturns
  useEffect(() => {
    const currentPlayerInTurn = gameState.players[gameState.current_player_index];
    const isAI= currentPlayerInTurn?.is_ai|| false;
    const playerId = currentPlayerInTurn?.player_id;
    const playerName = currentPlayerInTurn?.name;

    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('🔄 AIuseEffect FIRED', {
      timestamp: new Date().toLocaleTimeString(),
      playerIndex: gameState.current_player_index,
      playerName,
      playerId: playerId?.substring(0, 8),
      isAI,
      executingAiRef: executingAiRef.current,
      phase: gameState.phase
    });

    if (!currentPlayerInTurn) {
      console.log('❌ SKIP: No active player');
      return;
    }

    if (!isAI) {
      console.log('❌ SKIP: Not an AIplayer (human turn)');
      return;
    }

    if (executingAiRef.current) {
      console.log('❌ SKIP: AIalready executing (executingAiRef = true)');
      return;
    }

    if (gameState.phase !== 'playing') {
      console.log('❌ SKIP: Wrong phase:', gameState.phase);
      return;
    }

    console.log('✅ ALL CHECKS PASSED - Starting AIexecution');

    const executeAI= async () => {
      console.log(`🤖 [${playerName}] Setting executingAiRef = TRUE`);
      executingAiRef.current = true;
      setAiExecuting(true);

      try {
        // Small delay so user can see it's AI's turn
        console.log(`🤖 [${playerName}] Waiting 500ms...`);
        await new Promise((resolve) => setTimeout(resolve, 500));

        console.log(`🤖 [${playerName}] Calling API executeAiTurn...`);
        const response = await api.executeAiTurn(gameState.game_id);
        console.log(`🤖 [${playerName}] API response received:`, {
          newPlayerIndex: response.game?.current_player_index,
          newPlayerName: response.game?.players[response.game?.current_player_index]?.name
        });

        // Reset ref BEFORE updating game state so next AIcan execute
        console.log(`🤖 [${playerName}] Setting executingAiRef = FALSE (before onGameUpdate)`);
        executingAiRef.current = false;
        setAiExecuting(false);

        if (response.game) {
          console.log(`🤖 [${playerName}] Calling onGameUpdate...`);
          onGameUpdate(response.game);
          console.log(`🤖 [${playerName}] onGameUpdate complete`);

          // Check if next player is also AIand trigger their turn
          const nextPlayer = response.game.players[response.game.current_player_index];
          if (nextPlayer?.is_ai&& response.game.phase === 'playing') {
            console.log(`🔗 [${playerName}] Next player ${nextPlayer.name} is also AI- forcing re-trigger`);
            // Force useEffect to run again by incrementing trigger
            setTimeout(() => {
              setAiTrigger(prev => prev + 1);
            }, 100);
          }
        }
        setError(null);
      } catch (err) {
        console.error(`🤖 [${playerName}] AIturn FAILED:`, err);
        setError(err instanceof Error ? err.message : 'AIturn failed');
        executingAiRef.current = false;
        setAiExecuting(false);
      }

      console.log(`🤖 [${playerName}] AIturn execution function complete`);
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    };

    executeAI();
  }, [gameState.current_player_index, gameState.game_id, gameState.phase, aiTrigger]);


  const handleAcquireCard = async (card: CardInstance, fromExplorers: boolean = false) => {
    if (!currentPlayerId || !isMyTurn) return;

    try {
      const response = await api.acquireCard(
        gameState.game_id,
        currentPlayerId,
        card.instance_id,
        fromExplorers
      );
      if (response.game) {
        onGameUpdate(response.game);
      }
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to acquire card');
    }
  };

  const handleAttackPlayer = async (targetPlayerId: string) => {
    if (!currentPlayerId || !isMyTurn || !currentPlayer) return;

    if (currentPlayer.combat <= 0) {
      setError('No combat available');
      return;
    }

    onAttackEvent?.(currentPlayerId, targetPlayerId);

    try {
      const response = await api.attackPlayer(
        gameState.game_id,
        currentPlayerId,
        targetPlayerId
      );
      if (response.game) {
        onGameUpdate(response.game);
      }
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to attack');
    }
  };

  const handleAttackBase = async (targetPlayerId: string, base: CardInstance) => {
    if (!currentPlayerId || !isMyTurn || !currentPlayer) return;

    if (currentPlayer.combat <= 0) {
      setError('No combat available');
      return;
    }

    // Calculate damage (use enough to destroy, or all available combat)
    const damageNeeded = base.current_defense || base.defense || 0;
    const damage = Math.min(damageNeeded, currentPlayer.combat);

    onAttackEvent?.(currentPlayerId, targetPlayerId);

    try {
      const response = await api.attackBase(
        gameState.game_id,
        currentPlayerId,
        targetPlayerId,
        base.instance_id,
        damage
      );
      if (response.game) {
        onGameUpdate(response.game);
      }
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to attack base');
    }
  };

  const handleEndTurn = async () => {
    if (!currentPlayerId || !isMyTurn) return;

    try {
      const response = await api.endTurn(gameState.game_id, currentPlayerId);
      if (response.game) {
        onGameUpdate(response.game);
      }
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to end turn');
    }
  };

  const handleScrapCard = async (card: CardInstance) => {
    if (!currentPlayerId || !isMyTurn) return;

    try {
      const response = await api.scrapCard(gameState.game_id, currentPlayerId, card.instance_id);
      if (response.game) {
        onGameUpdate(response.game);
      }
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to scrap card');
    }
  };


  const handleResolveScrap = async (card: CardInstance, location: string) => {
    if (!currentPlayerId) return;
    try {
      const response = await api.resolveScrap(gameState.game_id, currentPlayerId, card.instance_id, location);
      if (response.game) onGameUpdate(response.game);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to resolve scrap');
    }
  };

  const handleResolveDiscard = async (card: CardInstance, targetPlayerId: string) => {
    if (!currentPlayerId) return;
    try {
      const response = await api.resolveDiscard(gameState.game_id, currentPlayerId, targetPlayerId, card.instance_id);
      if (response.game) onGameUpdate(response.game);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to resolve discard');
    }
  };

  const handleResolveDestroyBase = async (card: CardInstance, targetPlayerId: string) => {
    if (!currentPlayerId) return;
    try {
      const response = await api.resolveDestroyBase(gameState.game_id, currentPlayerId, targetPlayerId, card.instance_id);
      if (response.game) onGameUpdate(response.game);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to resolve destroy base');
    }
  };

  const handleSkipEffect = async () => {
    if (!currentPlayerId) return;
    try {
      const response = await api.skipEffect(gameState.game_id, currentPlayerId);
      if (response.game) onGameUpdate(response.game);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to skip effect');
    }
  };

  const handleResolveChoice = async (optionIndex: number) => {
    if (!currentPlayerId) return;
    try {
      const response = await api.resolveChoice(gameState.game_id, currentPlayerId, optionIndex);
      if (response.game) onGameUpdate(response.game);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to resolve choice');
    }
  };

  const handleResolveAcquireFree = async (card: CardInstance, fromExplorers: boolean = false) => {
    if (!currentPlayerId) return;
    try {
      const response = await api.resolveAcquireFree(gameState.game_id, currentPlayerId, card.instance_id, fromExplorers);
      if (response.game) onGameUpdate(response.game);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to resolve acquire free');
    }
  };

  const handleResolveDiscardAny = async (card: CardInstance) => {
    if (!currentPlayerId) return;
    try {
      const response = await api.resolveDiscardAny(gameState.game_id, currentPlayerId, card.instance_id);
      if (response.game) onGameUpdate(response.game);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed');
    }
  };

  const handleFinishDiscardAny = async () => {
    if (!currentPlayerId) return;
    try {
      const response = await api.finishDiscardAny(gameState.game_id, currentPlayerId);
      if (response.game) onGameUpdate(response.game);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed');
    }
  };

  const handleResolveCopyShip = async (card: CardInstance) => {
    if (!currentPlayerId) return;
    try {
      const response = await api.resolveCopyShip(gameState.game_id, currentPlayerId, card.instance_id);
      if (response.game) onGameUpdate(response.game);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed');
    }
  };

  const handleResolveBaseToTop = async (card: CardInstance) => {
    if (!currentPlayerId) return;
    try {
      const response = await api.resolveBaseToTop(gameState.game_id, currentPlayerId, card.instance_id);
      if (response.game) onGameUpdate(response.game);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to resolve base to top');
    }
  };

  const handleDistributeDamage = async (targets: Array<{ player_id: string; damage: number }>) => {
    if (!currentPlayerId || !isMyTurn) return;

    try {
      const response = await api.distributeDamage(gameState.game_id, currentPlayerId, targets);
      if (response.game) {
        onGameUpdate(response.game);
      }
      setShowDamageDistributor(false);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to distribute damage');
    }
  };

  if (gameState.phase === 'ended') {
    const winner = gameState.players.find((p) => p.player_id === gameState.winner_id);
    return (
      <div className="game-over">
        <h2>🎉 Game Over!</h2>
        <p className="winner">{winner?.name} Wins!</p>
        <button className="btn-primary" onClick={() => window.location.reload()}>
          New Game
        </button>
      </div>
    );
  }

  return (
    <div className="game-board">
      <YourTurnToast isMyTurn={isMyTurn} />
      <LaserOverlay attacks={attackEvents} />
      {error && (
        <div className="error-banner">
          {error}
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {aiExecuting && (
        <div className="ai-turn-banner">🤖 Robot is thinking...</div>
      )}

      {/* TOP — Trade Row */}
      <div className="game-zone-top">
        <TradeRow
          tradeRow={gameState.trade_row}
          explorerPile={gameState.explorer_pile}
          scrapHeap={gameState.scrap_heap}
          currentPlayer={currentPlayer}
          isMyTurn={isMyTurn}
          onAcquire={handleAcquireCard}
        />
      </div>

      {/* CENTER — flex column: opponents | AItom-row(sidebar | mine | log) */}
      <div className="game-zone-center">
        {/* Opponents */}
        <CombatZone
          currentPlayer={currentPlayer ?? gameState.players[0]}
          opponents={opponents.length > 0 ? opponents : gameState.players.slice(1)}
          isMyTurn={isMyTurn}
          activePlayerIndex={gameState.current_player_index}
          players={gameState.players}
          maxAuthority={gameState.config.starting_authority}
          onScrapCard={handleScrapCard}
          onAttackPlayer={handleAttackPlayer}
          onAttackBase={handleAttackBase}
          onEndTurn={handleEndTurn}
          onDistributeDamage={() => setShowDamageDistributor(true)}
        />

        {/* AItom row: sidebar | mine | log */}
        <div className="game-AItom-row">
          <div className="game-zone-left">
            <PlayerSidebar
              players={gameState.players}
              currentPlayerId={currentPlayerId}
              activePlayerIndex={gameState.current_player_index}
              startingAuthority={gameState.config.starting_authority}
            />
          </div>
          <PlayerMine
            currentPlayer={currentPlayer ?? gameState.players[0]}
            isMyTurn={isMyTurn}
            opponents={opponents.length > 0 ? opponents : gameState.players.slice(1)}
            maxAuthority={gameState.config.starting_authority}
            onScrapCard={handleScrapCard}
            onEndTurn={handleEndTurn}
            onDistributeDamage={() => setShowDamageDistributor(true)}
            launching={launchingFleet}
          />
          <div className="game-zone-right">
            <ActionLog gameState={gameState} />
          </div>
        </div>
      </div>

      {/* Damage Distributor Modal */}
      {showDamageDistributor && currentPlayer && (
        <DamageDistributor
          opponents={opponents}
          availableCombat={currentPlayer.combat}
          onDistribute={handleDistributeDamage}
          onCancel={() => setShowDamageDistributor(false)}
        />
      )}

      {/* Pending Effect Modal */}
      {gameState.pending_effect && isMyTurn && currentPlayer && (() => {
        const pe = gameState.pending_effect!;
        if (pe.type === 'scrap_card') {
          const loc = pe.location ?? 'hand';
          let cards: CardInstance[];
          let getLocation: (card: CardInstance) => string;
          if (loc === 'trade_row') {
            cards = gameState.trade_row;
            getLocation = () => 'trade_row';
          } else if (loc === 'hand') {
            cards = currentPlayer.hand;
            getLocation = () => 'hand';
          } else if (loc === 'discard') {
            cards = currentPlayer.discard_pile;
            getLocation = () => 'discard';
          } else {
            cards = [...currentPlayer.hand, ...currentPlayer.discard_pile];
            getLocation = (card) =>
              currentPlayer.hand.some(c => c.instance_id === card.instance_id) ? 'hand' : 'discard';
          }
          const subtitle = loc === 'trade_row'
            ? 'Choose a card from the trade row to scrap'
            : `Choose a card from your ${loc.replace('_', ' ')} to scrap`;
          return (
            <CardPicker
              title="Scrap a Card"
              subtitle={subtitle}
              cards={cards}
              onSelect={(card) => handleResolveScrap(card, getLocation(card))}
              onSkip={pe.optional ? handleSkipEffect : undefined}
              isOptional={pe.optional}
            />
          );
        }
        if (pe.type === 'discard_card') {
          if (pe.target === 'self') {
            return (
              <CardPicker
                title="Discard a Card"
                subtitle="Choose a card from your hand to discard"
                cards={currentPlayer.hand}
                onSelect={(card) => handleResolveDiscard(card, currentPlayerId!)}
                onSkip={pe.optional ? handleSkipEffect : undefined}
                isOptional={pe.optional}
              />
            );
          }
          if (opponents.length === 0) return null;
          const allCards = opponents.flatMap(o => o.hand);
          const ownerById: Record<string, string> = {};
          const playerByCard: Record<string, string> = {};
          for (const opp of opponents) {
            for (const card of opp.hand) {
              ownerById[card.instance_id] = opp.name;
              playerByCard[card.instance_id] = opp.player_id;
            }
          }
          return (
            <CardPicker
              title="Choose a Card to Discard"
              subtitle={opponents.length === 1 ? `Choose a card from ${opponents[0].name}'s hand` : "Choose a card from an opponent's hand"}
              cards={allCards}
              cardOwners={opponents.length > 1 ? ownerById : undefined}
              onSelect={(card) => handleResolveDiscard(card, playerByCard[card.instance_id])}
              onSkip={pe.optional ? handleSkipEffect : undefined}
              isOptional={pe.optional}
            />
          );
        }
        if (pe.type === 'destroy_base') {
          const allBases = opponents.flatMap(o => o.bases.map(b => ({ ...b, _ownerId: o.player_id })));
          const ownerById: Record<string, string> = {};
          const playerByBase: Record<string, string> = {};
          for (const opp of opponents) {
            for (const base of opp.bases) {
              ownerById[base.instance_id] = opp.name;
              playerByBase[base.instance_id] = opp.player_id;
            }
          }
          return (
            <CardPicker
              title="Destroy a Base"
              subtitle="Choose an opponent's base to destroy"
              cards={allBases}
              cardOwners={opponents.length > 1 ? ownerById : undefined}
              onSelect={(card) => handleResolveDestroyBase(card, playerByBase[card.instance_id])}
              onSkip={pe.optional ? handleSkipEffect : undefined}
              isOptional={pe.optional}
            />
          );
        }
        if (pe.type === 'choice') {
          const labels = pe.labels ?? [];
          return (
            <ChoicePicker
              labels={labels}
              onSelect={handleResolveChoice}
            />
          );
        }
        if (pe.type === 'acquire_free_to_top') {
          const maxCost = pe.max_cost ?? 999;
          const cardType = pe.card_type ?? 'ship';
          const eligible = gameState.trade_row.filter(c =>
            c.cost <= maxCost && (
              cardType === 'ship' ? c.type !== 'Base' :
              cardType === 'base' ? c.type === 'Base' : true
            )
          );
          const explorerOk = cardType !== 'base' && gameState.explorer_pile.length > 0 && gameState.explorer_pile[0].cost <= maxCost;
          const allCards = explorerOk ? [...eligible, gameState.explorer_pile[0]] : eligible;
          return (
            <CardPicker
              title="Acquire for Free"
              subtitle={`Choose a ${cardType} (cost ≤ ${maxCost === 999 ? 'any' : maxCost}) — goes on top of your deck`}
              cards={allCards}
              onSelect={(card) => {
                const fromExp = explorerOk && card.instance_id === gameState.explorer_pile[0].instance_id;
                handleResolveAcquireFree(card, fromExp);
              }}
              isOptional={false}
            />
          );
        }
        if (pe.type === 'discard_any_number') {
          return (
            <CardPicker
              title="Discard for Combat"
              subtitle="Click cards to discard them (+2 Combat each). Click Skip when finished."
              cards={currentPlayer.hand}
              onSelect={handleResolveDiscardAny}
              onSkip={handleFinishDiscardAny}
              isOptional={true}
            />
          );
        }
        if (pe.type === 'copy_ship') {
          const copiableShips = currentPlayer.in_play.filter(c => c.type !== 'Base' && c.name !== 'Stealth Needle');
          return (
            <CardPicker
              title="Copy a Ship"
              subtitle="Choose a ship you've played this turn to copy its abilities"
              cards={copiableShips}
              onSelect={handleResolveCopyShip}
              isOptional={false}
            />
          );
        }
        if (pe.type === 'base_from_discard_to_top' && currentPlayer) {
          const bases = currentPlayer.discard_pile.filter(c => c.type === 'Base');
          return (
            <CardPicker
              title="Base to Top of Deck"
              subtitle="Choose a base from your discard pile to put on top of your deck"
              cards={bases}
              onSelect={handleResolveBaseToTop}
              onSkip={pe.optional ? handleSkipEffect : undefined}
              isOptional={pe.optional}
            />
          );
        }
        return null;
      })()}
    </div>
  );
}
