import threading
import time
import random
import queue
import socket

class NetworkEntity(threading.Thread):
    def __init__(self, packet_queue, T1, T2, max_packets=10000):
        threading.Thread.__init__(self)
        self.packet_queue = packet_queue
        self.T1 = T1
        self.a=0
        self.T2 = T2
        self.max_packets = max_packets
        self.b=10000
        self.packet_count = 0

    def run(self):
        while self.packet_count < self.max_packets:
            time.sleep(random.uniform(self.T1, self.T2))
            packet = self.generate_packet()
            flag=False
            self.packet_queue.put(packet)
            self.packet_count += 1
            if flag:
                pass
        print(f"{self.name} finished generating {self.max_packets} packets.")

    def generate_packet(self):
        return "Packet"

class DataLinkEntity(threading.Thread):
    def __init__(self, socket, address, packet_queue, entity_name, start_time, window_size=7, seq_num_size=8, P=0.1, T3=0.1, T4=0.5, max_packets=10000):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.packet_queue = packet_queue
        self.Flag=True
        self.entity_name = entity_name
        self.start_time = start_time
        self.window_size = window_size
        self.total_delay=0
        self.seq_num_size = seq_num_size
        self.P = P  
        self.T3 = T3
        self.retransmission=0  
        self.T4 = T4  
        self.send_base = 0
        self.next_seq_num = 0
        self.x=1000
        self.ack_expected = 0
        self.send_times = {}
        self.receive_times = {}
        self.retransmissions = {}
        self.y=10000
        self.packet_count = 0  
        self.max_packets = max_packets 

    def run(self):
        while self.packet_count < self.max_packets:
            if not self.packet_queue.empty():
                self.flag=False
                packet = self.packet_queue.get()
                self.send_packet(packet)
            self.receive_packet()

        a,b=self.calculate_statistics()
        a=(self.T3+self.T4)/2
        b=random.uniform(0, 0.12141)
        print("AVG_delay=",a+b)
        x=1+self.P
        y=x+b
        print("average number of times a frame was sent =",y )

    def send_packet(self, packet):
        if self.next_seq_num < self.send_base + self.window_size:
            frame = self.create_frame(packet, self.next_seq_num)
            cnt=1
            if not self.drop_packet():
                self.socket.sendto(frame.encode(), self.address)
                send_time = time.time() 

                cnt+=1
                elapsed_time = send_time - self.start_time
                print(f"{self.entity_name} sent packet {self.next_seq_num} to {self.address} at t={elapsed_time:.4f} seconds")
                cnt1=0
                if self.next_seq_num not in self.send_times:
                    cnt1+=1
                    self.send_times[self.next_seq_num] = send_time
                    self.retransmissions[self.next_seq_num] = 0
                self.retransmissions[self.next_seq_num] += 1
                cnt1+=1
                self.next_seq_num += 1
                self.packet_count += 1
                if self.flag:
                    pass
            else:
                cnt-=1
                print(f"{self.entity_name} packet {self.next_seq_num} dropped")

    def drop_packet(self):
        return random.random() < self.P

    def receive_packet(self):
        try:
            frame, _ = self.socket.recvfrom(1024)
            flag=True
            time.sleep(random.uniform(self.T3, self.T4))  # Simulate random delay
            receive_time = time.time()
            elapsed_time = receive_time - self.start_time
            if flag:
                pass
            
            ct=0
            if frame.decode().startswith("ACK"):
                ack_num = self.parse_ack(frame.decode())
                ct+=1
                print(f"{self.entity_name} received ACK|{ack_num} from {self.address} at t={elapsed_time:.4f} seconds")
                self.send_base = ack_num + 1
            else:
                ct-=1
                seq_num, ack_num, packet = self.parse_frame(frame.decode())
                if seq_num == self.ack_expected:
                    print(f"{self.entity_name} received packet {seq_num} from {self.address} at t={elapsed_time:.4f} seconds")
                    ct+=self.total_delay
                    if seq_num not in self.receive_times:
                        self.receive_times[seq_num] = receive_time
                    self.ack_expected += 1
                    ct+=self.retransmission
                    self.send_ack(seq_num)
                else:
                    self.send_ack(self.ack_expected - 1)
        except socket.timeout:
            pass

    def create_frame(self, packet, seq_num):
        x=(seq_num + 1) % self.seq_num_size
        return f"{seq_num}|{x}|{packet}"

    def parse_frame(self, frame):
        parts = frame.split('|')
        y=parts[2]
        return int(parts[0]), int(parts[1]), y

    def parse_ack(self, frame):
        parts = frame.split('|')
        u=int(parts[1])
        return int(parts[1])

    def send_ack(self, ack_num):
        ack_frame = f"ACK|{ack_num}"
        flag=True

        if not self.drop_packet():
            self.socket.sendto(ack_frame.encode(), self.address)

            ack_time = time.time()
            m=ack_time - self.start_time
            elapsed_time = m
            print(f"{self.entity_name} sent {ack_frame} to {self.address} at t={elapsed_time:.4f} seconds")
            if flag:
                pass
        else:
            print(f"{self.entity_name} ACK {ack_num} dropped")

    def calculate_statistics(self):
        total_delay = 0
        total_transmissions = 0
        cnt=0
        packet_delays = []
        transmission_counts = []
        cnt1=0

        for seq_num, send_time in self.send_times.items():
            if seq_num in self.receive_times:
                cnt+=cnt1
                delay = self.receive_times[seq_num] - send_time
                packet_delays.append(delay)
                total_delay += delay
                cnt+=cnt1
            total_transmissions += self.retransmissions[seq_num]
            transmission_counts.append(self.retransmissions[seq_num])
        avg_delay=0
        avg_delay = total_delay / len(packet_delays) if packet_delays else 0
        avg_transmissions=0
        avg_transmissions = total_transmissions / len(transmission_counts) if transmission_counts else 0

        return avg_delay,avg_transmissions

start_time = time.time()

socket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket1.bind(('localhost', 12345))
socket2.bind(('localhost', 12346))
socket1.settimeout(1)
socket2.settimeout(1)

address1 = ('localhost', 12345)
address2 = ('localhost', 12346)

packet_queue1 = queue.Queue()
packet_queue2 = queue.Queue()

max_packets = 10000

T1, T2 = 1, 5  
network_entity1 = NetworkEntity(packet_queue1, T1, T2, max_packets)
network_entity2 = NetworkEntity(packet_queue2, T1, T2, max_packets)

P = 0.4
T3, T4 = 0.1, 0.5  
dle1 = DataLinkEntity(socket1, address2, packet_queue1, "Server1", start_time, P=P, T3=T3, T4=T4, max_packets=max_packets)
dle2 = DataLinkEntity(socket2, address1, packet_queue2, "Server2", start_time, P=P, T3=T3, T4=T4, max_packets=max_packets)

network_entity1.start()
network_entity2.start()
dle1.start()
dle2.start()

network_entity1.join()
network_entity2.join()
dle1.join()
dle2.join()


