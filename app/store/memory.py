"""In-memory data store."""

from threading import Lock

from app.schemas import (
    Brew,
    BrewQuery,
    Steep,
    Tea,
    TeaQuery,
    Teapot,
    TeapotQuery,
)
from app.schemas.common import PaginationQuery


class MemoryStore:
    """Thread-safe in-memory data store."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._teapots: dict[str, Teapot] = {}
        self._teas: dict[str, Tea] = {}
        self._brews: dict[str, Brew] = {}
        self._steeps: dict[str, Steep] = {}

    def clear(self) -> None:
        """Clear all data (useful for testing)."""
        with self._lock:
            self._teapots.clear()
            self._teas.clear()
            self._brews.clear()
            self._steeps.clear()

    # Teapot methods
    def list_teapots(self, query: TeapotQuery) -> tuple[list[Teapot], int]:
        """List teapots with pagination and filtering."""
        with self._lock:
            items = list(self._teapots.values())

            # Apply filters
            if query.material:
                items = [t for t in items if t.material == query.material]
            if query.style:
                items = [t for t in items if t.style == query.style]

            total = len(items)
            start = (query.page - 1) * query.limit
            end = start + query.limit

            return items[start:end], total

    def create_teapot(self, teapot: Teapot) -> None:
        """Create a new teapot."""
        with self._lock:
            self._teapots[teapot.id] = teapot

    def get_teapot(self, id: str) -> Teapot | None:
        """Get a teapot by ID."""
        with self._lock:
            return self._teapots.get(id)

    def update_teapot(self, teapot: Teapot) -> None:
        """Update an existing teapot."""
        with self._lock:
            self._teapots[teapot.id] = teapot

    def delete_teapot(self, id: str) -> bool:
        """Delete a teapot by ID. Returns True if deleted."""
        with self._lock:
            if id not in self._teapots:
                return False
            del self._teapots[id]
            return True

    # Tea methods
    def list_teas(self, query: TeaQuery) -> tuple[list[Tea], int]:
        """List teas with pagination and filtering."""
        with self._lock:
            items = list(self._teas.values())

            # Apply filters
            if query.type:
                items = [t for t in items if t.type == query.type]
            if query.caffeine_level:
                items = [t for t in items if t.caffeine_level == query.caffeine_level]

            total = len(items)
            start = (query.page - 1) * query.limit
            end = start + query.limit

            return items[start:end], total

    def create_tea(self, tea: Tea) -> None:
        """Create a new tea."""
        with self._lock:
            self._teas[tea.id] = tea

    def get_tea(self, id: str) -> Tea | None:
        """Get a tea by ID."""
        with self._lock:
            return self._teas.get(id)

    def update_tea(self, tea: Tea) -> None:
        """Update an existing tea."""
        with self._lock:
            self._teas[tea.id] = tea

    def delete_tea(self, id: str) -> bool:
        """Delete a tea by ID. Returns True if deleted."""
        with self._lock:
            if id not in self._teas:
                return False
            del self._teas[id]
            return True

    # Brew methods
    def list_brews(self, query: BrewQuery) -> tuple[list[Brew], int]:
        """List brews with pagination and filtering."""
        with self._lock:
            items = list(self._brews.values())

            # Apply filters
            if query.status:
                items = [b for b in items if b.status == query.status]
            if query.teapot_id:
                items = [b for b in items if b.teapot_id == query.teapot_id]
            if query.tea_id:
                items = [b for b in items if b.tea_id == query.tea_id]

            total = len(items)
            start = (query.page - 1) * query.limit
            end = start + query.limit

            return items[start:end], total

    def list_brews_by_teapot(
        self, teapot_id: str, query: PaginationQuery
    ) -> tuple[list[Brew], int]:
        """List brews for a specific teapot."""
        with self._lock:
            items = [b for b in self._brews.values() if b.teapot_id == teapot_id]

            total = len(items)
            start = (query.page - 1) * query.limit
            end = start + query.limit

            return items[start:end], total

    def create_brew(self, brew: Brew) -> None:
        """Create a new brew."""
        with self._lock:
            self._brews[brew.id] = brew

    def get_brew(self, id: str) -> Brew | None:
        """Get a brew by ID."""
        with self._lock:
            return self._brews.get(id)

    def update_brew(self, brew: Brew) -> None:
        """Update an existing brew."""
        with self._lock:
            self._brews[brew.id] = brew

    def delete_brew(self, id: str) -> bool:
        """Delete a brew by ID. Returns True if deleted."""
        with self._lock:
            if id not in self._brews:
                return False
            del self._brews[id]
            # Also delete associated steeps
            self._steeps = {
                k: v for k, v in self._steeps.items() if v.brew_id != id
            }
            return True

    # Steep methods
    def list_steeps_by_brew(
        self, brew_id: str, query: PaginationQuery
    ) -> tuple[list[Steep], int]:
        """List steeps for a specific brew."""
        with self._lock:
            items = [s for s in self._steeps.values() if s.brew_id == brew_id]
            # Sort by steep number
            items.sort(key=lambda s: s.steep_number)

            total = len(items)
            start = (query.page - 1) * query.limit
            end = start + query.limit

            return items[start:end], total

    def create_steep(self, steep: Steep) -> None:
        """Create a new steep."""
        with self._lock:
            self._steeps[steep.id] = steep

    def get_next_steep_number(self, brew_id: str) -> int:
        """Get the next steep number for a brew."""
        with self._lock:
            existing = [s for s in self._steeps.values() if s.brew_id == brew_id]
            if not existing:
                return 1
            return max(s.steep_number for s in existing) + 1

    def get_steep(self, id: str) -> Steep | None:
        """Get a steep by ID."""
        with self._lock:
            return self._steeps.get(id)


# Global store instance
store = MemoryStore()
