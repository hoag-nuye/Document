import java.util.Scanner;

public class ScanString {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        int number = scanner.nextInt(); 
        scanner.nextLine(); // Consume the newline character after the integer input
        String textLine1 = scanner.nextLine(); // Read the next line as a string
        String textLine2 = scanner.nextLine(); // Read the next line as a string


        System.out.print("Number: " + number + "\n");
        System.out.print("Text Line 1: " + textLine1 + "\n");
        System.out.print("Text Line 2: " + textLine2 + "\n");
        scanner.close();
    }
}