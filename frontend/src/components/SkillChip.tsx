import type { Skill } from "../types";

type SkillChipProps = {
  skill: Skill;
  tone: "strength" | "missing";
};

export function SkillChip({ skill, tone }: SkillChipProps) {
  return <span className={`skill-chip ${tone}`}>{skill.name}</span>;
}
