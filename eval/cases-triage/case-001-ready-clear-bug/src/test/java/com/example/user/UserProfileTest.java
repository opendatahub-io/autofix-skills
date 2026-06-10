package com.example.user;

import org.junit.Test;
import static org.junit.Assert.*;

public class UserProfileTest {

    @Test
    public void testFormatPhoneNumberWithValidNumber() {
        UserProfile profile = new UserProfile("John Doe", "john@example.com", "5551234567");
        assertEquals("(555) 123-4567", profile.formatPhoneNumber());
    }

    @Test
    public void testFormatPhoneNumberWithEmptyString() {
        UserProfile profile = new UserProfile("Alice Brown", "alice@example.com", "");
        assertEquals("N/A", profile.formatPhoneNumber());
    }

    @Test
    public void testGetDisplayName() {
        UserProfile profile = new UserProfile("Test User", "test@example.com", "5551234567");
        assertEquals("Test User (test@example.com)", profile.getDisplayName());
    }
}
