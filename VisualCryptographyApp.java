import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;
import java.util.Random;

import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;
//import javax.imageio.ImageIO;

public class VisualCryptographyApp {

    private static final int BLOCK_SIZE = 16;

    static class AESCipher {
        private final int blockSize = 16;
        private final String data;
        private final byte[] key;

        public AESCipher(String data, String key) {
            this.data = data;
            this.key = sha256(key).substring(0, 32).getBytes(StandardCharsets.UTF_8);
        }

        public String encrypt() {
            String plainText = pad(data);
            byte[] iv = new byte[blockSize];
            new Random().nextBytes(iv);
            IvParameterSpec ivSpec = new IvParameterSpec(iv);
            SecretKeySpec secretKey = new SecretKeySpec(key, "AES");

            try {
                Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
                cipher.init(Cipher.ENCRYPT_MODE, secretKey, ivSpec);
                byte[] encryptedBytes = cipher.doFinal(plainText.getBytes(StandardCharsets.UTF_8));
                byte[] combined = new byte[iv.length + encryptedBytes.length];
                System.arraycopy(iv, 0, combined, 0, iv.length);
                System.arraycopy(encryptedBytes, 0, combined, iv.length, encryptedBytes.length);
                return Base64.getEncoder().encodeToString(combined);
            } catch (Exception e) {
                e.printStackTrace();
                return null;
            }
        }

        public String decrypt() {
            try {
                byte[] encryptedBytes = Base64.getDecoder().decode(data);
                IvParameterSpec ivSpec = new IvParameterSpec(encryptedBytes, 0, blockSize);
                SecretKeySpec secretKey = new SecretKeySpec(key, "AES");
                Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
                cipher.init(Cipher.DECRYPT_MODE, secretKey, ivSpec);
                byte[] decryptedBytes = cipher.doFinal(encryptedBytes, blockSize, encryptedBytes.length - blockSize);
                return new String(decryptedBytes, StandardCharsets.UTF_8);
            } catch (Exception e) {
                e.printStackTrace();
                return null;
            }
        }

        private String pad(String s) {
            int padding = blockSize - (s.length() % blockSize);
            StringBuilder padded = new StringBuilder(s);
            for (int i = 0; i < padding; i++) {
                padded.append((char) padding);
            }
            return padded.toString();
        }

        private String sha256(String input) {
            try {
                MessageDigest digest = MessageDigest.getInstance("SHA-256");
                byte[] hash = digest.digest(input.getBytes(StandardCharsets.UTF_8));
                StringBuilder hexString = new StringBuilder();
                for (byte b : hash) {
                    String hex = Integer.toHexString(0xff & b);
                    if (hex.length() == 1) {
                        hexString.append('0');
                    }
                    hexString.append(hex);
                }
                return hexString.toString();
            } catch (NoSuchAlgorithmException e) {
                e.printStackTrace();
                return null;
            }
        }
    }

    public static void main(String[] args) {
        // Example usage
        String imagePath = "D:\\Users\\pobba\\Desktop\\cat.jpg";
        String key = "Cryptography";

        try {
            byte[] imageBytes = Files.readAllBytes(Paths.get(imagePath));
            String imageData = Base64.getEncoder().encodeToString(imageBytes);

            AESCipher aesCipher = new AESCipher(imageData, key);
            String encryptedData = aesCipher.encrypt();
            System.out.println("Encrypted Data: " + encryptedData);

            String decryptedData = aesCipher.decrypt();
            System.out.println("Decrypted Data: " + decryptedData);

            // If you want to convert decrypted data back to an image
            byte[] decryptedImageBytes = Base64.getDecoder().decode(decryptedData);
            BufferedImage decryptedImage = ImageIO.read(new ByteArrayInputStream(decryptedImageBytes));
            ImageIO.write(decryptedImage, "png", new File("path/to/decrypted/image.png"));

        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
