public class OrderProcessor {
    
    // Method name is misleading - it does way more than just "update"
    public void updateOrder(String orderId, double price, String status, String customerEmail) {
        // Validates the order
        if (orderId == null || orderId.isEmpty()) {
            throw new IllegalArgumentException("Order ID required");
        }
        
        // Updates database
        System.out.println("Updating order " + orderId + " to price " + price);
        
        // Sends emails
        sendOrderConfirmationEmail(customerEmail, orderId, price);
        
        // Generates invoice
        generateInvoice(orderId, price);
        
        // Updates inventory
        updateInventory(orderId);
        
        // Logs to audit trail
        logAuditTrail("Order updated: " + orderId + " status: " + status);
    }
    
    // Poor boolean naming - what does "ok" mean exactly?
    private boolean ok = true;
    
    // What about this one - "next"?
    private boolean next = false;
    
    private void sendOrderConfirmationEmail(String email, String orderId, double price) {
        System.out.println("Email sent to " + email);
    }
    
    private void generateInvoice(String orderId, double price) {
        System.out.println("Invoice generated for " + orderId);
    }
    
    private void updateInventory(String orderId) {
        System.out.println("Inventory updated");
    }
    
    private void logAuditTrail(String message) {
        System.out.println("[AUDIT] " + message);
    }
}
