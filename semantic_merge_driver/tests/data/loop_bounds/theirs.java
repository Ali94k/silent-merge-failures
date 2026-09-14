public class BatchProcessor {
    public void processItems() {
        System.out.println("Starting batch...");

        // Iterate through the standard ID range
        for (int i = 0; 
             // Check against max limit
             // CHANGED: Reduced batch size limit to 10
             i < 10; 
             i++) {
            
            System.out.println("Processing ID: " + i);
        }
    }
}