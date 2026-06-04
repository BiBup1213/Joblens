import { Plus } from "lucide-react";

type FloatingAddButtonProps = {
  onClick: () => void;
};

export function FloatingAddButton({ onClick }: FloatingAddButtonProps) {
  return (
    <button
      className="floating-add-button"
      type="button"
      aria-label="Neue Stelle hinzufügen"
      onClick={onClick}
    >
      <Plus aria-hidden="true" size={40} strokeWidth={2.5} />
    </button>
  );
}
