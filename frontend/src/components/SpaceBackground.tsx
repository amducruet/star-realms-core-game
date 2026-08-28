import '../styles/SpaceBackground.css';

export function SpaceBackground() {
  return (
    <div className="space-bg" aria-hidden="true">
      <div className="space-stars space-stars--small" />
      <div className="space-stars space-stars--medium" />
      <div className="space-nebula space-nebula--1" />
      <div className="space-nebula space-nebula--2" />
    </div>
  );
}
