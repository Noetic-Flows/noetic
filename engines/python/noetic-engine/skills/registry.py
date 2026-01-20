from typing import Dict, Optional
from .interfaces import Skill

class SkillRegistry:
    def __init__(self):
        self._skills: Dict[str, Skill] = {}

    def register(self, skill: Skill):
        if skill.id in self._skills:
            # Warning: Overwriting skill
            pass
        self._skills[skill.id] = skill

    def get_skill(self, skill_id: str) -> Optional[Skill]:
        return self._skills.get(skill_id)

    def has_permission(self, agent_id: str, skill_id: str) -> bool:
        # TODO: Integrate with Agent definition to check allowlist
        return True
