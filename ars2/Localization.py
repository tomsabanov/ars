import random

import numpy as np
import math
import pygame
from utils.vector import Point
import itertools


class Localization():
    def __init__(self, pos, theta, v, w, time_step, features, max_vision,
                sigma_err = 0.01, eps_t = 0.01, delta_t = 0.01, 
                qx=0.01, qy=0.01, qt = 0.01, rx=0.01, ry=0.01, rt=0.01):
        
        self.features = features
        self.max_vision = max_vision
        
        # constants
        self.t = 1
        self.A = np.identity(3)
        self.u = np.array([v, w])

        # ERROR OF INITIAL POSITION 
        self.sigma_err = sigma_err
        self.mu_t = np.array([pos.X, pos.Y, theta])
        self.sigma_t = np.identity(3) * sigma_err

        # Noise of sensor model
        self.Q = np.array([
            [qx**2,0,0],
            [0,qy**2,0],
            [0,0,qt**2]
        ])

        # Noise of motion model
        self.R_t = np.array([
            [rx**2,0,0],
            [0,ry**2,0],
            [0,0,rt**2]
        ])


        # Process noise, distributed with covariance R_t
        self.epsilon_t = eps_t        

        # Measurement noise, distributed with covariance Q_t
        mu, sigma = 1, (qx + qy + qt)/3 # mean and standard deviation
        self.delta = np.random.normal(mu, sigma, 1)[0]
        



        self.predicted_poses = list()
        self.predicted_sigmas = list()

        self.corrected_poses = list()
        self.corrected_sigmas = list()

        self.visible_features = list()

        self.covariance_hist = list()
    
    def update_speed(self, v,w):
        self.u = np.array([v, w])


    def get_predicted(self):
        return(self.predicted_poses, self.predicted_sigmas)
    def get_corrected(self):
        return(self.corrected_poses, self.corrected_sigmas)

    def get_visible_features(self):
        return self.visible_features

    def distance_between_points(self,p1,p2):
        dist = math.sqrt((p2.X - p1.X)**2 + (p2.Y - p1.Y)**2)
        return dist


    def find_features(self, pos):
        if pos == None:
            return

        for f in self.features:
            d = self.distance_between_points(f, pos)
            if(d<=self.max_vision):
                self.visible_features.append((f,d))

    def triangulate(self, points):
        (P1, r1) = points[0]
        (P2, r2) = points[1]
        (P3, r3) = points[2]

        P1 = np.array([P1.X, P1.Y])
        P2 = np.array([P2.X, P2.Y])
        P3 = np.array([P3.X, P3.Y])

        # First step
        e = P2 - P1
        ex = e / np.linalg.norm(e)

        # Second step
        i = np.dot(ex, P3-P1)

        # Third step
        e2 = P3 - P1 - i*ex
        ey = e2 / np.linalg.norm(e2)

        # Fourth step
        d = np.linalg.norm(P2-P1)

        # Fifth step
        j = np.dot(ey,(P3 - P1))

        # Sixth and seventh steps
        x = (r1**2 - r2**2 + d**2)/(2*d)
        y = (r1**2 - r3**2 + i**2 + j**2)/(2*j) - (i*x/j)

        # Final step
        p = P1 + x*ex + y*ey
        return (p[0],p[1])

    def triangulation(self):
        x = 0 
        y = 0
        i = 0
        for subset in itertools.combinations(self.visible_features, 3):
            i = i+1
            (xn, yn) = self.triangulate(subset)
            x = x + xn
            y = y + yn
        
        x = x/i
        y = y/i
        return (x,y)


    def unit_vector(self, vector):
        return vector / np.linalg.norm(vector)

    def angle_between(self,v1, v2):
        v1_u = self.unit_vector(v1)
        v2_u = self.unit_vector(v2)
        return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

    # Add noise
    def add_noise(self):

        s1 = random.randrange(10000) / 20000
        s2 = random.randrange(10000) / 20000
        s3 = random.randrange(10000) / 20000

        self.Q = np.array([[s1, 0, 0], [0, s2, 0], [0, 0, s3]])
        print("Q: " + str(self.Q))

        s1 = random.randrange(10000) / 20000
        s2 = random.randrange(10000) / 20000
        s3 = random.randrange(10000) / 20000

        self.R_t = np.array([[s1, 0, 0], [0, s2, 0], [0, 0, s3]])

        self.delta = random.randrange(10) / 9 + 0.5

    def get_robot_heading(self, p, theta):
        u = np.array([math.cos(theta),0]) # robot heading

        return u

    def estimate_bearing(self, p, theta): 
        bearing = 0
        p = np.array([p[0], p[1]])
        v = np.array([1,0]) # global vector
        v1 = self.get_robot_heading(p, theta)


        for g in self.visible_features:
            (f,r) = g
            # get vector between beacon and robot
            f = np.array([f.X,f.Y])
            v2 = f - p

            # Get global angle of beacon
            alpha = self.angle_between(v, v2)

            # Get angle between v2 and v1
            beta = self.angle_between(v1,v2)

            bearing = bearing + (beta-alpha)


        return bearing/len(self.visible_features)

        
    def update(self, real_pos, real_theta):
        real_theta = real_theta % math.pi

        # real_pos and real_theta used for calculating the features in range
        self.visible_features = list()

        self.add_noise()

        theta = self.mu_t[2]
        self.B = np.matrix([
                           [self.delta * self.t * math.cos(theta), 0], 
                           [self.delta * self.t * math.sin(theta), 0], 
                           [0, self.delta * self.t]
                           ])

        # Prediction
        mu_t_bar = np.add(self.mu_t, np.dot(self.B, self.u))
        sigma_t_bar = np.dot(np.dot(self.A, self.sigma_t), np.transpose(self.A)) + self.R_t


        # Find visible features
        self.find_features(real_pos)


        pred_theta = mu_t_bar.tolist()[0][2]
        #print("original angle: " + str(real_theta))
        #print("predicted angle: " + str(pred_theta))

        # If there are at least three features found - we do triangulation 
        # and correct our prediction, otherwise just use the prediction
        if len(self.visible_features) < 3:
            self.predicted_poses.append(mu_t_bar)
            self.predicted_sigmas.append(sigma_t_bar)
            
            mu_t_bar = mu_t_bar.tolist()
            mu_t_bar = mu_t_bar[0]

            self.mu_t = np.array([mu_t_bar[0], mu_t_bar[1], mu_t_bar[2]])
            self.sigma_t = sigma_t_bar
            self.covariance_hist.append(self.sigma_t)
            return



        # Do triangulation 
        z_t = self.triangulation()

        # Estimate bearing of the calculated z_t=[x,y] based on estimated theta 
        # and angle of beacons
        bearing = self.estimate_bearing(z_t, pred_theta)
        bearing = real_theta
        #print("Estimated bearing: " + str(bearing))
        #print("Original theta " + str(real_theta))
        #print("Predicted theta " + str(pred_theta))


        # Construct z_t with x,y and bearing values and apply noise
        z_t = self.epsilon * np.array([z_t[0],z_t[1], bearing])


        # Do correction
        K_t = np.matmul(sigma_t_bar, np.linalg.inv(np.add(sigma_t_bar, self.Q)))
        mu_t = np.add(mu_t_bar,  np.dot(K_t, np.add(z_t, -1*mu_t_bar).T).T)
        sigma_t = np.dot((np.identity(3) - K_t), sigma_t_bar)



        self.corrected_poses.append(mu_t)
        self.corrected_sigmas.append(sigma_t)

        # Update the values
        mu_t = mu_t.tolist()
        mu_t = mu_t[0]

        self.mu_t = np.array([mu_t[0], mu_t[1], mu_t[2]])
        self.sigma_t = sigma_t

        self.covariance_hist.append(self.sigma_t)

        #print("mu_t " + str(self.mu_t))

    def print(self):
        return
