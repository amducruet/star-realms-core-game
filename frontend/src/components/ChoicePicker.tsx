import '../styles/CardPicker.css';

interface ChoicePickerProps {
  labels: string[];
  onSelect: (index: number) => void;
}

export function ChoicePicker({ labels, onSelect }: ChoicePickerProps) {
  return (
    <div className="modal-overlay">
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
      </div>
    </div>
  );
}
