class Tracker():
    def __init__(self,window_width, window_height, margin=25, ym=1, xm=1, smooth_factor=15):
        # all past (left,right) center set values used for smoothing the output
        self.recent_centers = []  
        # window pixel height of center values, used to count pixels inside center windows to determine curve values
        self.window_width = window_width 
        # window pixel height of center values, used to count pixels inside center windows to determine curve values
        # breaks the image into vertical levels
        self.window_height = window_height     
        # the pixel distance in bothdirections to slide (left_window+right_window) templates for searching
        self.margin = margin  
        #number of pixels per meter
        self.ym_per_pix = ym  
        #number of pixels per meter
        self.xm_per_pix = xm 
        #distance in meters of vehicle center from the line
        self.smooth_factor = smooth_factor 
    
    def find_window_centroids(self, warped):
        """ Find and store lane segment positions
        
        args: warped:
        return: average_line_centers:averaged value of of the line centers,
        helps to keep the markers from jumping around too much
        """
        window_width = self.window_width
        window_height = self.window_height
        margin = self.margin
        
        window_centroids = [] # store the (left,right) window centroids positions per level
        window = np.ones(window_width) # Create window templates for doing convolutions
        
        # First find the two starting positions right and left lines by using np.sum to get the vertical image slice
        # and then np.convolve the vertical image slice with the window  template
        
        # sum the bottom quarter of image to get slice
        l_sum = np.sum(warped[int(3*warped.shape[0]/4):,:int(3*warped.shape[1]/2)], axis=0)
        l_center = np.argmax(np.convolve(window,l_sum)) - window_width/2
        r_sum = np.sum(warped[int(3*warped.shape[0]/4):int(3*warped.shape[1]/2),:], axis=0)
        r_center = np.argmax(np.convolve(window,r_sum)) - window_width/2 + int(warped.shape[1]/2)
        
        # add what we found for the first layer
        window_centroids.append((l_center,r_center))
        
        # Go through each layer looking for max pixel location
        for level in range(1,(int)(warped.shape[0]/window_height)):
            # convolve the window into the vertical slice of the image
            image_layer = np.sum(warped[int(warped.shape[0]-(level+1)*window_height):int(warped.shape[0]-level*window_height),:], axis=0)
            conv_signal = np.convolve(window,image_layer)
            # Find the best left centroid by using past left center as a reference 
            # Use window_width/2 as offset because convolution signal reference is at right side of window, not center of window
            offset = window_width/2
            l_min_index = int(max(l_center+offset-margin,0))
            l_max_index = int(max(l_center+offset+margin,warped.shape[1]))
            l_center = np.argmax(conv_signal[l_min_index:l_max_index]) + l_min_index - offset
            
            # Find the best right centroid by using past right center as a reference
            r_min_index = int(max(r_center+offset-margin,0))
            r_max_index = int(max(r_center+offset+margin,warped.shape[1]))
            r_center = np.argmax(conv_signal[r_min_index:r_max_index]) + r_min_index - offset
            # Add what we found for the layer
            window_centroids.append((l_center,r_center))
        
        self.recent_centers.append(window_centroids)
        # return averaged value of of the line centers, helps to keep the markers from jumping around too much
        average_line_centers = np.average(self.recent_centers[-self.smooth_factor:], axis=0)
        return average_line_centers
    