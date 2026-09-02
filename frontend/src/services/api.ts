/**
 * API service for communicating with backend.
 */

const BACKEND_URL = import.meta.env.VITE_API_URL ?? '';
const API_BASE = `${BACKEND_URL}/api`;

export interface ApiResponse<T = any> {
  status: string;
  game?: T;
  error?: string;
}

class ApiService {
  async createGame(gameId: string, playerNames: string[], aiCount: number = 0, startingAuthority: number = 50): Promise<ApiResponse> {
    const response = await fetch(`${API_BASE}/games/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        game_id: gameId,
        player_names: playerNames,
        ai_count: aiCount,
        starting_authority: startingAuthority,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create game');
    }

    return response.json();
  }

  async joinGame(gameId: string, playerName: string): Promise<ApiResponse & { player_id?: string }> {
    const response = await fetch(`${API_BASE}/games/${gameId}/join`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_name: playerName }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to join game');
    }

    return response.json();
  }

  async startGame(gameId: string): Promise<ApiResponse> {
    const response = await fetch(`${API_BASE}/games/${gameId}/start`, {
      method: 'POST',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to start game');
    }

    return response.json();
  }

  async getGame(gameId: string): Promise<ApiResponse> {
    const response = await fetch(`${API_BASE}/games/${gameId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get game');
    }

    return response.json();
  }

  async playCard(gameId: string, playerId: string, instanceId: string): Promise<ApiResponse> {
    const response = await fetch(`${API_BASE}/games/${gameId}/play_card`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId, instance_id: instanceId }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to play card');
    }

    return response.json();
  }

  async playHand(gameId: string, playerId: string): Promise<ApiResponse> {
    const response = await fetch(`${API_BASE}/games/${gameId}/play_hand`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to play hand');
    }
    return response.json();
  }

  async acquireCard(
    gameId: string,
    playerId: string,
    instanceId: string,
    fromExplorers: boolean = false
  ): Promise<ApiResponse> {
    const response = await fetch(`${API_BASE}/games/${gameId}/acquire_card`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        player_id: playerId,
        instance_id: instanceId,
        from_explorers: fromExplorers,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to acquire card');
    }

    return response.json();
  }

  async attackPlayer(
    gameId: string,
    playerId: string,
    targetPlayerId: string,
    damage?: number
  ): Promise<ApiResponse> {
    const response = await fetch(`${API_BASE}/games/${gameId}/attack_player`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        player_id: playerId,
        target_player_id: targetPlayerId,
        damage,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to attack player');
    }

    return response.json();
  }

  async distributeDamage(
    gameId: string,
    playerId: string,
    targets: Array<{ player_id: string; damage: number }>
  ): Promise<ApiResponse> {
    const response = await fetch(`${API_BASE}/games/${gameId}/distribute_damage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        player_id: playerId,
        targets,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to distribute damage');
    }

    return response.json();
  }

  async attackBase(
    gameId: string,
    playerId: string,
    targetPlayerId: string,
    instanceId: string,
    damage: number
  ): Promise<ApiResponse> {
    const response = await fetch(`${API_BASE}/games/${gameId}/attack_base`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        player_id: playerId,
        target_player_id: targetPlayerId,
        instance_id: instanceId,
        damage,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to attack base');
    }

    return response.json();
  }

  async endTurn(gameId: string, playerId: string): Promise<ApiResponse> {
    const response = await fetch(`${API_BASE}/games/${gameId}/end_turn`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to end turn');
    }

    return response.json();
  }

  async executeAiTurn(gameId: string): Promise<ApiResponse> {
    const response = await fetch(`${API_BASE}/games/${gameId}/ai_turn`, {
      method: 'POST',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to execute AIturn');
    }

    return response.json();
  }

  async resolveAcquireFree(gameId: string, playerId: string, instanceId: string, fromExplorers: boolean = false): Promise<ApiResponse> {
    const response = await fetch(`${API_BASE}/games/${gameId}/resolve_acquire_free`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId, instance_id: instanceId, from_explorers: fromExplorers }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to resolve acquire free');
    }
    return response.json();
  }

  async resolveBaseToTop(gameId: string, playerId: string, instanceId: string): Promise<ApiResponse> {
    const response = await fetch(`${API_BASE}/games/${gameId}/resolve_base_to_top`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId, instance_id: instanceId }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to resolve base to top');
    }
    return response.json();
  }

  async resolveChoice(gameId: string, playerId: string, optionIndex: number): Promise<ApiResponse> {
    const response = await fetch(`${API_BASE}/games/${gameId}/resolve_choice`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId, option_index: optionIndex }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to resolve choice');
    }
    return response.json();
  }

  async scrapCard(gameId: string, playerId: string, instanceId: string): Promise<ApiResponse> {
    const response = await fetch(`${API_BASE}/games/${gameId}/scrap_card`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId, instance_id: instanceId }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to scrap card');
    }

    return response.json();
  }
  async resolveScrap(gameId: string, playerId: string, instanceId: string, location: string): Promise<ApiResponse> {
    const response = await fetch(`${API_BASE}/games/${gameId}/resolve_scrap`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId, instance_id: instanceId, location }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to resolve scrap');
    }
    return response.json();
  }

  async resolveDiscard(gameId: string, playerId: string, targetPlayerId: string, instanceId: string): Promise<ApiResponse> {
    const response = await fetch(`${API_BASE}/games/${gameId}/resolve_discard`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId, target_player_id: targetPlayerId, instance_id: instanceId }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to resolve discard');
    }
    return response.json();
  }

  async resolveDiscardAny(gameId: string, playerId: string, instanceId: string): Promise<ApiResponse> {
    const response = await fetch(`${API_BASE}/games/${gameId}/resolve_discard_any`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId, instance_id: instanceId }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed');
    }
    return response.json();
  }

  async finishDiscardAny(gameId: string, playerId: string): Promise<ApiResponse> {
    const response = await fetch(`${API_BASE}/games/${gameId}/finish_discard_any`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed');
    }
    return response.json();
  }

  async resolveCopyShip(gameId: string, playerId: string, instanceId: string): Promise<ApiResponse> {
    const response = await fetch(`${API_BASE}/games/${gameId}/resolve_copy_ship`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId, instance_id: instanceId }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed');
    }
    return response.json();
  }

  async resolveDestroyBase(gameId: string, playerId: string, targetPlayerId: string, instanceId: string): Promise<ApiResponse> {
    const response = await fetch(`${API_BASE}/games/${gameId}/resolve_destroy_base`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId, target_player_id: targetPlayerId, instance_id: instanceId }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to resolve destroy base');
    }
    return response.json();
  }

  async skipEffect(gameId: string, playerId: string): Promise<ApiResponse> {
    const response = await fetch(`${API_BASE}/games/${gameId}/skip_effect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to skip effect');
    }
    return response.json();
  }
}

export const api = new ApiService();
