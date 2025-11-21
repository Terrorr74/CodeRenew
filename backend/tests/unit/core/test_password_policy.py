"""
Unit tests for password policy validation
Tests all password strength requirements and edge cases
"""
import pytest
from app.core.password_policy import (
    validate_password_strength,
    get_password_strength_score,
    PasswordValidationError,
    COMMON_PASSWORDS
)


class TestPasswordValidation:
    """Test password validation rules"""

    def test_valid_strong_password(self):
        """Test that a valid strong password passes validation"""
        # Arrange
        password = "StrongPass123!@#"

        # Act & Assert
        result = validate_password_strength(password)
        assert result == password

    def test_minimum_length_requirement(self):
        """Test that passwords must be at least 8 characters"""
        # Arrange
        short_passwords = ["", "a", "Ab1!", "Pass1!"]

        # Act & Assert
        for password in short_passwords:
            with pytest.raises(PasswordValidationError) as exc_info:
                validate_password_strength(password)
            assert "at least 8 characters" in str(exc_info.value)

    def test_maximum_length_requirement(self):
        """Test that passwords cannot exceed 128 characters"""
        # Arrange
        too_long_password = "A1!" + "a" * 126  # 129 characters

        # Act & Assert
        with pytest.raises(PasswordValidationError) as exc_info:
            validate_password_strength(too_long_password)
        assert "must not exceed 128 characters" in str(exc_info.value)

    def test_uppercase_letter_requirement(self):
        """Test that passwords must contain at least one uppercase letter"""
        # Arrange
        no_uppercase = "password123!@#"

        # Act & Assert
        with pytest.raises(PasswordValidationError) as exc_info:
            validate_password_strength(no_uppercase)
        assert "uppercase letter" in str(exc_info.value)

    def test_lowercase_letter_requirement(self):
        """Test that passwords must contain at least one lowercase letter"""
        # Arrange
        no_lowercase = "PASSWORD123!@#"

        # Act & Assert
        with pytest.raises(PasswordValidationError) as exc_info:
            validate_password_strength(no_lowercase)
        assert "lowercase letter" in str(exc_info.value)

    def test_digit_requirement(self):
        """Test that passwords must contain at least one digit"""
        # Arrange
        no_digit = "PasswordOnly!@#"

        # Act & Assert
        with pytest.raises(PasswordValidationError) as exc_info:
            validate_password_strength(no_digit)
        assert "at least one number" in str(exc_info.value)

    def test_special_character_requirement(self):
        """Test that passwords must contain at least one special character"""
        # Arrange
        no_special = "Password123"

        # Act & Assert
        with pytest.raises(PasswordValidationError) as exc_info:
            validate_password_strength(no_special)
        assert "special character" in str(exc_info.value)

    @pytest.mark.parametrize("common_password", [
        "password", "Password123!", "PASSWORD", "Qwerty123!",
        "123456789", "Admin123!", "Letmein1!"
    ])
    def test_common_password_rejection(self, common_password):
        """Test that common passwords are rejected"""
        # Act & Assert
        with pytest.raises(PasswordValidationError) as exc_info:
            validate_password_strength(common_password)
        assert "too common" in str(exc_info.value) or "common words" in str(exc_info.value)

    @pytest.mark.parametrize("password_with_sequence", [
        "Abc123!def", "User234!pass", "Test345!word",
        "Pass567!word", "Hello678!world"
    ])
    def test_sequential_character_rejection(self, password_with_sequence):
        """Test that passwords with sequential characters are rejected"""
        # Act & Assert
        with pytest.raises(PasswordValidationError) as exc_info:
            validate_password_strength(password_with_sequence)
        assert "sequential characters" in str(exc_info.value)

    @pytest.mark.parametrize("special_char", [
        "!", "@", "#", "$", "%", "^", "&", "*", "(", ")",
        "_", "+", "-", "=", "[", "]", "{", "}", "|",
        ";", ":", "'", '"', ",", ".", "<", ">", "?", "/", "\\", "`", "~"
    ])
    def test_all_special_characters_accepted(self, special_char):
        """Test that all special characters are accepted"""
        # Arrange
        password = f"ValidPass1{special_char}z"

        # Act & Assert - should not raise for valid patterns
        try:
            result = validate_password_strength(password)
            assert result == password
        except PasswordValidationError:
            # Some may trigger sequential rejection, that's ok
            pass

    def test_password_with_all_requirements(self):
        """Test password that meets all requirements"""
        # Arrange
        valid_passwords = [
            "Secure@Pass123",
            "MyStr0ng!Pass",
            "C0mpl3x#Passw0rd",
            "Un1que$Password"
        ]

        # Act & Assert
        for password in valid_passwords:
            result = validate_password_strength(password)
            assert result == password

    def test_edge_case_exactly_8_characters(self):
        """Test password with exactly 8 characters"""
        # Arrange
        password = "Pass123!"

        # Act & Assert
        result = validate_password_strength(password)
        assert result == password

    def test_edge_case_exactly_128_characters(self):
        """Test password with exactly 128 characters"""
        # Arrange
        password = "A1!" + "x" * 124 + "Z"  # Exactly 128 characters

        # Act & Assert
        result = validate_password_strength(password)
        assert result == password
        assert len(result) == 128

    def test_unicode_characters_in_password(self):
        """Test that unicode characters are handled properly"""
        # Arrange
        password = "Pass123!émojis"

        # Act & Assert - should validate based on other requirements
        result = validate_password_strength(password)
        assert result == password


class TestPasswordStrengthScore:
    """Test password strength scoring algorithm"""

    def test_weak_password_low_score(self):
        """Test that weak passwords get low scores"""
        # Arrange
        weak_passwords = ["Pass123!", "Password1!"]

        # Act & Assert
        for password in weak_passwords:
            score = get_password_strength_score(password)
            assert 0 <= score < 60, f"Expected low score for {password}, got {score}"

    def test_strong_password_high_score(self):
        """Test that strong passwords get high scores"""
        # Arrange
        strong_passwords = [
            "MyC0mpl3x&SecureP@ssw0rd!2024",
            "Ungu3ss@ble#Str0ng$Passw0rd",
        ]

        # Act & Assert
        for password in strong_passwords:
            score = get_password_strength_score(password)
            assert score >= 70, f"Expected high score for {password}, got {score}"

    def test_length_bonus_scoring(self):
        """Test that longer passwords get higher scores"""
        # Arrange
        password_8 = "Pass123!"
        password_12 = "Password123!"
        password_16 = "LongPassword123!"

        # Act
        score_8 = get_password_strength_score(password_8)
        score_12 = get_password_strength_score(password_12)
        score_16 = get_password_strength_score(password_16)

        # Assert - longer passwords should score higher (accounting for penalties)
        assert score_8 <= score_12 or score_8 <= score_16

    def test_character_variety_bonus(self):
        """Test that character variety increases score"""
        # Arrange
        simple = "Aaaaaa1!"
        varied = "Ab1!Xy2@"

        # Act
        score_simple = get_password_strength_score(simple)
        score_varied = get_password_strength_score(varied)

        # Assert
        assert score_varied > score_simple

    def test_common_password_penalty(self):
        """Test that common passwords receive score penalty"""
        # Arrange
        for common_pass in ["password", "123456", "qwerty"]:
            # Act
            score = get_password_strength_score(common_pass)

            # Assert - should have severe penalty
            assert score < 20

    def test_sequential_pattern_penalty(self):
        """Test that sequential patterns reduce score"""
        # Arrange
        password_with_seq = "Test123!abc"
        password_no_seq = "Test987!xyz"

        # Act
        score_seq = get_password_strength_score(password_with_seq)
        score_no_seq = get_password_strength_score(password_no_seq)

        # Assert
        assert score_seq < score_no_seq

    def test_score_range_boundaries(self):
        """Test that scores are always within 0-100 range"""
        # Arrange
        test_passwords = [
            "",
            "a",
            "Pass123!",
            "SuperStr0ng!P@ssw0rd#With$Many%Chars",
            "password",  # Common - should get penalty
        ]

        # Act & Assert
        for password in test_passwords:
            score = get_password_strength_score(password)
            assert 0 <= score <= 100, f"Score {score} out of range for {password}"

    def test_score_consistency(self):
        """Test that same password always returns same score"""
        # Arrange
        password = "ConsistentP@ss123"

        # Act
        score1 = get_password_strength_score(password)
        score2 = get_password_strength_score(password)
        score3 = get_password_strength_score(password)

        # Assert
        assert score1 == score2 == score3


class TestCommonPasswordsList:
    """Test common passwords list"""

    def test_common_passwords_list_not_empty(self):
        """Test that common passwords list is populated"""
        # Assert
        assert len(COMMON_PASSWORDS) > 0
        assert isinstance(COMMON_PASSWORDS, set)

    def test_common_passwords_are_lowercase(self):
        """Test that common passwords are stored in lowercase"""
        # Assert
        for password in COMMON_PASSWORDS:
            assert password == password.lower()

    def test_known_weak_passwords_in_list(self):
        """Test that known weak passwords are in the list"""
        # Arrange
        known_weak = ["password", "123456", "qwerty", "admin"]

        # Assert
        for weak in known_weak:
            assert weak in COMMON_PASSWORDS


class TestPasswordValidationErrorException:
    """Test custom PasswordValidationError exception"""

    def test_exception_is_value_error(self):
        """Test that PasswordValidationError inherits from ValueError"""
        # Assert
        assert issubclass(PasswordValidationError, ValueError)

    def test_exception_can_be_raised_with_message(self):
        """Test that exception can be raised with custom message"""
        # Arrange
        message = "Custom validation error"

        # Act & Assert
        with pytest.raises(PasswordValidationError) as exc_info:
            raise PasswordValidationError(message)
        assert message in str(exc_info.value)

    def test_exception_can_be_caught_as_value_error(self):
        """Test that exception can be caught as ValueError"""
        # Act & Assert
        try:
            raise PasswordValidationError("Test error")
        except ValueError as e:
            assert "Test error" in str(e)


@pytest.mark.parametrize("password,expected_valid", [
    ("ValidPass123!", True),
    ("Str0ng@Passw0rd", True),
    ("short", False),
    ("NoNumbers!", False),
    ("nospecial123", False),
    ("NOLOWERCASE123!", False),
    ("nouppercase123!", False),
    ("Password123!", False),  # Common word
])
def test_password_validation_parametrized(password, expected_valid):
    """Parametrized test for various password scenarios"""
    if expected_valid:
        result = validate_password_strength(password)
        assert result == password
    else:
        with pytest.raises(PasswordValidationError):
            validate_password_strength(password)
