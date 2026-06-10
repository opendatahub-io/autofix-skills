package com.example.user;

public class UserProfile {
    private String name;
    private String email;
    private String phoneNumber;

    public UserProfile(String name, String email, String phoneNumber) {
        this.name = name;
        this.email = email;
        this.phoneNumber = phoneNumber;
    }

    public String getName() {
        return name;
    }

    public String getEmail() {
        return email;
    }

    public String getPhoneNumber() {
        return phoneNumber;
    }

    public String formatPhoneNumber() {
        if (phoneNumber.isEmpty()) {
            return "N/A";
        }

        String cleaned = phoneNumber.replaceAll("[^0-9]", "");
        if (cleaned.length() == 10) {
            return String.format("(%s) %s-%s",
                cleaned.substring(0, 3),
                cleaned.substring(3, 6),
                cleaned.substring(6, 10));
        }

        return phoneNumber;
    }

    public String getDisplayName() {
        return name + " (" + email + ")";
    }

    public String getContactInfo() {
        return "Phone: " + formatPhoneNumber();
    }
}
