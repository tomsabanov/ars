import math
import numpy as np

class Kalman():

    def __init__(self, theta, v, w, x, y):
        self.d = 1
        self.t = 1

        self.u = [[v], [w]]
        self.theta = theta
        self.A = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        self.B = [[self.d * self.t * math.cos(self.theta), 0], [self.d * self.t * math.sin(theta), 0], [0, self.d * self.t]]
        self.C = [[0.01, 0, 0], [0, 0.01, 0], [0, 0, 0.01]]

        sigma_x = 0.01
        sigma_y = 0.01
        sigma_theta = 0.01
        self.R_t = [[math.pow(sigma_x, 2), 0, 0], [0, math.pow(sigma_y, 2), 0], [0, 0, math.pow(sigma_theta, 0)]]
        sigma_q_x = 0.01
        sigma_q_y = 0.01
        sigma_q_theta = 0.01
        self.Q_t = [[math.pow(sigma_q_x, 2), 0, 0], [0, math.pow(sigma_q_y, 2), 0], [0, 0, math.pow(sigma_q_theta, 2)]]
        self.I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

        self.mu_t = [[x], [y], [theta]]
        self.sigma_t = self.R_t
        self.z = np.dot(self.C, self.mu_t) + self.d


    def kalman_filter(self, mu_t, sigma_t, u_t, z_t):
        # Prediction:
        mu_t_bar = np.dot(self.A, mu_t) + np.dot(self.B, u_t)
        sigma_t_bar = np.dot(np.dot(self.A, sigma_t), np.transpose(self.A)) + self.R_t

        # Correction:
        latter = np.dot(np.dot(self.C, sigma_t_bar), np.transpose(self.C)) + self.Q_t
        latter = np.linalg.inv(latter)
        K_t = np.dot(np.dot(sigma_t_bar, np.transpose(self.C)), latter)

        mu_t_new = mu_t_bar + np.dot(K_t, (z_t - np.dot(self.C, mu_t_bar)))
        sigma_t_new = np.dot((self.I - np.dot(K_t, self.C)), sigma_t_bar)

        self.mu_t = mu_t_new
        self.R_t = sigma_t_new  # Not sure about this one
        self.Q_t = sigma_t_new
        self.z = np.dot(self.C, self.mu_t) + self.d

        return (mu_t_new, sigma_t_new)



def kalman_test():

    x = 0
    y = 0
    theta = 0

    kalman = Kalman(theta, 1, 1, x, y)


    for i in range(5):
        step_results = kalman.kalman_filter(kalman.mu_t, kalman.sigma_t, kalman.u, kalman.z)
        kalman.mu_t = step_results[0]
        kalman.sigma_t = step_results[1]
        print("kalman results:")
        print("pos: ")
        print(kalman.mu_t)
        print("sigma: ")
        print(kalman.sigma_t)
        kalman.z = np.dot(kalman.C, kalman.mu_t) + kalman.d
        print("z:")
        print(kalman.z)
        kalman.t += 1


    # Theta is really increasing


if __name__ == '__main__':
    kalman_test()