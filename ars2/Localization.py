import numpy as np
import math
import pygame

class Localization():
    def __init__(self, pos, theta, v, w, time_step, features, max_vision):
        
        self.features = features
        self.max_vision = max_vision

        self.mu_t = np.array([pos.X, pos.Y, theta])
        self.sigma_t = np.identity(3) * 0.001

        mu, sigma = 1, 0.1 # mean and standard deviation
        self.delta = np.random.normal(mu, sigma, 1)[0]
        self.t = 1

        self.A = np.identity(3)
        self.u = np.array([v, w])


        self.R_t = np.identity(3) * 0.001


        self.predicted_poses = list()
        self.predicted_sigmas = list()

        self.visible_features = list()
    
    def update_speed(self, v,w):
        self.u = np.array([v, w])


    def get_predicted(self):
        return(self.predicted_poses, self.predicted_sigmas)

    def get_visible_features(self):
        return self.visible_features

    def distance_between_points(self,p1,p2):
        dist = math.sqrt((p2.X - p1.X)**2 + (p2.Y - p1.Y)**2)
        return dist


    def find_features(self, pos, theta):
        if pos == None:
            return

        for f in self.features:
            d = self.distance_between_points(f, pos)
            if(d<=self.max_vision):
                self.visible_features.append(f)

    def update(self, real_pos, real_theta):
        # real_pos and real_theta used for calculating the features in range
        self.visible_features = list()

        theta = self.mu_t[2]
        self.B = np.matrix([
                           [self.delta * self.t * math.cos(theta), 0], 
                           [self.delta * self.t * math.sin(theta), 0], 
                           [0, self.delta * self.t]
                           ])

        # Prediction
        mu_t_bar = self.A.dot(self.mu_t) + self.B.dot(self.u)
        sigma_t_bar = np.dot(np.dot(self.A, self.sigma_t), np.transpose(self.A)) + self.R_t

        self.predicted_poses.append(mu_t_bar)
        self.predicted_sigmas.append(sigma_t_bar)


        # Find visible features
        # TODO: SHOULD IT USE THE CORRECTED THETA OR THE REAL THETA HERE???
        self.find_features(real_pos, real_theta)

        # Correction



        # Update values for next update

        mu_t_bar = mu_t_bar.tolist()
        mu_t_bar = mu_t_bar[0]


        self.mu_t = np.array([mu_t_bar[0], mu_t_bar[1], mu_t_bar[2]])
        self.sigma_t = sigma_t_bar

    def print(self):
        return
