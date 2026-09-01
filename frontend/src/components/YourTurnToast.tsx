import { useEffect, useRef, useState } from 'react';
import '../styles/animations.css';

interface YourTurnToastProps {
  isMyTurn: boolean;
}

export function YourTurnToast({ isMyTurn }: YourTurnToastProps) {
  const [visible, setVisible] = useState(false);
  const [leaving, setLeaving] = useState(false);
  const prevTurn = useRef(isMyTurn);
  const leaveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (isMyTurn && !prevTurn.current) {
      // Turn just became ours
      setLeaving(false);
      setVisible(true);
      if (leaveTimer.current) clearTimeout(leaveTimer.current);
      leaveTimer.current = setTimeout(() => {
        setLeaving(true);
        setTimeout(() => setVisible(false), 300);
      }, 2400);
    }
    prevTurn.current = isMyTurn;
    return () => { if (leaveTimer.current) clearTimeout(leaveTimer.current); };
  }, [isMyTurn]);

  if (!visible) return null;

  return (
    <div className={`your-turn-toast ${leaving ? 'your-turn-toast--out' : 'your-turn-toast--in'}`}>
      ⚔️ Your Turn
    </div>
  );
}
