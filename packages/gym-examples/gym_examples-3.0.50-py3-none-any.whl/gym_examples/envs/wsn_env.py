import copy
import gym
import numpy as np
from gym.spaces import Discrete, Box, Tuple, Dict, MultiDiscrete
import matplotlib.pyplot as plt
import csv
from datetime import datetime
import torch
import torch.nn as nn
import torch.nn.functional as F

# Define the network parameters for the final reward function
input_dim = 4  # length of the individual rewards vector
output_dim = 1  # final reward

Eelec = 50e-9  # energy consumption per bit in joules
Eamp = 100e-12  # energy consumption per bit per square meter in joules
info_amount = 3072  # data size in bits
initial_energy = 1  # initial energy of each sensor (in joules)
lower_bound = 0  # lower bound of the sensor positions
upper_bound = 100  # upper bound of the sensor positions
base_station_position = np.array([(upper_bound - lower_bound)/2, (upper_bound - lower_bound)/2]) # position of the base station
initial_number_of_packets = 1  # initial number of packets to transmit
latency_per_hop = 1  # latency per hop in seconds


# Define the final reward function using an attention mechanism
class Attention(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(Attention, self).__init__()  # Call the initializer of the parent class (nn.Module)
        self.input_dim = input_dim  # Set the input dimension of the network
        self.output_dim = output_dim  # Set the output dimension of the network
        self.linear1 = nn.Linear(input_dim, 64)  # Define the first linear layer. It takes input of size 'input_dim' and outputs size '64'
        self.linear2 = nn.Linear(64, output_dim)  # Define the second linear layer. It takes input of size '64' and outputs size 'output_dim'

    def forward(self, x):
        x = F.relu(self.linear1(x))  # Pass the input through a linear layer and a ReLU activation function
        attention_weights = F.softmax(x, dim=0)  # Apply the softmax function to get the attention weights
        x = attention_weights * x  # Multiply the input by the attention weights
        x = self.linear2(x)  # Pass the result through another linear layer
        return x

class WSNRoutingEnv(gym.Env):
    def __init__(self, n_sensors = 20, coverage_radius=(upper_bound - lower_bound)/4):

        super(WSNRoutingEnv, self).__init__()

        self.n_sensors = n_sensors
        self.n_agents = n_sensors
        self.coverage_radius = coverage_radius
        self.episode_count = 0
        self.scale_displacement = 0.01 * (upper_bound - lower_bound) # scale of the random displacement of the sensors
        self.epsilon = 1e-10 # small value to avoid division by zero
        # Initialize the position of the sensors randomly

        # Define observation space
        self.observation_space = Tuple(
            tuple([self._get_observation_space() for _ in range(self.n_sensors)])
        )
        self.action_space = Tuple(tuple([Discrete(self.n_sensors + 1)] * self.n_agents))
                
        self.reset()
        

    def reset(self):
                
        self.sensor_positions = np.random.rand(self.n_sensors, 2) * (upper_bound - lower_bound) + lower_bound
        self.distance_to_base = np.linalg.norm(self.sensor_positions - base_station_position, axis=1)
        self.remaining_energy = np.ones(self.n_sensors) * initial_energy
        self.number_of_packets = np.ones(self.n_sensors, dtype=int) * initial_number_of_packets # number of packets to transmit
        self.episode_count += 1

        self.packets_delivered = 0
        self.total_energy_consumed = 0
        self.steps = 0
        self.first_node_dead_time = None
        self.total_latency = 0
        self.packet_latency = np.zeros(self.n_sensors)  # Latency for each packet
        self.total_packets_sent_by_sensors = 0

        self.network_throughput = None
        self.energy_efficiency = None
        self.packet_delivery_ratio = None
        self.network_lifetime = None
        self.average_latency = None

        return self._get_obs()

    def step(self, actions):
        self.steps += 1
        rewards = [0] * self.n_sensors
        dones = [False] * self.n_sensors
        for i, action in enumerate(actions):
            if action not in range(self.n_sensors + 1):
                raise ValueError("Invalid action!")
            
            if i >= self.n_sensors:
                continue  # Skip if the number of actions is greater than the number of sensors

            if self.remaining_energy[i] <= 0 or self.number_of_packets[i] <= 0:
                continue  # Skip if sensor has no energy left or no packets to transmit
            
            if (action == i):
                continue  # Skip if sensor tries to transmit data to itself

            if action == self.n_sensors:
                if self.distance_to_base[i] > self.coverage_radius:
                    continue  # Skip if the distance to the base station is greater than the coverage radius

                # Calculate the energy consumption for transmitting data to the base station
                transmission_energy = self.transmission_energy(self.number_of_packets[i], self.distance_to_base[i])
                if self.remaining_energy[i] < transmission_energy:
                    continue  # Skip if the sensor does not have enough energy to transmit data to the base station
                
                self.update_sensor_energies(i, transmission_energy)

                # Update the metrics
                self.total_energy_consumed += transmission_energy
                self.packets_delivered += self.number_of_packets[i]
                self.total_packets_sent_by_sensors += self.number_of_packets[i]
                self.total_latency += self.packet_latency[i] + latency_per_hop
                self.packet_latency[i] = 0

                # rewards[i] = self.compute_individual_rewards(i, action)
                rewards[i] = np.ones(input_dim)  # Reward for transmitting data to the base station
                dones[i] = True       
            else:
                distance = np.linalg.norm(self.sensor_positions[i] - self.sensor_positions[action])
                if distance > self.coverage_radius:
                    continue  # Skip if the distance to the next hop is greater than the coverage radius

                transmission_energy = self.transmission_energy(self.number_of_packets[i], distance)
                reception_energy = self.reception_energy(self.number_of_packets[i])
                if self.remaining_energy[i] < transmission_energy or self.remaining_energy[action] < reception_energy:
                    continue

                self.update_sensor_energies(i, transmission_energy)  
                self.update_sensor_energies(action, reception_energy) 

                # Update the metrics
                self.total_energy_consumed += transmission_energy + reception_energy
                self.total_packets_sent_by_sensors += self.number_of_packets[i]
                self.packet_latency[action] += self.packet_latency[i] + latency_per_hop
                self.packet_latency[i] = 0

                rewards[i] = self.compute_individual_rewards(i, action)                                

                # Update the number of packets
                self.number_of_packets[action] += self.number_of_packets[i]
            self.number_of_packets[i] = 0 # Reset the number of packets of the sensor i
            # Calculate final reward
            rewards[i] = self.compute_attention_rewards(rewards[i])
            # rewards[i] = self.compute_sum_rewards(rewards[i])
        for i in range(self.n_sensors):
            if (self.remaining_energy[i] <= 0) or (self.number_of_packets[i] <= 0):
                dones[i] = True

        # Integrate the mobility of the sensors
        # self.integrate_mobility() 

        self.distance_to_base = np.linalg.norm(self.sensor_positions - base_station_position, axis=1)

        if self.first_node_dead_time is None and np.any(self.remaining_energy <= 0):
            self.first_node_dead_time = self.steps

        self.get_metrics()

        return self._get_obs(), rewards, dones, {}

    def _get_obs(self):

        return [{'remaining_energy': np.array([e]), 
                 'consumption_energy': np.array([initial_energy - e]),
                 'sensor_positions': p,
                 'number_of_packets': np.array([d])
                } for e, p, d in zip(self.remaining_energy, self.sensor_positions, self.number_of_packets)]

    def _get_observation_space(self):
        return Dict({
            'remaining_energy': Box(low=0, high=initial_energy, shape=(1,), dtype=np.float64),
            'consumption_energy': Box(low=0, high=initial_energy, shape=(1,), dtype=np.float64),
            'sensor_positions': Box(low=lower_bound, high=upper_bound, shape=(2,), dtype=np.float64),
            'number_of_packets': Box(low=0, high=self.n_sensors * initial_number_of_packets + 1, shape=(1,), dtype=int)
        })

    def get_state(self):
        return self._get_obs()
    
    def get_avail_actions(self):
        return [list(range(self.n_sensors + 1)) for _ in range(self.n_sensors)]
    
    def update_sensor_energies(self, i, delta_energy):
        self.remaining_energy[i] -= delta_energy

    def transmission_energy(self, number_of_packets, distance):
        # energy consumption for transmitting data on a distance        
        return number_of_packets * info_amount * (Eelec + Eamp * distance**2)
    
    def reception_energy(self, number_of_packets):
        # energy consumption for receiving data
        return number_of_packets * info_amount * Eelec
    
    def compute_angle_vectors(self, i, action):
        '''
        Compute the angle in radians between the vectors formed by (i, action) and (i, base station)
        '''
        if action == self.n_sensors:
            return 0
        else:
            vector_to_next_hop = self.sensor_positions[action] - self.sensor_positions[i]
            vector_to_base = base_station_position - self.sensor_positions[i]
            cosine_angle = np.dot(vector_to_next_hop, vector_to_base) / (np.linalg.norm(vector_to_next_hop) * np.linalg.norm(vector_to_base))
            
            return np.arccos(np.clip(cosine_angle, -1, 1))

    def compute_reward_angle(self, i, action):
        '''
        Compute the reward based on the angle between the vectors formed by (i, action) and (i, base station)
        '''
        # Calculate the angle in radians between the vectors formed by (i, action) and (i, base station)
        angle = self.compute_angle_vectors(i, action)
        # Normalize the angle
        normalized_angle = abs(angle) / np.pi

        return np.clip(1 - normalized_angle, 0, 1)
    
    def compute_reward_distance(self, i, action):
        '''
        Compute the reward based on the distance to the next hop
        '''
        if action == self.n_sensors:
            distance = np.linalg.norm(self.sensor_positions[i] - self.distance_to_base[i])
        else:
            distance = np.linalg.norm(self.sensor_positions[i] - self.sensor_positions[action])
        # Normalize the distance to the next hop
        normalized_distance_to_next_hop = distance / self.coverage_radius

        return np.clip(1 - normalized_distance_to_next_hop, 0, 1)

    def compute_reward_consumption_energy(self, i, action):
        '''
        Compute the reward based on the total energy consumption (transmission, reception)
        '''
        # Calculate the total energy consumption (transmission, reception)
        if action == self.n_sensors:
            total_energy = self.transmission_energy(self.number_of_packets[i], self.distance_to_base[i])
        else:
            distance = np.linalg.norm(self.sensor_positions[i] - self.sensor_positions[action])
            transmission_energy = self.transmission_energy(self.number_of_packets[i], distance)
            reception_energy = self.reception_energy(self.number_of_packets[i])
            total_energy = transmission_energy + reception_energy
        
        # Normalize the total energy consumption
        max_transmission_energy = self.transmission_energy(self.n_sensors * initial_number_of_packets, self.coverage_radius)
        max_reception_energy = self.reception_energy(self.n_sensors * initial_number_of_packets)
        max_total_energy = max_transmission_energy + max_reception_energy
        normalized_total_energy = total_energy / (max_total_energy + self.epsilon)

        return np.clip(1 - normalized_total_energy, 0, 1)
    
    def compute_reward_dispersion_remaining_energy(self):
        '''
        Compute the reward based on the standard deviation of the remaining energy
        '''
        dispersion_remaining_energy = np.std(self.remaining_energy)
        # Normalize the standard deviation of the remaining energy
        max_dispersion_remaining_energy = initial_energy / 2 # maximum standard deviation of the remaining energy if n_sensors is even
        normalized_dispersion_remaining_energy = dispersion_remaining_energy / (max_dispersion_remaining_energy + self.epsilon)

        return np.clip(1 - normalized_dispersion_remaining_energy, 0, 1)
    
    def compute_reward_number_of_packets(self, action):
        '''
        Compute the reward based on the number of packets of the receiver
        '''
        max_number_of_packets = self.n_sensors * initial_number_of_packets
        if action == self.n_sensors:
            normalized_number_of_packets = 0
        else: 
            normalized_number_of_packets = self.number_of_packets[action] / (max_number_of_packets + self.epsilon)

        return np.clip(1 - normalized_number_of_packets, 0, 1)

    def compute_individual_rewards(self, i, action):
        '''
        Compute the individual rewards
        '''
        #-- rewards related to the energy consumption minimization and energy balance
        reward_angle = self.compute_reward_angle(i, action)
        # reward_distance = self.compute_reward_distance(i, action)
        reward_consumption_energy = self.compute_reward_consumption_energy(i, action)
        reward_dispersion_remaining_energy = self.compute_reward_dispersion_remaining_energy()
        reward_number_of_packets = self.compute_reward_number_of_packets(action)

        rewards_energy = np.array([reward_angle, reward_consumption_energy, reward_dispersion_remaining_energy, reward_number_of_packets])

        #-- rewards related to the performance metrics
        reward_latency = self.compute_reward_latency()
        reward_network_throughput = self.compute_reward_network_throughput()
        reward_packet_delivery_ratio = self.compute_reward_packet_delivery_ratio()

        rewards_performance = np.array([reward_latency, reward_network_throughput, reward_packet_delivery_ratio])

        # return np.concatenate((rewards_energy, rewards_performance))
        return rewards_energy
                
    def network_reward_dispersion_remaining_energy(self):
        '''
        Compute the reward based on the standard deviation of the remaining energy at the network level
        '''
        dispersion_remaining_energy = np.std(self.remaining_energy)
        # Normalize the standard deviation of the remaining energy
        max_dispersion_remaining_energy = initial_energy / 2 # maximum standard deviation of the remaining energy if n_sensors is even
        normalized_dispersion_remaining_energy = dispersion_remaining_energy / (max_dispersion_remaining_energy + self.epsilon)

        return np.clip(1 - normalized_dispersion_remaining_energy, 0, 1)
    
    def network_reward_consumption_energy(self):
        '''
        Compute the reward based on the total energy consumption (transmission, reception) at the network level
        '''
        total_energy = self.n_sensors * initial_energy - np.sum(self.remaining_energy)
        # Normalize the total energy consumption
        max_total_energy = self.n_sensors * initial_energy
        normalized_total_energy = total_energy / (max_total_energy + self.epsilon)

        return np.clip(1 - normalized_total_energy, 0, 1)
    
    def compute_reward_packet_delivery_ratio(self):
        '''
        Compute the reward based on the packet delivery ratio
        '''
        packet_delivery_ratio = self.packets_delivered / (self.total_packets_sent_by_sensors + self.epsilon) if self.total_packets_sent_by_sensors > 0 else 0
        return np.clip(packet_delivery_ratio, 0, 1)
    
    def compute_reward_latency(self):
        '''
        Compute the reward based on the average latency
        '''
        # Normalize the average latency
        max_latency = self.n_sensors * self.steps
        normalized_latency = self.total_latency / (max_latency + self.epsilon)

        return np.clip(1 - normalized_latency, 0, 1)

    def compute_reward_network_throughput(self):
        '''
        Compute the reward based on the network throughput
        '''
        network_throughput = self.packets_delivered / (self.steps + self.epsilon) if self.steps > 0 else 0
        maximum_throughput = self.n_sensors * initial_number_of_packets
        normalized_throughput = network_throughput / (maximum_throughput + self.epsilon)
        return np.clip(normalized_throughput, 0, 1)


    def compute_sum_rewards(self, rewards):
        '''
        Compute the sum of the rewards
        '''
        return np.sum(rewards)
    
    def compute_attention_rewards(self, rewards):
        '''
        Compute the attention-based rewards
        '''
        rewards = torch.tensor(rewards, dtype=torch.double)
        net = Attention(len(rewards), output_dim)
        net = net.double()  # Convert the weights to Double
        final_reward = net(rewards)
        return final_reward 

    def integrate_mobility(self):
        '''
        Integrate the mobility of the sensors after each step
        '''
        # Add a small random displacement to each sensor's position
        displacement = np.random.normal(scale=self.scale_displacement, size=(self.n_sensors, 2))
        self.sensor_positions += displacement
        # Cancel the displacement if the sensor goes out of bounds
        for i in range(self.n_sensors):
            if not(np.all(self.sensor_positions[i] >= lower_bound) and np.all(self.sensor_positions[i] <= upper_bound)):
                self.sensor_positions[i] -= displacement[i]
    
    def get_metrics(self):
        # Calculate network throughput
        self.network_throughput = self.packets_delivered / (self.steps + self.epsilon) if self.steps > 0 else 0
        # Calculate energy efficiency
        self.energy_efficiency = self.packets_delivered / (self.total_energy_consumed + self.epsilon) if self.total_energy_consumed > 0 else 0
        # Calculate packet delivery ratio
        self.packet_delivery_ratio = self.packets_delivered / (self.total_packets_sent_by_sensors + self.epsilon) if self.total_packets_sent_by_sensors > 0 else 0
        # Calculate network lifetime
        self.network_lifetime = self.first_node_dead_time if self.first_node_dead_time is not None else self.steps
        # Calculate average latency
        self.average_latency = self.total_latency / (self.packets_delivered + self.epsilon) if self.packets_delivered > 0 else 0

        return {
            "network_throughput": self.network_throughput,
            "energy_efficiency": self.energy_efficiency,
            "packet_delivery_ratio": self.packet_delivery_ratio,
            "network_lifetime": self.network_lifetime,
            "average_latency": self.average_latency
        }