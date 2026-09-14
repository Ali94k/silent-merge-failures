public class BatchProcessor {
    public void processItems() {
        System.out.println("Starting batch...");

        // Iterate through the standard ID range
        // CHANGED: We now skip the first 15 reserved IDs
        for (int i = 15; 
             // Check against max limit
             i < 20; 
             i++) {
            
            System.out.println("Processing ID: " + i);
        }
    }
}