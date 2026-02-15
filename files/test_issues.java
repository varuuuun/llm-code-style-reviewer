public class DataProcessor {
    
    // This method name doesn't reflect what it actually does
    public void processData(String input) {
        System.out.println(input);
        sortArray(new int[]{3, 1, 2});
        validateEmail(input);
        saveToDatabase(input);
        sendNotification(input);
    }
    
    // This boolean name is confusing - should it be "isProcessing" or "isProcessed"?
    private boolean done = false;
    
    private void sortArray(int[] arr) {
        for (int i = 0; i < arr.length; i++) {
            for (int j = i + 1; j < arr.length; j++) {
                if (arr[i] > arr[j]) {
                    int temp = arr[i];
                    arr[i] = arr[j];
                    arr[j] = temp;
                }
            }
        }
    }
    
    private void validateEmail(String email) {
        if (!email.contains("@")) {
            throw new IllegalArgumentException("Invalid email");
        }
    }
    
    private void saveToDatabase(String data) {
        // Simulate database save
        System.out.println("Saved: " + data);
    }
    
    private void sendNotification(String message) {
        // Simulate notification
        System.out.println("Notified: " + message);
    }
}
