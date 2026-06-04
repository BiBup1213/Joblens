import type { FitLevel } from "../types";
import type { CSSProperties } from "react";

const fitOrder: FitLevel[] = [
  "Passt nicht so gut",
  "Passt teilweise",
  "Passt gut",
  "Passt sehr gut",
  "Passt hervorragend",
];

const segmentColors = [
  "#f7e7b7",
  "#f6d786",
  "#f2bd43",
  "#d6c95a",
  "#94cf8a",
  "#48c6ac",
  "#10aeca",
];

type FitScaleProps = {
  fit: FitLevel;
};

export function FitScale({ fit }: FitScaleProps) {
  const activeSegments = fitOrder.indexOf(fit) + 3;

  return (
    <div className="fit-row">
      <div className="fit-copy">
        <span className="meta-label">Passform</span>
        <div className="fit-scale" aria-label={`Passform: ${fit}`}>
          {segmentColors.map((color, index) => (
            <span
              className={`fit-segment${
                index < activeSegments ? " is-active" : ""
              }`}
              key={color}
              style={{ "--segment-color": color } as CSSProperties}
            />
          ))}
        </div>
      </div>
      <span className="fit-label">{fit}</span>
    </div>
  );
}
