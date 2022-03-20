import numpy as np
import math
import pygame

class Localization():
    def __init__(self, pos, theta, v, w, time_step):

        self.mu_t = np.array([pos.X, pos.Y, theta])
        self.sigma_t = np.identity(3) * 0.001

        mu, sigma = 1, 0.1 # mean and standard deviation
        self.delta = np.random.normal(mu, sigma, 1)[0]
        self.t = 1

        self.A = np.identity(3)
        self.u = np.array([v, w])

        print(time_step)

        self.R_t = np.identity(3) * 0.001


        self.predicted_poses = list()
        self.predicted_sigmas = list()
    
    def update_speed(self, v,w):
        self.u = np.array([v, w])


    def get_predicted(self):
        return(self.predicted_poses, self.predicted_sigmas)

    def update(self):
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


        mu_t_bar = mu_t_bar.tolist()
        mu_t_bar = mu_t_bar[0]
        self.mu_t = np.array([mu_t_bar[0], mu_t_bar[1], mu_t_bar[2]])




    def print(self):
        return
