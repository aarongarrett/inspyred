import sys
import socket
import pickle
import threading
import collections
import SocketServer

class NetworkMigrator(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """Defines a migration function across a network.
    
    This callable class acts as a migration function that 
    allows candidate solutions to migrate from one population
    to another via TCP/IP connections.
    
    The migrator is constructed by specifying the IP address
    of the server (hosting the population from which individuals
    emigrate) as an IP-port tuple and the addresses of the clients 
    (hosting the populations to which individuals from the server 
    immigrate) as a list of IP-port tuples. The ``max_migrants`` 
    parameter specifies the size of the queue of migrants waiting 
    to immigrate to the server from the clients; the newest migrants 
    replace older ones in the queue.
    
    Note: In order to use this migration operator, individuals
    must be pickle-able.
        
    The following is an example of the use of this operator::
    
        m = NetworkMigrator(('192.168.1.10', 25125),
                            [('192.168.1.11', 12345), ('192.168.1.12', 54321)], 
                            max_migrants=3)
                        
    Since the NetworkMigrator object is a server, it should always
    call the ``shutdown()`` method when it is no longer needed, in
    order to give back its resources.

    Public Attributes:
    
    - *client_addresses* -- the list of IP address tuples
      (IP, port) to which individuals should migrate
    - *migrants* -- the deque of migrants (of maximum size 
      specified by ``max_migrants``) waiting to immigrate 
      to client populations
    
    """
    def __init__(self, server_address, client_addresses, max_migrants=1):
        self._lock = threading.Lock()
        SocketServer.TCPServer.__init__(self, server_address, None)
        self.client_addresses = client_addresses
        self.migrants = collections.deque(maxlen=max_migrants)
        t = threading.Thread(target=self.serve_forever)
        t.setDaemon(True)
        t.start()
        self.__name__ = self.__class__.__name__

    def finish_request(self, request, client_address):
        try:
            rbufsize = -1
            wbufsize = 0
            rfile = request.makefile('rb', rbufsize)
            wfile = request.makefile('wb', wbufsize)

            pickle_data = rfile.readline().strip()
            migrant = pickle.loads(pickle_data)
            with self._lock:
                self.migrants.append(migrant)
            
            if not wfile.closed:
                wfile.flush()
            wfile.close()
            rfile.close()        
        finally:
            sys.exc_traceback = None

    def __call__(self, random, population, args):
        """Perform the migration.
        
        This function serves as the migration operator. Here, a random address
        is chosen from the ``client_addresses`` list, and a random individual
        is chosen from the population to become the migrant. A socket is opened
        to the chosen client address, and the chosen migrant is pickled and
        sent to the NetworkMigrator object running at the client address. Then
        the migrant queue on the current machine is queried for a migrant
        to replace the one sent. If one is found, it replaces the newly
        migrated individual; otherwise, the individual remains in the population.
        
        Any immigrants may also be re-evaluated before insertion into the
        current population by setting the ``evaluate_migrant`` keyword
        argument in ``args`` to True. This is useful if the evaluation
        functions in different populations are different and we want to compare
        "apples to apples," as they say.

        Arguments:
        
        - *random* -- the random number generator object
        - *population* -- the population of Individuals
        - *args* -- a dictionary of keyword arguments
        
        Optional keyword arguments in the ``args`` parameter:
        
        - *evaluate_migrant* -- whether to re-evaluate the immigrant (default False)
        
        """
        evaluate_migrant = args.setdefault('evaluate_migrant', False)
        client_address = random.choice(self.client_addresses)
        migrant_index = random.randint(0, len(population) - 1)
        pickle_data = pickle.dumps(population[migrant_index])
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(client_address)
            sock.send(pickle_data + '\n')
        finally:
            sock.close()
        migrant = None
        with self._lock:
            if len(self.migrants) > 0:
                migrant = self.migrants.popleft()
        if migrant is not None:
            if evaluate_migrant:
                fit = args._ec.evaluator([migrant], args)
                migrant.fitness = fit[0]
                args._ec.num_evaluations += 1
            population[migrant_index] = migrant
        return population
		
    def __str__(self):
        return str(self.migrants)
