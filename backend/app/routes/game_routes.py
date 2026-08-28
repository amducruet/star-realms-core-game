"""
Game API routes.
"""
from typing import List
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

import asyncio

from app.services.game_service import game_service
from app.services.ai_service import ai_service as ai_service_instance
from app.websocket_manager import manager


router = APIRouter()


# Request/Response models
class CreateGameRequest(BaseModel):
    game_id: str
    player_names: List[str]
    ai_count: int = 0
    starting_authority: int = 50


class GameActionRequest(BaseModel):
    player_id: str


class PlayCardRequest(GameActionRequest):
    instance_id: str


class AcquireCardRequest(GameActionRequest):
    instance_id: str
    from_explorers: bool = False


class AttackPlayerRequest(GameActionRequest):
    target_player_id: str
    damage: int = None


class DistributeDamageRequest(GameActionRequest):
    targets: List[dict]  # [{"player_id": str, "damage": int}, ...]


class AttackBaseRequest(GameActionRequest):
    target_player_id: str
    instance_id: str
    damage: int


class ScrapCardRequest(GameActionRequest):
    instance_id: str


class ResolveScrapRequest(GameActionRequest):
    instance_id: str
    location: str


class ResolveDiscardRequest(GameActionRequest):
    instance_id: str
    target_player_id: str


class ResolveChoiceRequest(GameActionRequest):
    option_index: int


class ResolveAcquireFreeRequest(GameActionRequest):
    instance_id: str
    from_explorers: bool = False


class ResolveBaseToTopRequest(GameActionRequest):
    instance_id: str


class ResolveScrapRequest(GameActionRequest):
    instance_id: str
    location: str  # "hand" or "discard"


class ResolveDiscardRequest(GameActionRequest):
    instance_id: str
    target_player_id: str


class SkipEffectRequest(GameActionRequest):
    pass


class ResolveDiscardAnyRequest(GameActionRequest):
    instance_id: str


class FinishDiscardAnyRequest(GameActionRequest):
    pass


class ResolveCopyShipRequest(GameActionRequest):
    instance_id: str

@router.post("/games/create")
async def create_game(request: CreateGameRequest):
    """Create a new game."""
    try:
        game = game_service.create_game(
            game_id=request.game_id,
            player_names=request.player_names,
            ai_count=request.ai_count,
            starting_authority=request.starting_authority
        )
        return {"status": "success", "game": game.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class JoinGameRequest(BaseModel):
    player_name: str


@router.post("/games/{game_id}/join")
async def join_game(game_id: str, request: JoinGameRequest):
    """Join an existing lobby-phase game as a new human player."""
    try:
        game, player_id = game_service.join_game(game_id, request.player_name)
        await manager.broadcast(game_id, {"type": "player_joined", "game": game.model_dump()})
        return {"status": "success", "game": game.model_dump(), "player_id": player_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/games/{game_id}/start")
async def start_game(game_id: str):
    """Start a game."""
    try:
        game = game_service.start_game(game_id)
        # Broadcast game state to all connected clients
        await manager.broadcast(game_id, {
            "type": "game_started",
            "game": game.model_dump()
        })
        return {"status": "success", "game": game.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/games/{game_id}")
async def get_game(game_id: str):
    """Get current game state."""
    game = game_service.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return {"status": "success", "game": game.model_dump()}


@router.post("/games/{game_id}/play_card")
async def play_card(game_id: str, request: PlayCardRequest):
    """Play a card from hand."""
    try:
        game = game_service.play_card(game_id, request.player_id, request.instance_id)
        await manager.broadcast(game_id, {
            "type": "card_played",
            "game": game.model_dump()
        })
        return {"status": "success", "game": game.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/games/{game_id}/acquire_card")
async def acquire_card(game_id: str, request: AcquireCardRequest):
    """Acquire a card from trade row or explorer pile."""
    try:
        game = game_service.acquire_card(
            game_id,
            request.player_id,
            request.instance_id,
            request.from_explorers
        )
        await manager.broadcast(game_id, {
            "type": "card_acquired",
            "game": game.model_dump()
        })
        return {"status": "success", "game": game.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/games/{game_id}/attack_player")
async def attack_player(game_id: str, request: AttackPlayerRequest):
    """Attack a player."""
    try:
        game = game_service.attack_opponent(
            game_id,
            request.player_id,
            request.target_player_id,
            request.damage
        )
        await manager.broadcast(game_id, {
            "type": "player_attacked",
            "game": game.model_dump()
        })
        return {"status": "success", "game": game.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/games/{game_id}/distribute_damage")
async def distribute_damage(game_id: str, request: DistributeDamageRequest):
    """Distribute damage among multiple opponents."""
    try:
        game = game_service.distribute_damage(
            game_id,
            request.player_id,
            request.targets
        )
        await manager.broadcast(game_id, {
            "type": "damage_distributed",
            "game": game.model_dump()
        })
        return {"status": "success", "game": game.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/games/{game_id}/attack_base")
async def attack_base(game_id: str, request: AttackBaseRequest):
    """Attack a base."""
    try:
        game = game_service.attack_base(
            game_id,
            request.player_id,
            request.target_player_id,
            request.instance_id,
            request.damage
        )
        await manager.broadcast(game_id, {
            "type": "base_attacked",
            "game": game.model_dump()
        })
        return {"status": "success", "game": game.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/games/{game_id}/scrap_card")
async def scrap_card(game_id: str, request: ScrapCardRequest):
    """Scrap a card from play to activate its scrap ability."""
    try:
        game = game_service.scrap_card(game_id, request.player_id, request.instance_id)
        await manager.broadcast(game_id, {
            "type": "card_scrapped",
            "game": game.model_dump()
        })
        return {"status": "success", "game": game.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/games/{game_id}/end_turn")
async def end_turn(game_id: str, request: GameActionRequest):
    """End the current turn."""
    try:
        game = game_service.end_turn(game_id, request.player_id)
        await manager.broadcast(game_id, {
            "type": "turn_ended",
            "game": game.model_dump()
        })
        return {"status": "success", "game": game.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/games/{game_id}/ai_turn")
async def execute_ai_turn(game_id: str):
    """Execute AIturn step-by-step, broadcasting intermediate states with delays."""
    try:
        game = game_service.get_game(game_id)
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")

        current_player = game.players[game.current_player_index]
        if not current_player.is_ai:
            raise HTTPException(status_code=400, detail="Current player is not AI")

        actions = ai_service_instance._plan_actions(game, current_player)

        for action in actions:
            action_type = action.get("type")

            if action_type == "play_all_cards":
                played = set()
                while True:
                    cp = game.get_player(current_player.player_id)
                    unplayed = [c for c in cp.hand if c.instance_id not in played]
                    if not unplayed:
                        break
                    card = unplayed[0]
                    played.add(card.instance_id)
                    game = game_service.play_card(game.game_id, current_player.player_id, card.instance_id)
                    game = ai_service_instance._resolve_pending_effect(game, current_player, game_service)
                    await manager.broadcast(game_id, {"type": "ai_card_played", "game": game.model_dump()})
                    await asyncio.sleep(0.45)

            elif action_type == "buy_cards":
                cp = game.get_player(current_player.player_id)
                while cp.trade > 0:
                    affordable = [(c, False) for c in game.trade_row if c.cost <= cp.trade]
                    if game.explorer_pile and cp.trade >= 2:
                        affordable.append((game.explorer_pile[0], True))
                    if not affordable:
                        break
                    affordable.sort(key=lambda x: x[0].cost, reverse=True)
                    best_card, from_explorers = affordable[0]
                    game = game_service.acquire_card(game.game_id, current_player.player_id, best_card.instance_id, from_explorers)
                    cp = game.get_player(current_player.player_id)
                    await manager.broadcast(game_id, {"type": "ai_card_acquired", "game": game.model_dump()})
                    await asyncio.sleep(0.35)

            elif action_type == "attack_phase":
                cp = game.get_player(current_player.player_id)
                opponents = [p for p in game.players if p.player_id != current_player.player_id and p.authority > 0]
                if opponents and cp.combat > 0:
                    target = min(opponents, key=lambda p: p.authority)
                    outposts = [b for b in target.bases if b.is_outpost]
                    for outpost in outposts:
                        cp = game.get_player(current_player.player_id)
                        if cp.combat >= outpost.current_defense:
                            await manager.broadcast(game_id, {
                                "type": "combat_attack",
                                "attacker_id": current_player.player_id,
                                "target_id": target.player_id,
                                "base_id": outpost.instance_id,
                                "damage": outpost.current_defense,
                                "game": game.model_dump()
                            })
                            await asyncio.sleep(1.2)
                            game = game_service.attack_base(game.game_id, current_player.player_id, target.player_id, outpost.instance_id, outpost.current_defense)
                            await manager.broadcast(game_id, {"type": "base_attacked", "game": game.model_dump()})
                            await asyncio.sleep(0.6)
                    cp = game.get_player(current_player.player_id)
                    if cp.combat > 0:
                        await manager.broadcast(game_id, {
                            "type": "combat_attack",
                            "attacker_id": current_player.player_id,
                            "target_id": target.player_id,
                            "base_id": None,
                            "damage": cp.combat,
                            "game": game.model_dump()
                        })
                        await asyncio.sleep(1.2)
                        game = game_service.attack_opponent(game.game_id, current_player.player_id, target.player_id, None)
                        await manager.broadcast(game_id, {"type": "player_attacked", "game": game.model_dump()})
                        await asyncio.sleep(0.6)

            elif action_type == "end_turn":
                game = game_service.end_turn(game.game_id, current_player.player_id)
                await manager.broadcast(game_id, {"type": "ai_turn_completed", "game": game.model_dump()})

        return {"status": "success", "game": game.model_dump()}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))



@router.post("/games/{game_id}/resolve_scrap")
async def resolve_scrap(game_id: str, request: ResolveScrapRequest):
    """Resolve a pending scrap effect by choosing a card from hand or discard."""
    try:
        game = game_service.resolve_scrap(game_id, request.player_id, request.instance_id, request.location)
        await manager.broadcast(game_id, {
            "type": "effect_resolved",
            "game": game.model_dump()
        })
        return {"status": "success", "game": game.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/games/{game_id}/resolve_discard")
async def resolve_discard(game_id: str, request: ResolveDiscardRequest):
    """Resolve a pending discard effect by choosing a card from the target's hand."""
    try:
        game = game_service.resolve_discard(game_id, request.player_id, request.target_player_id, request.instance_id)
        await manager.broadcast(game_id, {
            "type": "effect_resolved",
            "game": game.model_dump()
        })
        return {"status": "success", "game": game.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/games/{game_id}/skip_effect")
async def skip_effect(game_id: str, request: SkipEffectRequest):
    """Skip an optional pending effect."""
    try:
        game = game_service.skip_effect(game_id, request.player_id)
        await manager.broadcast(game_id, {
            "type": "effect_skipped",
            "game": game.model_dump()
        })
        return {"status": "success", "game": game.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/games/{game_id}/resolve_choice")
async def resolve_choice(game_id: str, request: ResolveChoiceRequest):
    """Resolve a pending OR choice effect."""
    try:
        game = game_service.resolve_choice(game_id, request.player_id, request.option_index)
        await manager.broadcast(game_id, {"type": "choice_resolved", "game": game.model_dump()})
        return {"status": "success", "game": game.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/games/{game_id}/resolve_acquire_free")
async def resolve_acquire_free(game_id: str, request: ResolveAcquireFreeRequest):
    """Acquire a card for free and place it on top of deck."""
    try:
        game = game_service.resolve_acquire_free_to_top(game_id, request.player_id, request.instance_id, request.from_explorers)
        await manager.broadcast(game_id, {"type": "acquire_free_resolved", "game": game.model_dump()})
        return {"status": "success", "game": game.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/games/{game_id}/resolve_base_to_top")
async def resolve_base_to_top(game_id: str, request: ResolveBaseToTopRequest):
    """Move a base from discard pile to top of deck."""
    try:
        game = game_service.resolve_base_from_discard_to_top(game_id, request.player_id, request.instance_id)
        await manager.broadcast(game_id, {"type": "base_to_top_resolved", "game": game.model_dump()})
        return {"status": "success", "game": game.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/games/{game_id}/resolve_discard_any")
async def resolve_discard_any(game_id: str, request: ResolveDiscardAnyRequest):
    """Discard one card as part of a discard_any_number effect."""
    try:
        game = game_service.resolve_discard_any(game_id, request.player_id, request.instance_id)
        await manager.broadcast(game_id, {"type": "effect_resolved", "game": game.model_dump()})
        return {"status": "success", "game": game.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/games/{game_id}/finish_discard_any")
async def finish_discard_any(game_id: str, request: FinishDiscardAnyRequest):
    """Finish the discard_any_number effect."""
    try:
        game = game_service.finish_discard_any(game_id, request.player_id)
        await manager.broadcast(game_id, {"type": "effect_resolved", "game": game.model_dump()})
        return {"status": "success", "game": game.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/games/{game_id}/resolve_copy_ship")
async def resolve_copy_ship(game_id: str, request: ResolveCopyShipRequest):
    """Copy the abilities of a ship played this turn."""
    try:
        game = game_service.resolve_copy_ship(game_id, request.player_id, request.instance_id)
        await manager.broadcast(game_id, {"type": "copy_ship_resolved", "game": game.model_dump()})
        return {"status": "success", "game": game.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    """WebSocket endpoint for real-time game updates."""
    await manager.connect(websocket, game_id)
    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_json()

            # Echo back for now (client actions go through HTTP API)
            await websocket.send_json({"type": "pong", "data": data})

    except WebSocketDisconnect:
        manager.disconnect(websocket, game_id)
