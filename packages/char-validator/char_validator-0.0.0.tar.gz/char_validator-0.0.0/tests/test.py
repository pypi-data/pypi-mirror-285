import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import filters

# Load the image
image_path = "019_crop_3.png.jpg"
image = plt.imread(image_path)
if image.ndim == 3:
    gray = np.dot(image[...,:3], [0.2989, 0.5870, 0.1140])
else:
    gray = image

# Step 1: Compute the gradient of the image
Ix = filters.sobel(gray, axis=0)
Iy = filters.sobel(gray, axis=1)

# Step 2: Compute the products of derivatives
Ix2 = Ix**2
Iy2 = Iy**2
IxIy = Ix * Iy

# Step 3: Compute the Harris corner response matrix
k = 0.04
window_size = 3
offset = window_size // 2

height, width = gray.shape
corner_response = np.zeros((height, width))

for y in range(offset, height-offset):
    for x in range(offset, width-offset):
        Sx2 = np.sum(Ix2[y-offset:y+offset+1, x-offset:x+offset+1])
        Sy2 = np.sum(Iy2[y-offset:y+offset+1, x-offset:x+offset+1])
        Sxy = np.sum(IxIy[y-offset:y+offset+1, x-offset:x+offset+1])
        
        # Compute the determinant and trace of the matrix
        det = (Sx2 * Sy2) - (Sxy**2)
        trace = Sx2 + Sy2
        R = det - k * (trace**2)
        
        corner_response[y, x] = R

# Step 4: Threshold the response
threshold = 0.01 * corner_response.max()
corners = np.zeros_like(corner_response)
corners[corner_response > threshold] = 1

# Create a copy of corners for the new result
filtered_corners = np.copy(corners)

# Step 5: Filter corners based on the 3x3 kernel condition
for y in range(offset, height-offset):
    for x in range(offset, width-offset):
        if corners[y, x] == 1:
            # Get the 3x3 kernel
            kernel = corners[y-offset:y+offset+1, x-offset:x+offset+1]
            # Count the number of white pixels in the kernel
            white_pixels = np.sum(kernel)
            # Keep only points with one or three white pixels
            if white_pixels == 2:
                filtered_corners[y, x] = 0

# Plot the results
fig, ax = plt.subplots()
ax.imshow(image, cmap='gray')
ax.plot(np.where(filtered_corners)[1], np.where(filtered_corners)[0], 'r.', markersize=5)
plt.title('Filtered Corners')
plt.axis('off')
plt.show()
