"""
test_mystic.py — C8 Mystic Engine tests (MBTI + эннеаграмма в скоринге).

Покрывает:
  - compute_mystic_score — совместимые / несовместимые / отсутствующие MBTI и эннеаграмма
  - score_pair_with_mystic — с mystic данными и без (фоллбэк на FounderFit)
  - MBTI_TYPES — словарь содержит все 16 типов
"""

from core.mystic.analysis import compute_mystic_score
from core.mystic.mbti import MBTI_TYPES
from scoring import FounderProfile, score_pair_with_mystic


# ─── Фикстуры профилей ────────────────────────────────────────────────────────

def _profile(user_id: str = "a", role: str = "builder") -> FounderProfile:
    return FounderProfile(
        user_id=user_id,
        time_commitment=80.0,
        no_salary_readiness=70.0,
        intent_goal="build_company",
        launched_projects=50.0,
        self_execution_breadth=60.0,
        primary_role=role,
        no_go_roles=[],
        decision_style="discuss_first",
        conflict_style="calm_discussion",
        work_mode="tight_pair",
        tempo="iterate_fast",
        sync_frequency=60.0,
        accountability_disappear=70.0,
        accountability_ownership=80.0,
    )


# ─── compute_mystic_score ─────────────────────────────────────────────────────

class TestComputeMysticScore:

    def test_compute_mystic_score_compatible(self):
        """INTJ × ENFP — прямо совместимые → mbti_score = 100."""
        a = {"mbti_type": "INTJ", "enneagram_type": 4}
        b = {"mbti_type": "ENFP", "enneagram_type": 5}
        result = compute_mystic_score(a, b)
        assert result["mbti_score"] == 100.0
        # 4 ↔ 5: соседние → enneagram_score = 80
        assert result["enneagram_score"] == 80.0
        # 0.6 * 100 + 0.4 * 80 = 92
        assert result["mystic_total"] == 92.0
        assert result["mbti_a"] == "INTJ"
        assert result["mbti_b"] == "ENFP"
        assert result["enneagram_a"] == 4
        assert result["enneagram_b"] == 5

    def test_compute_mystic_score_incompatible(self):
        """INTJ × ISTJ — не в compatible_with → mbti_score = 50."""
        a = {"mbti_type": "INTJ"}
        b = {"mbti_type": "ISTJ"}
        result = compute_mystic_score(a, b)
        assert result["mbti_score"] == 50.0

    def test_compute_mystic_score_neutral(self):
        """Нет ни MBTI, ни эннеаграммы → всё по 50 → mystic_total = 50."""
        result = compute_mystic_score({}, {})
        assert result["mbti_score"] == 50.0
        assert result["enneagram_score"] == 50.0
        assert result["mystic_total"] == 50.0
        assert result["mbti_a"] is None
        assert result["mbti_b"] is None
        assert result["enneagram_a"] is None
        assert result["enneagram_b"] is None

    def test_enneagram_same(self):
        """Одинаковые типы эннеаграммы → 60."""
        a = {"enneagram_type": 7}
        b = {"enneagram_type": 7}
        result = compute_mystic_score(a, b)
        assert result["enneagram_score"] == 60.0

    def test_enneagram_wraparound(self):
        """9 и 1 — соседние по кругу (diff == 8) → 80."""
        a = {"enneagram_type": 9}
        b = {"enneagram_type": 1}
        result = compute_mystic_score(a, b)
        assert result["enneagram_score"] == 80.0

    def test_enneagram_distant(self):
        """1 и 5 — не соседи и не равны → 40."""
        a = {"enneagram_type": 1}
        b = {"enneagram_type": 5}
        result = compute_mystic_score(a, b)
        assert result["enneagram_score"] == 40.0


# ─── score_pair_with_mystic ───────────────────────────────────────────────────

class TestScorePairWithMystic:

    def test_score_pair_with_mystic(self):
        """С mystic: total = 0.75*founder_fit + 0.25*mystic_total."""
        a = _profile("a", role="builder")
        b = _profile("b", role="seller")
        mystic_a = {"mbti_type": "INTJ", "enneagram_type": 4}
        mystic_b = {"mbti_type": "ENFP", "enneagram_type": 5}

        result = score_pair_with_mystic(a, b, mystic_a, mystic_b)

        assert "founder_fit_score" in result
        assert "mystic" in result and result["mystic"] is not None
        assert "total_score" in result
        assert "breakdown" in result

        ff = result["founder_fit_score"]
        mt = result["mystic"]["mystic_total"]
        expected_total = round(0.75 * ff + 0.25 * mt, 2)
        # clamp округляет до 2 знаков, разрешаем небольшой допуск
        assert abs(result["total_score"] - expected_total) < 0.5

    def test_score_pair_without_mystic(self):
        """Без mystic: total_score == total_compatibility_score (старая формула)."""
        a = _profile("a", role="builder")
        b = _profile("b", role="seller")

        result = score_pair_with_mystic(a, b, None, None)

        assert result["mystic"] is None
        assert result["total_score"] == result["breakdown"]["total_compatibility_score"]

    def test_score_pair_mystic_only_one_side(self):
        """Если только одна сторона имеет mystic — фолбэк на founder_fit."""
        a = _profile("a", role="builder")
        b = _profile("b", role="seller")
        result = score_pair_with_mystic(a, b, {"mbti_type": "INTJ"}, None)
        assert result["mystic"] is None

    def test_score_pair_with_mystic_improves_when_compatible(self):
        """Совместимый mystic должен поднять total относительно нейтрального."""
        a = _profile("a", role="builder")
        b = _profile("b", role="seller")

        neutral = score_pair_with_mystic(a, b, {}, {})
        compat = score_pair_with_mystic(
            a, b,
            {"mbti_type": "INTJ", "enneagram_type": 4},
            {"mbti_type": "ENFP", "enneagram_type": 5},
        )
        assert compat["total_score"] >= neutral["total_score"]


# ─── MBTI catalog integrity ──────────────────────────────────────────────────

class TestMBTITypes:

    def test_mbti_types_loaded(self):
        """MBTI_TYPES должен содержать все 16 типов."""
        assert len(MBTI_TYPES) == 16
        expected = {
            "INTJ", "INTP", "ENTJ", "ENTP",
            "INFJ", "INFP", "ENFJ", "ENFP",
            "ISTJ", "ISFJ", "ESTJ", "ESFJ",
            "ISTP", "ISFP", "ESTP", "ESFP",
        }
        assert set(MBTI_TYPES.keys()) == expected

    def test_each_type_has_compatible_with(self):
        for code, t in MBTI_TYPES.items():
            assert t.code == code
            assert isinstance(t.compatible_with, list)
            assert len(t.compatible_with) >= 1
