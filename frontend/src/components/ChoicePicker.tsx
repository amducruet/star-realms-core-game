import '../styles/CardPicker.css';

interface ChoicePickerProps {
  labels: string[];
  onSelect: (index: number) => void;
  onSkip?: () => void;
}

export function ChoicePicker({ labels, onSelect, onSkip }: ChoicePickerProps) {
  return (
    <div className="modal-overlay" onClick={onSkip}>
      <div className="card-picker" onClick={(e) => e.stopPropagation()}>
        <h2>Choose One</h2>
        <div className="card-picker-list">
          {labels.map((label, i) => (
            <div
              key={i}
              className="card-picker-item"
              onClick={() => onSelect(i)}
            >
              <span className="card-picker-item-name">
                {label.replace(/\{|\}/g, '').replace(/<[^>]+>/g, '').trim()}
              </span>
            </div>
          ))}
        </div>
        {onSkip && (
          <div className="card-picker-actions">
            <button className="btn-skip" onClick={onSkip}>Skip</button>
          </div>
        )}
      </div>
    </div>
  );
}
