public class UserValidator {
    
    // Method name says "validate" but it actually does validation AND transforms AND logging
    public String checkUser(String username, String password) {
        // Validation step
        if (username.length() < 3) {
            System.err.println("Username too short");
            return null;
        }
        
        if (password.length() < 8) {
            System.err.println("Password too weak");
            return null;
        }
        
        // Also does transformation (what?!)
        String transformed = username.toUpperCase() + "_" + System.currentTimeMillis();
        
        // And logging
        System.out.println("User " + transformed + " was validated at " + new java.util.Date());
        
        return transformed;
    }
    
    // Confusing boolean variable - is it "waiting"? "done"? "ready"?
    private boolean flag = false;
    
    public void processUserCreation(String user) {
        if (!flag) {
            System.out.println("Creating user: " + user);
            flag = true;
        }
    }
}
