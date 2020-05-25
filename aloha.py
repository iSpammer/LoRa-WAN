from random import random
from random import randrange
from batch_lora import send_lora


class NodeOccupiedException(Exception):
    pass


class Node:
    def __init__(self, id_, x, y, gateway_q_gen):
        self.id = id_
        self.state = False
        self.latency = 0
        self.result = False
        self.gateway_q_gen = gateway_q_gen
        self.x = x
        self.y = y

    def gen_msg(self):
        if not self.state:
            tmp = random()
            if tmp <= self.gateway_q_gen:
                # print("node", tmp, "meaw ", self.id)
                self.state = True


class Gateway:

    def __init__(self, size, p_send_max, q_gen_max):

        self.idle_proc = True
        self.rx_proc = False
        self.netw_map = [[0 for x in range(size)] for y in range(size)]
        self.netw_map[int(size / 2) - 1][int(size / 2) - 1] = -1
        self.p_send = p_send_max
        self.q_gen = q_gen_max
        # print(self.netw_map)

    def add_to_map(self, x, y, id_):
        if self.netw_map[x][y] == 0:
            self.netw_map[x][y] = id_
        else:
            raise NodeOccupiedException()

    def draw_map(self):
        print("started")
        for i in range(len(self.netw_map)):
            print(self.netw_map[i], " ")
        print("ended")


class Aloha:
    def __init__(self, map_size, num_nodes, epochs, q_gen, p_send):
        self.n = num_nodes
        self.gateway = Gateway(map_size, p_send, q_gen)
        self.nodes = []
        self.node_latencies = {i: [] for i in range(num_nodes)}
        self.init_netw()
        self.epochs = epochs
        self.result = []

    def init_netw(self):
        for i in range(self.n):
            self.nodes.append(Node(id_=i, x=randrange(10), y=randrange(10), gateway_q_gen=self.gateway.q_gen))
            self.gateway.add_to_map(self.nodes[i].x, self.nodes[i].y, self.nodes[i].id)
            print("Node of id:", self.nodes[i].id, ", x loc:", self.nodes[i].y, ", y loc:", self.nodes[i].id)
        self.gateway.draw_map()

    def create_msg(self):
        for i in range(self.n):
            self.nodes[i].gen_msg()

    def tx(self):

        actives = [self.nodes[i] for i in range(self.n) if self.nodes[i].state]
        # print("active")
        # print([active.state for active in actives])
        senders = [actv for actv in actives if random() <= self.gateway.p_send]
        # print("senders")
        # If more than one try to send we have a collision that results
        # in transmission failure
        # print([sender.gateway_q_gen for sender in senders])
        # print("3adad senders", len(senders))
        if len(senders) > 1:
            self.result.append(False)
            # so any active node experiences latency
            for active in actives:
                active.latency += 1
            for sender in senders:
                send_lora()

        else:
            if not senders:
                self.result.append(True)
                for active in actives:
                    active.latency += 1
            else:
                senders[0].state = False

                send_lora()
                self.node_latencies[senders[0].id].append(senders[0].latency)  # the sender is not latent now
                senders[0].latency = 0
                # all other active nodes experience latency again
                actives.remove(senders[0])
                for active in actives:
                    active.latency += 1
                self.result.append(True)

    def simulate(self):
        for i in range(self.epochs):
            self.create_msg()
            self.tx()

    def avg_latency_per_node(self):
        avg = 0

        for node in self.nodes:
            y = [value for value in self.node_latencies[node.id] if value]

            if y:
                avg += sum(y) / len(y)

        return avg / self.n


if __name__ == '__main__':
    print('Exhibition:')
    x = Aloha(map_size=10, num_nodes=10, epochs=4, q_gen=0.8, p_send=0.1, )
    x.simulate()
    print('Result: ' + str(x.result))
    print('Node latencies: ' + str(x.node_latencies))
    print('Average node latency: ' + str(x.avg_latency_per_node()))
