public class UserManager {
    
    // Method name is misleading - says "validate" but also transforms and saves
    public void validateUser(String name, String email) {
        if (name.length() < 2) {
            throw new IllegalArgumentException("Name too short");
        }
        
        String normalized = name.toUpperCase();
        System.out.println("Processed: " + normalized);
        saveToDatabase(normalized, email);
    }
    
    // Unclear boolean - what does "flag" mean?
    private boolean flag = false;
    
    private void saveToDatabase(String name, String email) {
        System.out.println("Saved");
    }
}
