public class Test5_Blocks {
    public static void main(String[] args) {
        int x;
        x = 10;
        {
            int y;
            y = 20;
            System.out.println(y);
        }
        System.out.println(x);
    }
}
