import pytest
from django.contrib.auth.models import User

from complaints.models import Complaint


@pytest.mark.django_db
def test_complaint_creation_and_inference():
    user = User.objects.create_user(username="alice", password="password")
    c = Complaint.objects.create(
        title="Broken fan in classroom",
        description="The fan in room 101 is broken and needs urgent repair.",
        created_by=user,
        anonymous=False,
    )
    # After save, inference should fill fields
    c.refresh_from_db()
    assert c.category != ""
    assert c.summary != ""
    assert c.priority in ["low", "medium", "high"]