import pygame
import math
import time
from collections import deque

class EnemyGroupManager:
    """
    Zarządza stanem skupisk wrogów.
    Odpowiada za:
    - wykrycie grupy min. X botów i zmiane ich stanu (BFS)
    - wyznaczenie jednego lidera ataku
    - zapobieganie efektowi łańcuchowemu
    """

    def __init__(self, enemy, min_group_size=10, attack_cooldown=4.0):
        self.enemy = enemy
        self.min_group_size = min_group_size
        self.attack_cooldown = attack_cooldown

        # aktualny lider grupy
        self.group_leader = None

        # timestamp startu cooldownu
        self.cooldown_start_time = None

    def find_full_group(self):
        """
        Zwraca pełną grupę używając BFS.
        """
        visited = set()
        queue = deque([self.enemy])

        visited.add(self.enemy)

        while queue:
            current = queue.popleft()
            for nb in current.neighbors:
                if nb not in visited and nb.state == "explore":
                    visited.add(nb)
                    queue.append(nb)

        return list(visited)

    def pick_new_leader(self, group):
        """
        Wybiera nowego lidera grupy spośród aktywnych członków.
        """
        alive_members = [e for e in group if e.state != "dead"]
        if not alive_members:
            self.group_leader = None
            return

        # kryterium wyboru lidera (np. najmniejszy id)
        new_leader = min(alive_members, key=lambda e: id(e))
        self.group_leader = new_leader

        # flagi wśród członków grupy
        for e in alive_members:
            e.is_group_leader = (e is new_leader)
            e.attack_group_id = id(new_leader) if e.state == "attack" else None
            # reset offset followers
            if not e.is_group_leader and hasattr(e, 'attack_offset'):
                del e.attack_offset  # wymusi losowanie w EnemySteering

    def update(self):
        """
        Podejmuje decyzję czy Enemy ma przejść w stan attack.
        wybiera nowego lidera, gdy obecny lider padł

        """
        if self.enemy.state == "attack" :
            if self.group_leader is not None and self.group_leader.state == "dead":
                alive_attackers = [e for e in self.find_full_group() if e.state == "attack"]
                if alive_attackers:
                    self.pick_new_leader(alive_attackers)
            return

        group = [e for e in self.find_full_group() if e.state == "explore"]
        group_size = len(group)

        if group_size < self.min_group_size:
            # grupa jest za mała - reset cooldown, pozostajemy w explore
            self.cooldown_start_time = None
            return

        # jeśli lider nie istnieje, wybierz lidera
        if self.group_leader is None or getattr(self.group_leader, 'state', None) == "dead":
            self.pick_new_leader(group)

        now = time.time()

        # start cooldown
        if self.cooldown_start_time is None:
            self.cooldown_start_time = now
            return  # czas na eksplorację

        # czy cooldown minął
        if now - self.cooldown_start_time >= self.attack_cooldown:
            # sprawdzamy ponownie, czy grupa jest nadal >= min_group_size
            group = [e for e in self.find_full_group() if e.state == "explore"]
            group_size = len(group)
            if group_size >= self.min_group_size:
                # atakujemy
                self.pick_new_leader(group)
                new_group_id = id(self.group_leader)
                for e in group:
                    e.state = "attack"
                    e.attack_group_id = new_group_id
                    e.is_group_leader = (e is self.group_leader)
                # reset cooldown
                self.cooldown_start_time = None
