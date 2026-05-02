#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Vietnamese pronoun selection from register policy and entity hints."""

from __future__ import annotations

from src.context.register_policy import RegisterPolicy


class VietnamesePronounSelector:
    """Select Vietnamese pronouns for resolved entity references."""

    def __init__(self, policy: RegisterPolicy | None = None):
        self.policy = policy or RegisterPolicy()

    def select_pronoun(
        self,
        *,
        gender: str | None = None,
        role: str = "subject",
        register: str = "xianxia",
    ) -> str:
        return self.policy.select(register=register, gender=gender, role=role)

    def select_for_entity(self, entity: dict, *, role: str = "subject", register: str = "xianxia") -> str:
        return self.select_pronoun(gender=str(entity.get("gender") or ""), role=role, register=register)
