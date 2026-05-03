"""
Tests – Abstract Factory (NotificationFactory families)
=========================================================
Covers:
  - Each factory produces the correct concrete product types
  - Notification.send() marks notification as sent
  - Alert summary renders the correct channel-specific format
  - Factory selector raises on unknown channel
  - dispatch() returns both send_result and summary
"""

import pytest
from creational_patterns.abstract_factory import (
    EmailNotificationFactory,
    SMSNotificationFactory,
    get_notification_factory,
)
from src.models import FraudAlert, AlertSeverity, EmailNotification, SMSNotification


@pytest.fixture
def sample_alert():
    return FraudAlert(
        transaction_id="TXN-ABCD-1234",
        alert_type="VELOCITY_BREACH",
        severity=AlertSeverity.HIGH,
        description="Excessive transaction frequency detected.",
    )


class TestEmailNotificationFactory:

    def setup_method(self):
        self.factory = EmailNotificationFactory()

    def test_create_notification_returns_email_type(self, sample_alert):
        notification = self.factory.create_notification(sample_alert, "analyst@sentinelpay.io")
        assert isinstance(notification, EmailNotification)

    def test_send_marks_notification_as_sent(self, sample_alert):
        notification = self.factory.create_notification(sample_alert, "analyst@sentinelpay.io")
        notification.send()
        assert notification.sent is True

    def test_email_subject_contains_alert_type(self, sample_alert):
        notification = self.factory.create_notification(sample_alert, "analyst@sentinelpay.io")
        assert "VELOCITY_BREACH" in notification.subject

    def test_email_subject_contains_severity(self, sample_alert):
        notification = self.factory.create_notification(sample_alert, "analyst@sentinelpay.io")
        assert "HIGH" in notification.subject

    def test_create_summary_renders_email_format(self, sample_alert):
        summary = self.factory.create_summary(sample_alert, "analyst@sentinelpay.io")
        rendered = summary.render()
        assert "EMAIL" in rendered
        assert "VELOCITY_BREACH" in rendered

    def test_dispatch_returns_dict_with_both_keys(self, sample_alert):
        result = self.factory.dispatch(sample_alert, "analyst@sentinelpay.io")
        assert "send_result" in result
        assert "summary" in result


class TestSMSNotificationFactory:

    def setup_method(self):
        self.factory = SMSNotificationFactory()

    def test_create_notification_returns_sms_type(self, sample_alert):
        notification = self.factory.create_notification(sample_alert, "+27821234567")
        assert isinstance(notification, SMSNotification)

    def test_send_marks_notification_as_sent(self, sample_alert):
        notification = self.factory.create_notification(sample_alert, "+27821234567")
        notification.send()
        assert notification.sent is True

    def test_sms_body_contains_alert_type(self, sample_alert):
        notification = self.factory.create_notification(sample_alert, "+27821234567")
        assert "VELOCITY_BREACH" in notification.body

    def test_sms_summary_renders_sms_format(self, sample_alert):
        summary = self.factory.create_summary(sample_alert, "+27821234567")
        rendered = summary.render()
        assert "SentinelPay" in rendered


class TestGetNotificationFactory:

    def test_returns_email_factory_for_email_channel(self):
        factory = get_notification_factory("EMAIL")
        assert isinstance(factory, EmailNotificationFactory)

    def test_channel_lookup_is_case_insensitive(self):
        factory = get_notification_factory("sms")
        assert isinstance(factory, SMSNotificationFactory)

    def test_raises_for_unknown_channel(self):
        with pytest.raises(ValueError, match="No notification factory"):
            get_notification_factory("CARRIER_PIGEON")