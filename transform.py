import cv2
import numpy as np

def add_salt_pepper_noise(image, amount=0.05):
    """Добавить шум 'соль и перец'"""
    noisy = image.copy()
    num_salt = np.ceil(amount * image.size * 0.5)
    num_pepper = np.ceil(amount * image.size * 0.5)
    
    coords = [np.random.randint(0, i - 1, int(num_salt))
              for i in image.shape[:2]]
    noisy[coords[0], coords[1], :] = 255
    
    coords = [np.random.randint(0, i - 1, int(num_pepper))
              for i in image.shape[:2]]
    noisy[coords[0], coords[1], :] = 0
    
    return noisy

def add_gaussian_noise(image, mean=0, sigma=150):
    gauss = np.random.normal(mean, sigma, image.shape)
    noisy = image.astype(np.float32) + gauss
    return np.clip(noisy, 0, 255).astype(np.uint8)

def reduce_contrast(image, factor=0.5):
    mean = np.mean(image)
    return np.clip((image - mean) * factor + mean, 0, 255).astype(np.uint8)

original = cv2.imread('./images/image.jpg')
original = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)

noisy_sp = add_salt_pepper_noise(original, 0.05)
noisy_gauss = add_gaussian_noise(original, 0, 25)
low_contrast = reduce_contrast(original, 0.3)

cv2.imwrite('./images/test_salt_pepper.jpg', cv2.cvtColor(noisy_sp, cv2.COLOR_RGB2BGR))
cv2.imwrite('./images/test_gaussian.jpg', cv2.cvtColor(noisy_gauss, cv2.COLOR_RGB2BGR))
cv2.imwrite('./images/test_low_contrast.jpg', cv2.cvtColor(low_contrast, cv2.COLOR_RGB2BGR))