import pytest
from unittest.mock import patch, MagicMock
from app.worker.tasks import (
    send_notification, 
    _get_notification_title, 
    _get_notification_message,
    _should_send_email,
    _send_email_notification,
    _send_push_notification,
    _send_sms_notification
)


class TestNotificationHelpers:
    """Test notification helper functions"""
    
    def test_get_notification_title(self):
        """Test notification title generation"""
        assert _get_notification_title("deal_status_update", {}) == "Deal Status Updated"
        assert _get_notification_title("new_matches_available", {}) == "New Matches Available"
        assert _get_notification_title("unknown_type", {}) == "Notification"
    
    def test_get_notification_message(self):
        """Test notification message generation"""
        # Deal status update
        data = {"new_status": "approved"}
        message = _get_notification_message("deal_status_update", data)
        assert "approved" in message
        
        # New matches
        data = {"matches_count": 5}
        message = _get_notification_message("new_matches_available", data)
        assert "5 new athlete matches" in message
        
        # Payment received
        data = {"amount": 1500.50}
        message = _get_notification_message("payment_received", data)
        assert "$1,500.50" in message
    
    def test_should_send_email(self):
        """Test email sending logic based on user preferences"""
        # User with email preferences
        user = MagicMock()
        user.email_preferences = {"deal_status_update": True, "profile_viewed": False}
        
        assert _should_send_email("deal_status_update", user) == True
        assert _should_send_email("profile_viewed", user) == False
        
        # User without preferences - should use defaults
        user.email_preferences = None
        assert _should_send_email("deal_status_update", user) == True  # Important notification
        assert _should_send_email("profile_viewed", user) == False     # Non-important
    
    @patch('smtplib.SMTP')
    @patch('app.core.config.settings')
    def test_send_email_notification(self, mock_settings, mock_smtp):
        """Test email notification sending"""
        # Mock settings
        mock_settings.SMTP_HOST = "smtp.example.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USE_TLS = True
        mock_settings.SMTP_USERNAME = "user"
        mock_settings.SMTP_PASSWORD = "pass"
        mock_settings.SMTP_FROM_EMAIL = "noreply@playright.ai"
        
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        _send_email_notification("test@example.com", "deal_status_update", {"new_status": "approved"})
        
        # Verify SMTP calls
        mock_smtp.assert_called_once_with("smtp.example.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("user", "pass")
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()
    
    @patch('requests.post')
    @patch('app.core.config.settings')
    def test_send_push_notification(self, mock_settings, mock_requests):
        """Test push notification sending"""
        mock_settings.FCM_SERVER_KEY = "test_key"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.return_value = mock_response
        
        _send_push_notification("test_token", "new_matches_available", {"matches_count": 3})
        
        # Verify FCM API call
        mock_requests.assert_called_once()
        call_args = mock_requests.call_args
        assert "https://fcm.googleapis.com/fcm/send" in call_args[1]["url"] or call_args[0][0] == "https://fcm.googleapis.com/fcm/send"
    
    @patch('requests.post')
    @patch('app.core.config.settings')
    def test_send_sms_notification(self, mock_settings, mock_requests):
        """Test SMS notification sending"""
        mock_settings.TWILIO_ACCOUNT_SID = "test_sid"
        mock_settings.TWILIO_AUTH_TOKEN = "test_token"
        mock_settings.TWILIO_PHONE_NUMBER = "+1234567890"
        
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_requests.return_value = mock_response
        
        _send_sms_notification("+0987654321", "deal_expired", {})
        
        # Verify Twilio API call
        mock_requests.assert_called_once()
        call_args = mock_requests.call_args
        assert "api.twilio.com" in (call_args[1].get("url", "") or call_args[0][0])


class TestNotificationTask:
    """Test the main notification task"""
    
    @patch('app.worker.tasks.pb_client')
    @patch('app.worker.tasks._send_email_notification')
    @patch('app.worker.tasks._send_push_notification')
    @patch('app.worker.tasks._send_sms_notification')
    def test_send_notification_task_complete_flow(self, mock_sms, mock_push, mock_email, mock_pb):
        """Test complete notification flow"""
        # Mock user data
        mock_user = MagicMock()
        mock_user.email = "test@example.com"
        mock_user.push_token = "test_push_token"
        mock_user.phone = "+1234567890"
        
        mock_pb.client.collection.return_value.get_one.return_value = mock_user
        mock_pb.client.collection.return_value.create.return_value = MagicMock()
        
        # Mock _should_send_email to return True
        with patch('app.worker.tasks._should_send_email', return_value=True):
            result = send_notification.apply(args=["user123", "deal_expired", {"deal_id": "deal123"}])
        
        # Verify all notification methods were called for urgent notification
        mock_email.assert_called_once()
        mock_push.assert_called_once()
        mock_sms.assert_called_once()
        
        # Verify in-app notification was created
        mock_pb.client.collection.assert_called()
        
        assert result.result["status"] == "sent"
    
    @patch('app.worker.tasks.pb_client')
    def test_send_notification_task_error_handling(self, mock_pb):
        """Test notification task error handling"""
        # Mock database error
        mock_pb.client.collection.return_value.get_one.side_effect = Exception("Database error")
        
        result = send_notification.apply(args=["user123", "test_type", {}])
        
        assert result.result["status"] == "failed"
        assert "Database error" in result.result["error"]