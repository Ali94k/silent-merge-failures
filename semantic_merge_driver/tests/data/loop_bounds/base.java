public class BatchProcessor {
    public void processItems() {
        System.out.println("Starting batch...");

        // Iterate through the standard ID range
        for (int i = 0; 
             // Check against max limit
             i < 20; 
             i++) {
            
            System.out.println("Processing ID: " + i);
        }
    }
}