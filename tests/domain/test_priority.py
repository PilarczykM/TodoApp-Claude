from src.domain.priority import Priority


class TestPriority:
    def test_priority_enum_values(self):
        assert Priority.LOW == "low"
        assert Priority.MEDIUM == "medium"
        assert Priority.HIGH == "high"

    def test_priority_enum_membership(self):
        assert "low" in Priority
        assert "medium" in Priority
        assert "high" in Priority
        assert "invalid" not in Priority
