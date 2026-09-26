"""
RKS Draft State Manager
Manages the current RKS draft state (in-memory + persisted to JSON).
Supports CRUD operations on bab/sub-bab for the hybrid revision workflow.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


DRAFTS_DIR = Path("./drafts")


class RKSDraft:
    """Manages the current RKS draft state."""

    def __init__(self):
        self.data: dict = {}
        self.draft_path: str = ""
        DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

    def create(self, structure: dict) -> None:
        """Initialize a new draft from AI-generated structure."""
        self.data = structure
        # Auto-set metadata if not present
        if "metadata" not in self.data:
            self.data["metadata"] = {}
        self.data["metadata"].setdefault("tanggal_dibuat", datetime.now().strftime("%Y-%m-%d"))
        self.data["metadata"].setdefault("versi", 1)
        # Auto-save
        self.save()

    def get_section(self, bab_nomor: str) -> Optional[dict]:
        """Get a single bab by its nomor (e.g., 'I', 'II', '1', '2')."""
        for bab in self.data.get("bab", []):
            if bab.get("nomor", "").upper() == bab_nomor.upper():
                return bab
        return None

    def update_section(self, bab_nomor: str, updated: dict) -> bool:
        """Update the content of a single bab."""
        for i, bab in enumerate(self.data.get("bab", [])):
            if bab.get("nomor", "").upper() == bab_nomor.upper():
                self.data["bab"][i] = updated
                self._increment_version()
                self.save()
                return True
        return False

    def add_section(self, bab: dict, position: int = -1) -> None:
        """Add a new bab at a given position (-1 = end)."""
        if "bab" not in self.data:
            self.data["bab"] = []
        if position < 0 or position >= len(self.data["bab"]):
            self.data["bab"].append(bab)
        else:
            self.data["bab"].insert(position, bab)
        self._increment_version()
        self.save()

    def remove_section(self, bab_nomor: str) -> bool:
        """Remove a bab by its nomor."""
        original_len = len(self.data.get("bab", []))
        self.data["bab"] = [
            b for b in self.data.get("bab", [])
            if b.get("nomor", "").upper() != bab_nomor.upper()
        ]
        if len(self.data["bab"]) < original_len:
            self._increment_version()
            self.save()
            return True
        return False

    def reorder_sections(self, new_order: list[str]) -> bool:
        """Reorder bab based on a list of nomor values."""
        bab_map = {b["nomor"].upper(): b for b in self.data.get("bab", [])}
        reordered = []
        for nomor in new_order:
            bab = bab_map.get(nomor.upper())
            if bab:
                reordered.append(bab)
            else:
                return False  # Unknown bab nomor
        self.data["bab"] = reordered
        self._increment_version()
        self.save()
        return True

    def update_cover(self, cover_data: dict) -> None:
        """Update cover page metadata."""
        if "cover_page" not in self.data:
            self.data["cover_page"] = {}
        self.data["cover_page"].update(cover_data)
        self._increment_version()
        self.save()

    def save(self) -> str:
        """Persist draft to a JSON file. Returns the file path."""
        if not self.draft_path:
            # Generate filename from judul_pekerjaan or timestamp
            name_part = self.data.get("cover_page", {}).get(
                "judul_pekerjaan", "draft"
            )
            # Sanitize filename
            safe_name = "".join(
                c if c.isalnum() or c in (" ", "-", "_") else "_"
                for c in name_part
            )[:60].strip()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"RKS_{safe_name}_{timestamp}.json"
            self.draft_path = str(DRAFTS_DIR / filename)

        with open(self.draft_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        return self.draft_path

    def load(self, path: str) -> None:
        """Load a draft from a JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        self.draft_path = path

    def get_summary(self) -> str:
        """Return a human-readable summary of the draft structure."""
        if not self.data:
            return "Tidak ada draft aktif."

        lines = []
        cover = self.data.get("cover_page", {})
        if cover:
            lines.append(f"📄 **{cover.get('judul_pekerjaan', 'Tanpa Judul')}**")
            if cover.get("nama_perusahaan"):
                lines.append(f"   🏢 {cover['nama_perusahaan']}")
            if cover.get("resiko_csms"):
                lines.append(f"   ⚠️ Risiko CSMS: {cover['resiko_csms']}")
            lines.append("")

        meta = self.data.get("metadata", {})
        if meta.get("nomor_dokumen"):
            lines.append(f"📋 No. Dokumen: {meta['nomor_dokumen']}")
        if meta.get("versi"):
            lines.append(f"🔄 Versi: {meta['versi']}")
        lines.append("")

        bab_list = self.data.get("bab", [])
        lines.append(f"📚 Struktur ({len(bab_list)} bab):")
        for bab in bab_list:
            nomor = bab.get("nomor", "?")
            judul = bab.get("judul", "Tanpa Judul")
            sub_count = len(bab.get("sub_bab", []))
            lines.append(f"   BAB {nomor} - {judul} ({sub_count} sub-bab)")
            for sub in bab.get("sub_bab", []):
                lines.append(f"      {sub.get('nomor', '?')}. {sub.get('judul', '')}")

        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Export the entire draft as a dict for rendering."""
        return self.data.copy()

    def is_active(self) -> bool:
        """Check if there is an active draft."""
        return bool(self.data and self.data.get("bab"))

    def _increment_version(self) -> None:
        """Increment the version counter."""
        if "metadata" not in self.data:
            self.data["metadata"] = {}
        current = self.data["metadata"].get("versi", 0)
        self.data["metadata"]["versi"] = current + 1
